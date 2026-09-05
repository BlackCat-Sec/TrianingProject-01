# Module 12: LLM / Chat — Model Integration Specification

| Attribute | Value |
| :--- | :--- |
| **Module Identifier** | `MOD-12-LLM-CHAT` |
| **Title** | LLM / Chat Model Integration Adapter |
| **Document Version** | 1.0.0 |
| **Status** | Approved / Engineering Specification |
| **Target Runtime** | `llama.cpp` Server (GGUF Quantized Native Engine) |
| **API Interface** | Standardized `generate(messages, settings)` Contract |

---

## 1. Executive Summary & Purpose

The primary objective of **Module 12: Model Integration** is to provide a unified, decoupled, and stable programmatic interface—specifically `generate(messages, settings)`—between the host application and the local Large Language Model (LLM) runtime.

### 1.1 Separation of Concerns
A critical architectural boundary must be maintained:
* **The adapter knows how to call the model runtime.** It handles socket communication, serialization, schema conversion, template verification, generation limits, timeouts, and low-level runtime error mappings.
* **The adapter does NOT know how to query databases.** It must remain entirely agnostic to Vector Databases, Retrieval-Augmented Generation (RAG) pipelines, SQL/NoSQL stores, document parsing, semantic search logic, or application-level user session persistence.

```
+-------------------------------------------------------------------------+
|                           Application Layer                             |
|          (RAG Pipelines, Vector Search, Agent Orchestration)            |
+-------------------------------------------------------------------------+
                                     |
                                     | calls generate(messages, settings)
                                     v
+-------------------------------------------------------------------------+
|                  Module 12: Model Integration Adapter                   |
|  - Validates Chat Templates & Parameter Bounds                          |
|  - Enforces Request Timeouts & Concurrency Caps                         |
|  - Maps /health Readiness vs. Process Liveness                          |
|  - Serializes to Qualified OpenAI-compatible Payload                    |
+-------------------------------------------------------------------------+
                                     |
                                     | HTTP REST (/v1/chat/completions, /health)
                                     v
+-------------------------------------------------------------------------+
|                       llama.cpp Server Runtime                          |
|  - Model: Quantized GGUF Artifact (Q4_K_M / Q5_K_M)                     |
|  - Native C++ SIMD Execution (AVX2 / AVX-512 / ARM NEON)                |
|  - Internal KV Cache Management & Slot Scheduler                        |
+-------------------------------------------------------------------------+
```

---

## 2. Runtime Evaluation & Architecture Selection

Deploying local models requires choosing between native binary inference engines (`llama.cpp`) and direct Python runtime bindings (Hugging Face `transformers`).

### 2.1 Comparative Analysis

| Evaluation Vector | `llama.cpp` Server Daemon (Chosen Baseline) | Hugging Face `transformers` Direct Loading |
| :--- | :--- | :--- |
| **Format Execution** | Native quantized execution directly on GGUF weights (Q4_K_M, Q5_K_M, etc.). | Automatically dequantizes GGUF formats to full FP32/FP16 tensors in host memory upon load. |
| **RAM / VRAM Overhead** | **Strictly bounded**: Disk size ≈ RAM size + fixed KV cache allocation. | **Severe memory amplification**: A ~4.5 GB GGUF model expands to 16 GB–32 GB+ in memory. |
| **Process Isolation** | Independent C++ binary process. Python crashes or memory fragmentation do not impact model weights. | Monolithic execution within the Python interpreter memory space. Prone to GIL contention and memory leaks. |
| **CPU SIMD Acceleration** | Highly optimized C++ kernels (AVX2, AVX-512, ARM NEON, Metal) with near-zero runtime overhead. | Python-to-PyTorch binding overhead, unoptimized for pure CPU quantized inference pipelines. |
| **API Surface** | Built-in HTTP server providing qualified OpenAI-compatible `/v1/chat/completions` and `/health`. | Requires manual implementation of API endpoints, request queuing, and health probes. |

