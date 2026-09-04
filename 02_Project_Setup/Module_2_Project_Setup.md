# Module 02: Project Setup

**Project: Simple RAG System**  
**Team Leader**  
**Prepared by:** Mokshith H S  
**USN:** 4BB23AIO20  
**Department:** Artificial intelligence and Machine Learning

## Problem statement and objective

The team needs an application that answers questions about a chosen set of documents. A general language model does not automatically know private project files, and it can produce plausible answers without supporting evidence. The system should retrieve relevant passages from approved documents, give those passages to the language model and return an answer that the user can trace to its sources.

Retrieval-augmented generation combines model knowledge with external retrieved information. The original RAG research studied trained retriever-generator systems. This project uses the same broad retrieval-and-generation idea but proposes frozen pretrained models for the first version. Indexing documents changes the searchable knowledge store; it does not update the language model's weights. [Lewis et al., RAG paper](https://arxiv.org/abs/2005.11401).

**What “specific things” means here:** the project's domain is defined by its approved corpus, scope instructions and evaluation questions. For example, a training-manual assistant may answer from the manuals and decline questions that those manuals do not support. It cannot guarantee correct answers to every possible question, even if the topic sounds related.

### Scope and requirements

Working assumptions are an English corpus, text PDF/DOCX/TXT/Markdown inputs, approximately 100–1,000 documents for the pilot, and local use by a small team. Those numbers are planning bounds, not product limits. Image-only pages require a separately tested OCR stage; tables and diagrams need special review. A browser interface is sufficient for users on all three operating systems.

| ID | Requirement | Evidence required at acceptance |
| - | - | - |
| FR1 | Index approved documents and preserve locations | Source-to-chunk traceability sample |
| FR2 | Retrieve evidence for domain questions | Labeled retrieval test results |
| FR3 | Generate answers with source references | Supported-answer review |
| FR4 | Abstain when evidence is insufficient | Unsupported-question test results |
| FR5 | Update and remove indexed content | Re-index and deletion demonstrations |
| FR6 | Return stable structured API responses | Schema and failure-path checks |
| NFR1 | Run on Windows, macOS and Linux targets | Recorded native-architecture smoke tests |
| NFR2 | Persist models and database state | Restart and restore demonstrations |
| NFR3 | Reproduce a release | Dependency, model and image lock records |
| NFR4 | Restrict access and protect source content | Retrieval and source-access checks |
| NFR5 | Measure resource use and response times | Hardware-specific benchmark sheet |


Out of scope for the first version: training an LLM from scratch, automatic web crawling, autonomous tools, arbitrary code execution, high availability, production multitenancy and guaranteed correctness. Fine-tuning is a later option if a measured behavior problem remains after retrieval, prompts and model selection have been evaluated.

### Proposed stack and why it fits

| Component | Baseline choice | Design reason |
| - | - | - |
| Backend and contracts | Python 3.11, FastAPI, Pydantic | One language for ingestion and API logic |
| Embeddings | all-MiniLM-L6-v2 | Small English embedding baseline |
| Vector storage | Qdrant service | Vector search with source metadata filters |
| Generator | Qwen2.5-1.5B-Instruct, GGUF Q4\_K\_M | Small instruction model for CPU evaluation |
| Model runtime | llama.cpp HTTP server | Quantized inference behind a service boundary |
| Interface | Simple browser page served by the API | No OS-specific client installation |
| Packaging | Docker Compose and multi-platform images | Reproducible service topology |
| Tests | pytest plus a labeled question set | Contracts, retrieval and groundedness checks |


The exact Python package versions must be resolved and locked on both architectures; Python 3.11 is a project starting choice, not a statement about the newest Python release. FastAPI can validate and filter responses against declared models, which supports the stable contract required by Modules 14 and 15. [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/).

MiniLM produces 384-dimensional vectors and truncates inputs beyond 256 WordPieces by default. Start with about 200 embedder tokens per passage and 30 tokens of overlap, then verify the final embedding input, including headings and special tokens, fits the model limit. These chunk settings are proposed tuning values. [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).

Qwen2.5-1.5B-Instruct has 1.54 billion parameters and an Apache-2.0 license. Its model-specific context limit is 32,768 tokens; the card's generic series description also mentions 128K, which should not be used as this model's limit. The official Q4\_K\_M GGUF file is approximately 1.12 GB. File size does not equal full application RAM use. [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct); [official quantized file](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/blob/main/qwen2.5-1.5b-instruct-q4_k_m.gguf).