### 2.2 The Dequantization Pitfall
When running local models on resource-constrained or CPU-baseline infrastructure, teams often mistakenly load `.gguf` files via `AutoModelForCausalLM.from_pretrained(...)`. While Hugging Face `transformers` has added GGUF parsing support, **it dequantizes the weights into 32-bit floating point by default**. Consequently, the low disk footprint of a quantized artifact provides no memory savings. 

**Architectural Decision:** The proposed baseline mandates running the quantized GGUF artifact strictly within the native `llama.cpp` server runtime daemon.

---

## 3. Server Configuration & Process Lifecycle

The `llama.cpp` HTTP server (`llama-server`) exposes an OpenAI-compatible `/v1/chat/completions` endpoint alongside dedicated diagnostic endpoints.

### 3.1 Startup Configuration
The daemon should be launched with explicit generation constraints, slot bounds, and resource controls:

```bash
./llama-server \
  --model ./models/meta-llama-3-8b-instruct.Q4_K_M.gguf \
  --alias primary-model \
  --ctx-size 4096 \
  --n-predict 1024 \
  --parallel 1 \
  --threads 8 \
  --host 127.0.0.1 \
  --port 8080 \
  --timeout 60 \
  --log-disable
```

#### Parameter Breakdown:
* `--model`: Absolute path to the validated quantized GGUF artifact.
* `--alias primary-model`: Assigns a fixed, vendor-neutral identifier for adapter validation.
* `--ctx-size 4096`: Fixed total context window (prompt tokens + completion tokens).
* `--n-predict 1024`: Hard upper bound on token generation length per invocation.
* `--parallel 1`: Limits execution to a single generation slot for predictable latency and zero CPU thrashing.
* `--timeout 60`: Runtime socket timeout in seconds.

### 3.2 Readiness vs. Process Start Separation
In cloud or containerized environments (Kubernetes, Systemd), a process start does **not** signify that the model is ready to serve inference. Large model weights take several seconds or minutes to be mapped into memory and cache structures.

* **Liveness Probe (`GET /slots`):** Verifies that the HTTP daemon process is running and sockets are accepting connections.
* **Readiness Probe (`GET /health`):**
  * `HTTP 503 Service Unavailable`: Process active, model loading or slot initializing (`{"status": "loading model"}`). Traffic must be withheld.
  * `HTTP 200 OK`: Model weights loaded, KV caches pre-allocated, slot ready for generation (`{"status": "ok"}`).

### 3.3 Qualified API Compatibility
While `llama.cpp` supports the `/v1/chat/completions` route, compatibility is **qualified rather than universal**:
* Streaming semantics, tool-calling JSON schemas, and logit bias behavior may differ slightly from OpenAI cloud specifications.
* The adapter must validate payload schemas explicitly and avoid relying on proprietary OpenAI extensions.

---

## 4. Chat Templates & Prompt Alignment

Local instruction-tuned models depend heavily on exact delimiter formats. For example:
* **Llama 3:** `<|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|>`
* **ChatML (Qwen/Yi):** `<|im_start|>user
{prompt}<|im_end|>`
* **Mistral:** `[INST] {prompt} [/INST]`

### Template Enforcement Rules
1. **Never construct raw prompt delimiters manually in business logic.**
2. Rely on the server's embedded chat template parser (which parses the Jinja template embedded directly in the GGUF metadata).
3. Always verify that the prompt buffer logged by `llama-server` matches the model's official instruction specification. Mismatched templates cause severe degradation in instruction following, erratic termination, or repetitive token loops.

---

## 5. Adapter Specification & Interface Design

The Python adapter standardizes interaction, guarantees timeout compliance, wraps response schemas, and maps network errors into strongly-typed domain exceptions.

### 5.1 Python Implementation

```python
"""Module 12: LLM Chat Integration Adapter.
Provides a stable generate(messages, settings) interface backed by llama.cpp.
"""

import time
import json
import logging
from dataclasses import dataclass, field
from typing import List, Literal, Optional, Dict, Any
import requests

logger = logging.getLogger("Module12.ModelIntegration")


# ---------------------------------------------------------------------------
# Domain Exceptions
# ---------------------------------------------------------------------------
class LLMIntegrationError(Exception):
    """Base exception for all model integration errors."""
    pass

class ModelNotReadyError(LLMIntegrationError):
    """Raised when the model server is still loading weights or unavailable."""
    pass

class GenerationTimeoutError(LLMIntegrationError):
    """Raised when inference exceeds the specified timeout threshold."""
    pass

class InvalidResponseError(LLMIntegrationError):
    """Raised when the server returns a malformed or non-compliant response."""
    pass

class ModelArtifactMismatchError(LLMIntegrationError):
    """Raised when the runtime is serving an unexpected model alias or artifact."""
    pass


# ---------------------------------------------------------------------------
# Data Transfer Objects (DTOs)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant"]
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class GenerationSettings:
    max_tokens: int = 512
    temperature: float = 0.0          # Greedy decoding baseline
    top_p: float = 1.0
    timeout_seconds: float = 30.0
    stop_sequences: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class GenerationUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class GenerationResponse:
    content: str
    finish_reason: Literal["stop", "length", "timeout", "error"]
    usage: GenerationUsage
    model_alias: str


# ---------------------------------------------------------------------------
# Model Adapter Class
# ---------------------------------------------------------------------------
class LlamaCppChatAdapter:
    """Adapter executing chat generation against a running llama.cpp server."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080",
        expected_model_alias: str = "primary-model",
        default_settings: Optional[GenerationSettings] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.expected_model_alias = expected_model_alias
        self.default_settings = default_settings or GenerationSettings()

    def check_readiness(self) -> bool:
        """Validates that the model daemon has finished loading weights.
        
        Returns:
            bool: True if server responds 200 OK with 'ok' status.
            
        Raises:
            ModelNotReadyError: If server responds 503 or cannot be reached.
        """
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    return True
            raise ModelNotReadyError(
                f"Model server not ready: HTTP {resp.status_code} - {resp.text}"
            )
        except requests.RequestException as exc:
            raise ModelNotReadyError(f"Health probe unreachable: {exc}") from exc

    def generate(
        self,
        messages: List[ChatMessage],
        settings: Optional[GenerationSettings] = None
    ) -> GenerationResponse:
        """Dispatches chat payload to the inference daemon.

        Args:
            messages: Chronological conversation message history.
            settings: Optional parameter overrides for generation.

        Returns:
            GenerationResponse: Standardized response object.
        """
        if not messages:
            raise ValueError("Parameter 'messages' cannot be empty.")

        cfg = settings or self.default_settings
        self.check_readiness()

        payload = {
            "model": self.expected_model_alias,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": cfg.max_tokens,
            "temperature": cfg.temperature,
            "top_p": cfg.top_p,
            "stop": cfg.stop_sequences if cfg.stop_sequences else None,
            "stream": False
        }

        start_time = time.perf_counter()
        try:
            resp = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=cfg.timeout_seconds
            )
        except requests.Timeout as exc:
            elapsed = time.perf_counter() - start_time
            logger.error(f"Inference timed out after {elapsed:.2f}s (cap: {cfg.timeout_seconds}s)")
            raise GenerationTimeoutError(
                f"Inference request exceeded timeout of {cfg.timeout_seconds}s"
            ) from exc
        except requests.RequestException as exc:
            raise LLMIntegrationError(f"Socket transport failure: {exc}") from exc

        if resp.status_code != 200:
            raise InvalidResponseError(
                f"Daemon returned error HTTP {resp.status_code}: {resp.text}"
            )

        try:
            body = resp.json()
            returned_model = body.get("model", "")
            if returned_model and self.expected_model_alias not in returned_model:
                raise ModelArtifactMismatchError(
                    f"Model alias mismatch: expected '{self.expected_model_alias}', got '{returned_model}'"
                )

            choice = body["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "stop")
            
            usage_data = body.get("usage", {})
            usage = GenerationUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )

            return GenerationResponse(
                content=content,
                finish_reason=finish_reason,
                usage=usage,
                model_alias=returned_model or self.expected_model_alias
            )
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise InvalidResponseError(f"Malformed response structure: {resp.text}") from exc
```