Use a 4,096-token runtime context and at most 512 output tokens initially. Budget system messages, question, source labels and evidence within that total. Choose 16 GB host RAM as a preferred evaluation machine; an 8 GB machine is a constrained test target rather than a verified minimum. Start with at least 15 GB of free disk for images, models and a small corpus. These are engineering allowances; measure the actual stack before promising support.

A larger candidate is Qwen2.5-7B-Instruct Q4\_K\_M. Its official quantization totals approximately 4.68 GB across two shards; both are needed. Evaluate its quality and resource cost on the same test set. Do not assume every Qwen size has the same license: the 3B variant uses a research license. [7B model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct); [7B files](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/tree/main); [3B license](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE).

If the corpus includes Kannada, Hindi or other languages, replace the English embedding baseline only after language-specific retrieval tests. One candidate, multilingual-e5-small, requires different query and passage prefixes. Re-embed all documents when changing the embedding model, even when both models produce vectors of the same dimension. [Multilingual E5 model card](https://huggingface.co/intfloat/multilingual-e5-small).

### System operation

```
flowchart TD        
  D\\\\\\\\\\\\\\\["Approved documents"\\\\\\\\\\\\\\\] --\\\\\\\\\\\\\\\> I\\\\\\\\\\\\\\\["Load, clean and chunk"\\\\\\\\\\\\\\\]        
  I --\\\\\\\\\\\\\\\> E\\\\\\\\\\\\\\\["Embed and store"\\\\\\\\\\\\\\\]        
  E --\\\\\\\\\\\\\\\> V\\\\\\\\\\\\\\\[("Versioned vector database")\\\\\\\\\\\\\\\]        
  Q\\\\\\\\\\\\\\\["Validated question"\\\\\\\\\\\\\\\] --\\\\\\\\\\\\\\\> P\\\\\\\\\\\\\\\["Module 13: retrieve evidence"\\\\\\\\\\\\\\\]        
  V --\\\\\\\\\\\\\\\> P        
  P --\\\\\\\\\\\\\\\> G\\\\\\\\\\\\\\\{"Enough evidence?"\\\\\\\\\\\\\\\}        
  G --\\\\\\\\\\\\\\\>|Yes| L\\\\\\\\\\\\\\\["Generate and validate references"\\\\\\\\\\\\\\\]        
  G --\\\\\\\\\\\\\\\>|No| A\\\\\\\\\\\\\\\["Insufficient evidence"\\\\\\\\\\\\\\\]        
  L --\\\\\\\\\\\\\\\> O\\\\\\\\\\\\\\\["Module 15: answer and sources"\\\\\\\\\\\\\\\]        
  A --\\\\\\\\\\\\\\\> O
```

Proposed system boundaries. Indexing prepares knowledge ahead of time. Module 13 coordinates the online query path and sends the final result to Module 15.

**Indexing path:** approved files pass through loading, cleaning, structural processing and chunking. The embedding component converts each passage into a vector. Storage writes vectors together with the passage text, location and version metadata. A validated corpus release becomes available for queries.

**Question path:** the API validates the question and derives its permitted document scope. The same embedding configuration encodes the query. Retrieval selects candidate passages from the active corpus. The pipeline applies an evidence gate, assembles the prompt, calls the generator and validates the answer's references. Output is either a supported answer, an insufficient-evidence response or an operational error.

The three long-running services are the API, Qdrant and llama.cpp. A short-lived preparation job downloads pinned model artifacts. The API contains the embedding component initially; a separate embedding service can be introduced later if scaling needs justify it. The 15 modules are ownership and code boundaries, not 15 required containers.

## Setup specification

**Module responsibility:** define the common foundation so that every member builds against the same configuration, schema and release procedure. The deliverable is more than folder creation: it is a reproducible development and deployment contract.

### Inputs, outputs and ownership boundaries

Inputs are the project brief, module list, target hardware, selected models, approved source policy and team repository. Outputs are the repository structure, local setup instructions, dependency lock, environment template, container build specification, shared schemas and release manifest.

Module 1 owns project scaffolding, common configuration and build conventions. Module 8 owns database collection behavior; Module 12 owns model serving; Module 13 owns orchestration; Module 15 owns the response contract. Review these interfaces together before each member implements independently.

### Setup procedure

1. Record the domain and corpus owner. Write ten representative questions, including at least two that should not be answered from the corpus. Confirm whether the project must work after disconnecting from the internet.

2. Inventory the team's operating systems, CPU architectures, RAM, free disk and GPUs. Select one reference machine and identify the weakest machine that must pass the demo.

3. Create the shared repository and assign a working branch per task. Protect the main branch through review and checks. Keep one authoritative setup guide rather than separate conflicting copies.

4. Create the application package, shared schemas, documentation folders and test fixtures. Add a README to each module folder so its contract is visible before code exists.

5. Resolve Python dependencies in a clean environment. Build for amd64 and arm64 and check binary-wheel availability. Commit the resolved lock and interpreter choice; do not describe an untested list of latest packages as reproducible.

6. Define configuration validation, model artifact preparation, persistent volumes and service readiness. Build a minimal API health endpoint before joining all modules.

### Repository and folder conventions

Use the existing numbered team folders. Folder 01 is reserved for team member names, so the folder number is one greater than the original module number: Module 1 uses 02\_Project\_Setup, Module 13 uses 14\_RAG\_Pipeline\_Integration, and Module 15 uses 16\_Output. Keep importable Python code in one package with lowercase names and underscores. The application paths below describe the proposed implementation layout; they do not imply that those files already exist.

| Path or pattern | Contents |
| - | - |
| README.md | Project goal, quickstart, demo and limitations |
| 02\_Project\_Setup/Module\_1\_Project\_Setup.md | Module 1 specification |
| 14\_RAG\_Pipeline\_Integration/Module\_13\_RAG\_Pipeline\_Integration.md | Module 13 specification |
| 16\_Output/Module\_15\_Output.md | Module 15 specification |
| existing numbered module folder/README.md | Each other module's contract |
| app/main.py and app/config.py | API lifecycle and validated configuration |
| app/contracts.py | Shared typed input/output models |
| app/ingestion/ | Modules 2–6 and indexing coordination |
| app/embeddings.py and app/storage.py | Modules 7–9 |
| app/retrieval.py and app/prompts.py | Modules 10–11 |
| app/llm.py and app/pipeline.py | Modules 12–13 |
| app/query.py and app/output.py | Modules 14–15 |
| app/prepare\_models.py and app/ingest.py | Model provisioning and ingestion commands |
| app/static/ | Browser interface with local static assets |
| tests/ and eval/ | Fixtures, tests and labeled question set |
| Dockerfile and compose.yaml | Build and service definitions |
| requirements.lock and model-lock.json | Resolved packages and model revisions |
| .env.example and .dockerignore | Configuration guide and build exclusions |


Keep raw confidential documents, model weights, tokens, local caches, database files and generated logs out of Git. Exclude them from the Docker build context too. Store a small approved synthetic fixture in the repository for tests. A Git repository shares code and permitted documentation; it does not automatically synchronize each member's database volume.

Recommended direct dependencies are FastAPI, Uvicorn, Pydantic, pydantic-settings, sentence-transformers, torch, qdrant-client, httpx, huggingface-hub, pypdf and python-docx. Add pytest for development. Add OCR dependencies only when that scope is approved. Resolve these together; record transitive versions and platform differences in the lock process.

### Configuration and reproducibility

| Setting | Proposed starting value or rule |
| - | - |
| EMBEDDING\_MODEL\_ID | sentence-transformers/all-MiniLM-L6-v2 |
| EMBEDDING\_DIMENSION | 384 |
| EMBEDDING\_PATH | /models/embedding |
| LLM\_REPO | Qwen/Qwen2.5-1.5B-Instruct-GGUF |
| LLM\_FILE | qwen2.5-1.5b-instruct-q4\_k\_m.gguf |
| LLM\_BASE\_URL | http://llm:8080/v1 |
| LLM\_MODEL\_ALIAS | domain-rag |
| QDRANT\_URL | http://qdrant:6333 |
| COLLECTION\_ALIAS | domain\_active |
| CHUNK\_TARGET / OVERLAP | 200 / 30 embedder tokens |
| RETRIEVAL\_K / CONTEXT\_K | 8 candidates / up to 4 evidence chunks |
| CONTEXT\_WINDOW / MAX\_NEW\_TOKENS | 4096 / 512 generator tokens |
| GENERATION\_CONCURRENCY | 1 initially |
| REQUEST\_DEADLINE\_SECONDS | 120 initially; tune after measurement |
| SCORE\_THRESHOLD | Calibrate using labeled positive and negative queries |


Do not use a universal cosine threshold such as 0.7 without validation. Similarity is a ranking signal, not a calibrated probability that an answer is correct. A threshold can be chosen to trade off missed answers and unsupported responses on a held-out validation split.

Maintain a release manifest containing the application commit, schema version, Python lock hash, image manifest digests, actual model repository commits, GGUF checksum, embedding model identity and revision, prompt version, chunker version, corpus manifest and collection name. Record the context and generation parameters too. Hugging Face supports downloading a particular revision; pin a full commit rather than relying on a moving branch. [Hugging Face download guide](https://huggingface.co/docs/huggingface_hub/en/guides/download).

The model preparation job must verify the selected file and embedding assets, write a manifest and exit nonzero on mismatch. Download into a temporary location and publish the completed artifact only after verification. Runtime containers then load local artifacts. Do not download a new model inside every question request.

### Common contracts

All records use schema\_version, stable identifiers and explicit provenance. Times use UTC ISO 8601. PDF page numbers are one-based file page positions; preserve printed page labels separately when available. DOCX passages use section and paragraph locations because pagination may change across viewers.

| Record | Required fields |
| - | - |
| SourceDocument | doc\_id, content\_hash, title, source\_uri, version, language, access\_scope |
| DocumentElement | element\_id, doc\_id, text, element\_type, location, extraction\_method |
| Chunk | chunk\_id, doc\_id, text, location, chunk\_index, chunker\_version, token\_count |
| EmbeddedChunk | Chunk fields, vector, embedding\_model, embedding\_revision |
| RetrievedChunk | Chunk fields, score, score\_type, corpus\_version, permitted source metadata |
| QueryRequest | question, optional domain filter, optional session\_id |
| AnswerResponse | request\_id, status, answer, citations, warnings, corpus\_version |


Keep vectors out of ordinary answer responses. Derive source-access scope in the backend from the authenticated identity or a configured local profile; never trust a caller-supplied access\_scope. Use one stable namespace when deriving UUIDs for Qdrant point identifiers.

### Module 1 acceptance and handover

Module 1 is complete when a clean checkout builds, its configuration rejects missing required values, the dependency lock is reproducible on selected targets, no credentials or private corpus files are in the image, and the release manifest identifies all changing inputs. The handover package is the setup README, environment template, container files, shared schemas, model preparation specification and a fresh-checkout verification record.

Suggested explanation to the team: “I define how every module runs and communicates. The same model revisions, schemas and configuration are used by each teammate, and Docker packages the runtime dependencies for the supported machine architectures.”

## Docker deployment and operation

### What cross-platform deployment means

Build Linux container images and run them through a supported container environment. Docker does not turn a Linux image into a native Windows or macOS executable. It also does not guarantee that one CPU architecture or GPU backend works on every computer. Multi-platform images contain architecture-specific variants, and Docker selects a compatible variant. [Docker multi-platform builds](https://docs.docker.com/build/building/multi-platform/).

| Host | Common CPU deployment | Acceleration option |
| - | - | - |
| Windows, Intel/AMD | Docker Desktop, WSL 2, linux/amd64 | Supported NVIDIA GPU through WSL 2 setup |
| macOS, Apple silicon | Docker Desktop, linux/arm64 | Native Metal runner as a separate profile |
| macOS, Intel | Docker Desktop, linux/amd64 | Keep CPU baseline unless separately validated |
| Linux, Intel/AMD | Docker Engine plus Compose, linux/amd64 | NVIDIA Container Toolkit where supported |
| Linux, ARM64 | Compatible Docker Engine, linux/arm64 | Hardware-specific validation required |


Windows requires supported Windows/WSL versions and virtualization. macOS needs the correct installer for Intel or Apple silicon and a supported macOS release. Linux installation is distribution-specific. On Kali, follow the Debian-derivative guidance rather than assuming Ubuntu instructions apply. [Docker Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/); [Mac installation](https://docs.docker.com/desktop/setup/install/mac-install/); [Debian installation](https://docs.docker.com/engine/install/debian/).

Ordinary Docker Desktop GPU support is documented for Windows with WSL 2 and NVIDIA hardware. Linux NVIDIA acceleration requires drivers and the container toolkit. Mac Metal acceleration can use a native runtime or Docker Model Runner, whose engines run outside ordinary containers on macOS and Windows; treat that as a separate deployment design if every service must remain in Linux containers. [Docker GPU support](https://docs.docker.com/desktop/features/gpu/); [NVIDIA toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html); [Docker Model Runner](https://docs.docker.com/ai/model-runner/).

### Packaging model weights correctly

An image is the packaged application and runtime. A container is a running instance. Push the built application image to a registry; do not describe pushing a running container as the release process. Model weights can be downloaded into a persistent volume by a preparation job, or packaged in a separate licensed artifact. Avoid committing multi-gigabyte model files to the ordinary code repository.

The official CPU llama.cpp server image is ghcr.io/ggml-org/llama.cpp:server, and its documentation lists amd64 and arm64 support. The tag is mutable. Before release, inspect its manifest and record the tested multi-platform digest or an appropriate tested release. Apply the same rule to the Python base and Qdrant images. [llama.cpp Docker documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md).

Use named volumes for model files, Qdrant data and application-managed source files. A model mounted read-only at inference time is easier to keep stable. Volumes persist beyond a container's lifetime, but they are not automatic backups and do not synchronize different computers. [Docker volumes](https://docs.docker.com/engine/storage/volumes/).

### Dockerfile template for the application

This is a design template. It becomes runnable after the team implements app.main, app.prepare\_models and app.ingest and creates the dependency lock. PYTHON\_BASE must be set to the selected image reference; requirements.lock must contain resolved packages with hashes for the target architectures. The directories excluded by .dockerignore must include secrets, raw private files and caches.

```
ARG PYTHON\\\\\\\\\\\\\\\_BASE        
FROM $\\\\\\\\\\\\\\\{PYTHON\\\\\\\\\\\\\\\_BASE\\\\\\\\\\\\\\\}        
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1        
WORKDIR /app        
COPY requirements.lock .        
RUN pip install --no-cache-dir --require-hashes -r requirements.lock        
RUN useradd --uid 10001 --create-home appuser \\\\\\\\\\\\\\\\        
    && mkdir -p /models /data \\\\\\\\\\\\\\\\        
    && chown appuser:appuser /models /data        
COPY --chown=appuser:appuser app/ ./app/        
USER appuser        
EXPOSE 8000        
CMD \\\\\\\\\\\\\\\["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"\\\\\\\\\\\\\\\]
```

FastAPI documents building an application-specific Linux image. The template above adds this project's non-root user and model/data ownership requirements. Verify volume permissions on a clean installation and after restore. [FastAPI container guidance](https://fastapi.tiangolo.com/deployment/docker/).

### Compose template: models and inference

The two code blocks below are consecutive portions of one compose.yaml. They intentionally require selected image references. Model preparation must download the pinned artifacts from model-lock.json, verify checksums, write /models/llm and /models/embedding, and exit successfully only when complete. Package model-lock.json inside app/ or make it available through explicit configuration.

```
services:        
  model-init:        
    image: $\\\\\\\\\\\\\\\{RAG\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_IMAGE:?Set RAG\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_IMAGE\\\\\\\\\\\\\\\}        
    command: \\\\\\\\\\\\\\\["python", "-m", "app.prepare\\\\\\\\\\\\\\\_models"\\\\\\\\\\\\\\\]        
    environment:        
      HF\\\\\\\\\\\\\\\_HOME: /models/hf-cache        
    volumes:        
      - model\\\\\\\\\\\\\\\_data:/models        
    restart: "no"        
        
  llm:        
    image: $\\\\\\\\\\\\\\\{LLAMA\\\\\\\\\\\\\\\_IMAGE:?Set LLAMA\\\\\\\\\\\\\\\_IMAGE\\\\\\\\\\\\\\\}        
    command:        
      - "-m"        
      - /models/llm/qwen2.5-1.5b-instruct-q4\\\\\\\\\\\\\\\_k\\\\\\\\\\\\\\\_m.gguf        
      - "--host"        
      - "0.0.0.0"        
      - "--port"        
      - "8080"        
      - "--ctx-size"        
      - "4096"        
      - "--parallel"        
      - "1"        
      - "--n-gpu-layers"        
      - "0"        
      - "--alias"        
      - domain-rag        
    volumes:        
      - model\\\\\\\\\\\\\\\_data:/models:ro        
    depends\\\\\\\\\\\\\\\_on:        
      model-init:        
        condition: service\\\\\\\\\\\\\\\_completed\\\\\\\\\\\\\\\_successfully        
    healthcheck:        
      test: \\\\\\\\\\\\\\\["CMD", "curl", "-f", "http://localhost:8080/health"\\\\\\\\\\\\\\\]        
      interval: 10s        
      timeout: 5s        
      retries: 12        
      start\\\\\\\\\\\\\\\_period: 120s        
    restart: unless-stopped
```

The current CPU image includes curl and the server exposes /health. Model loading can take longer on constrained hardware, so the startup allowance must be measured and adjusted. The server supports a model alias and explicit context configuration. [llama.cpp CPU Dockerfile](https://github.com/ggml-org/llama.cpp/blob/master/.devops/cpu.Dockerfile); [server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

### Compose template: storage and API

```
  qdrant:        
    image: $\\\\\\\\\\\\\\\{QDRANT\\\\\\\\\\\\\\\_IMAGE:?Set QDRANT\\\\\\\\\\\\\\\_IMAGE\\\\\\\\\\\\\\\}        
    volumes:        
      - qdrant\\\\\\\\\\\\\\\_data:/qdrant/storage        
    restart: unless-stopped        
        
  api:        
    image: $\\\\\\\\\\\\\\\{RAG\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_IMAGE:?Set RAG\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_IMAGE\\\\\\\\\\\\\\\}        
    environment:        
      QDRANT\\\\\\\\\\\\\\\_URL: http://qdrant:6333        
      LLM\\\\\\\\\\\\\\\_BASE\\\\\\\\\\\\\\\_URL: http://llm:8080/v1        
      LLM\\\\\\\\\\\\\\\_MODEL\\\\\\\\\\\\\\\_ALIAS: domain-rag        
      EMBEDDING\\\\\\\\\\\\\\\_PATH: /models/embedding        
      HF\\\\\\\\\\\\\\\_HUB\\\\\\\\\\\\\\\_OFFLINE: "1"        
      DATA\\\\\\\\\\\\\\\_ROOT: /data        
    ports:        
      - "127.0.0.1:8000:8000"        
    volumes:        
      - model\\\\\\\\\\\\\\\_data:/models:ro        
      - source\\\\\\\\\\\\\\\_data:/data        
    depends\\\\\\\\\\\\\\\_on:        
      llm:        
        condition: service\\\\\\\\\\\\\\\_healthy        
      qdrant:        
        condition: service\\\\\\\\\\\\\\\_started        
    healthcheck:        
      test:        
        - CMD        
        - python        
        - -c        
        - \\\\\\\\\\\\\\\>-        
          import urllib.request;        
          urllib.request.urlopen(        
          'http://localhost:8000/health/ready', timeout=3)        
      interval: 15s        
      timeout: 5s        
      retries: 6        
      start\\\\\\\\\\\\\\\_period: 60s        
    restart: unless-stopped        
        
volumes:        
  model\\\\\\\\\\\\\\\_data:        
  qdrant\\\\\\\\\\\\\\\_data:        
  source\\\\\\\\\\\\\\\_data:
```

Qdrant's documented container storage location is /qdrant/storage. Keep its port internal for this local baseline; its default quickstart configuration does not provide authentication or encryption. The API must poll Qdrant readiness and handle later failures because service\_started only means the container has started. [Qdrant local quickstart](https://qdrant.tech/documentation/quickstart/); [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/).

The API binds all interfaces inside its container so Docker can route to it; the host publishes only 127.0.0.1. Qdrant and llama.cpp are accessed through Compose service names, not localhost from inside the API container. Bare published port mappings otherwise bind all host addresses by default. [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/).

### Command contracts and first run

The following app commands are project interfaces to implement, not existing commands supplied by a framework:

| Interface | Required behavior |
| - | - |
| python -m app.prepare\_models | Verify/download pinned model bundle; exit nonzero on failure |
| python -m app.ingest --input PATH --release NAME | Build and validate a versioned collection from permitted files |
| GET /health/live | Confirm the API process can answer |
| GET /health/ready | Check embedder, model, Qdrant and corpus compatibility |
| POST /query | Run the controlled question pipeline |
| GET /sources/... | Return permitted source content after access validation |


On an empty installation, readiness should report corpus\_not\_indexed until ingestion publishes a collection. Liveness may still pass. The ingestion command must be able to run before query readiness succeeds. The browser should explain the empty-corpus state instead of appearing broken.

1. Install a supported Docker environment and check docker version and docker compose version. On Windows, run the workflow in WSL 2 or adapt shell syntax to PowerShell.

2. Check out the repository. Create .env from .env.example and set the built application image, the tested llama.cpp image and the tested Qdrant image. Record the corresponding manifest digests for the release.

3. Build the application using the chosen PYTHON\_BASE and validated requirements.lock, or pull the team's existing application image. Ensure model-lock.json is included and resolves actual immutable model revisions.

4. Prepare model assets, then start the stack. The first online download can take time; subsequent verified starts should reuse the volume.

5. Copy approved pilot documents to source\_data, ingest them into a named release and verify readiness. Run both a supported and an unsupported question.

```
docker compose config --quiet        
docker compose run --rm model-init        
docker compose up -d        
docker compose cp ./sample\\\\\\\\\\\\\\\_docs api:/data/inbox        
docker compose exec api python -m app.ingest \\\\\\\\\\\\\\\\        
  --input /data/inbox --release pilot-v1        
docker compose ps        
docker compose logs --tail=100 api llm qdrant
```

These commands assume the template interfaces have been implemented, sample\_docs exists and the API container is running even while query readiness awaits ingestion. The model-init job must be idempotent because startup can invoke it again. For a fully offline demonstration, prefetch all images and model files, serve browser assets locally and test with network access disabled. Merely setting HF\_HUB\_OFFLINE does not provision missing assets or block every possible outbound request.

### Build, push and verify a release

Use a real registry namespace that the team can access. The following Bash command uses variables deliberately; it must be run after assigning RAG\_API\_IMAGE and PYTHON\_BASE to real values. The first value should include a version tag; record the resulting immutable manifest digest after the push.

```
docker buildx build \\\\\\\\\\\\\\\\        
  --platform linux/amd64,linux/arm64 \\\\\\\\\\\\\\\\        
  --build-arg PYTHON\\\\\\\\\\\\\\\_BASE="$PYTHON\\\\\\\\\\\\\\\_BASE" \\\\\\\\\\\\\\\\        
  --tag "$RAG\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_IMAGE" --push .        
docker buildx imagetools inspect "$RAG\\\\\\\\\\\\\\\_API\\\\\\\\\\\\\\\_IMAGE"
```

Configure a buildx builder with support for both platforms if the current builder lacks it. Build success and manifest presence are necessary but do not prove runtime correctness. Run native-architecture tests on Windows/amd64, macOS/arm64 and Linux/amd64, plus Intel Mac or ARM Linux only if those are claimed supported targets. Avoid forcing linux/amd64 on an Apple silicon machine as the normal solution; emulation can reduce performance. [Docker multi-platform builds](https://docs.docker.com/build/building/multi-platform/).

Record OS, CPU, Docker version, image digest, available RAM, model checksum, cold-start duration, peak RAM, first-answer latency and test outcome. Include the exact limitations in the release README. Evaluate model licenses and retain required notices for redistributed artifacts; installation availability is not a substitute for redistribution rights.

### Backup, recovery and common problems

Use docker compose down for routine shutdown without intentionally deleting volumes. The -v option deletes named volumes managed by the Compose project and can remove models and indexed data; reserve it for an intentional reset after backups.

Back up approved source files, corpus and model manifests, prompt/configuration versions and Qdrant snapshots. A collection snapshot does not include collection aliases, so preserve and restore alias mapping separately. Test restoration into a fresh environment, then compare point counts, known retrieval results and source resolution. [Qdrant snapshots](https://qdrant.tech/documentation/snapshots/).

| Symptom | Likely investigation |
| - | - |
| exec format error / no matching manifest | Check amd64 versus arm64 image variants |
| Container exits under load | Inspect logs, exit status and memory limits |
| Model file missing | Check provisioning result, revision, path and volume permissions |
| Slow answers | Measure CPU generation, context size, queue and token limit |
| Poor retrieval | Check extraction, truncation, model identity and source coverage |
| Vector size mismatch | Compare embedder configuration with collection schema |
| Hallucinated answer with real citation | Review semantic support, not just source-ID validity |
| Works until container recreation | Verify model/data volumes and restore procedure |
| API cannot reach model/database | Use service DNS names and internal container ports |
| Stale or deleted content appears | Check active release, cache invalidation and deletion policy |