---

## 6. Concurrency & Generation Constraints

### 6.1 Single Generation Slot (`--parallel 1`)
On CPU-bounded deployments:
1. **Thread Thrashing:** Multiple concurrent requests running multi-threaded matrix operations compete directly for L2/L3 cache and CPU cores, causing aggregate throughput collapse.
2. **Latency Predictability:** Setting `--parallel 1` processes requests serially or buffers them uniformly, ensuring consistent latency for real-time interaction.

### 6.2 Determinism & Low Temperature Caveats
Developers frequently assume that setting `temperature: 0.0` guarantees bitwise reproducible outputs and ensures factual accuracy:
* **No Guarantee of Factual Correctness:** Greedy decoding (`temperature: 0.0`) simply picks the token with highest conditional probability `argmax P(w_t | w_{<t})`. It prevents sampling variance, but will confidently output hallucinations if the model's parametric weights favor an inaccurate continuation.
* **Cross-Hardware Non-Determinism:** Floating-point operations (GEMM / GEMV) are not associative under different SIMD instruction sets (AVX2 vs. AVX-512 vs. Apple Silicon AMX). The cumulative rounding differences at layer 32 alter logit rankings at boundary tokens, leading to divergent paths across architectures.

---

## 7. Acceptance Criteria & Validation Matrix

All deployments of Module 12 must pass the following validation matrix before integration into upper-level orchestration layers:

| Test ID | Scenario | Test Input / Action | Expected Result | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **VAL-01** | Baseline Output | Prompt: `"Reply with 'PONG'"` | Content is `"PONG"`, `HTTP 200 OK`. | Output strictly matches expected text, HTTP status is 200. |
| **VAL-02** | Readiness Guard | Invoke `generate()` while `/health` returns 503 | `ModelNotReadyError` raised immediately. | Adapter does not block or time out; fails fast. |
| **VAL-03** | Token Length Cap | Request 500-word essay with `max_tokens: 16` | Generated token count ≤ 16, `finish_reason: "length"`. | Response is clipped; usage reflects limit. |
| **VAL-04** | Timeout Enforcement | Trigger computation with `timeout_seconds: 0.001` | Adapter aborts; raises `GenerationTimeoutError`. | Client releases thread cleanly without indefinite hanging. |
| **VAL-05** | Template Verification | Inspect server prompt buffer logs | Message tokens wrapped with native role markers. | No delimiter leaks; proper `<|im_start|>` or `<|eot_id|>`. |
| **VAL-06** | Malformed Payload | Mock server returning `{ "corrupt": true }` | Adapter raises `InvalidResponseError`. | Handled gracefully without uncaught unhandled exceptions. |
| **VAL-07** | Model Alias Match | Serve `other-model` when adapter expects `primary-model` | Raises `ModelArtifactMismatchError`. | Prevents execution against incorrect model checkpoints. |

---

## 8. Summary of Operating Rules

1. **Keep it decoupled:** Do not add database clients, vector store connections, or retrieval logic into this adapter.
2. **Use `llama.cpp` for GGUF:** Do not load GGUF models directly via PyTorch/Transformers on CPU baselines.
3. **Respect `/health`:** Always verify readiness before dispatching inference jobs.
4. **Cap token lengths and timeouts:** Never make unbounded inference requests without explicit timeouts.
