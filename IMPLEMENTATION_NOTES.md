# Implemented Assignment: Terminal PDF RAG and Tokenization Demos

## Purpose

This note records the runnable implementation included with this repository. It complements the numbered module documents; it does not replace the team documentation or alter its authorship information.

The numbered documents describe a planned production-style RAG architecture using FastAPI, Qdrant, Docker, and llama.cpp. For the assignment submission, the repository implements a smaller local terminal version that can answer questions from an uploaded PDF without operating database or web services.

## Implemented RAG workflow

```text
PDF in data/
  -> PyMuPDF extracts page text while preserving word boundaries
  -> text is split into overlapping chunks
  -> all-MiniLM-L6-v2 creates chunk embeddings
  -> semantic search selects relevant evidence
  -> Qwen2.5-1.5B-Instruct answers using only the retrieved evidence
  -> terminal prints answer, source excerpt, PDF page, and chunk number
```

Qwen receives only the top retrieved PDF passages, produces a concise answer, and is instructed to cite source labels. If no sufficiently relevant evidence exists, the program returns an insufficient-evidence message instead of inventing an answer. The terminal always displays the supporting excerpts with their page and chunk locations so the answer can be checked against the PDF.

## Source code locations

| Path | Responsibility |
| --- | --- |
| `app/cli.py` | Terminal command, automatic PDF discovery in `data/`, interactive question loop, and configured model names |
| `app/rag.py` | PDF text extraction, cleaning, chunking, embedding, semantic retrieval, Qwen answer generation, and citation creation |
| `data/` | Assignment PDF corpus; all PDFs in this folder are indexed automatically |
| `requirements.txt` | Python dependencies |
| `tokenization_demos/` | BPE, spaCy, NLTK, and tiktoken AI Track demonstrations |

## Models

| Role | Hugging Face model | Use |
| --- | --- | --- |
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` | Converts each PDF chunk and user question into vectors for semantic similarity search |
| Answer generation | `Qwen/Qwen2.5-1.5B-Instruct` | Generates a concise answer from the top retrieved PDF passages |

This is retrieval-augmented generation, not model training or fine-tuning. The open-source model weights remain unchanged. Indexing the PDF creates searchable embeddings only for the local document collection. Qwen receives the user question together with the top retrieved passages and is instructed to answer only from them, cite source labels, or return `INSUFFICIENT_EVIDENCE`.

## Run instructions

From the repository root:

```powershell
python -m pip install -r requirements.txt
python -m app.download_models
python -m app.cli
```

`python -m app.download_models` downloads only the required SafeTensors/PyTorch model files once into the local Hugging Face cache. It skips optional ONNX and OpenVINO variants. The application then reuses that cache, so the normal question-answering command does not need to download model weights again. Ask a question at the `Question:` prompt and type `exit` to end the program.

### Model resource options

The default answer model is `Qwen/Qwen2.5-1.5B-Instruct`. Its primary model file is approximately 3.09 GB, so it is the higher-quality local option for the assignment but needs several GB of free disk space and adequate RAM. If the computer is constrained, pass `--generator-model "Qwen/Qwen2.5-0.5B-Instruct"` to the CLI. This smaller option reduces resource use but may produce less complete answers.

The retrieval model is always `sentence-transformers/all-MiniLM-L6-v2` unless explicitly overridden with `--embedding-model`.

To use a PDF outside `data/`:

```powershell
python -m app.cli --pdf "D:\path\to\document.pdf"
```

## Assignment verification

The project includes a focused test suite covering invalid documents, character-spaced PDF text cleanup, and question-relevant sentence selection:

```powershell
python -m pytest -q
```

Current verification result: `7 passed`.

The BPE demonstration can be run without extra model downloads:

```powershell
python -m tokenization_demos.bpe_demo
```

Run all AI Track tokenization demonstrations after installing dependencies:

```powershell
python -m tokenization_demos.run_all
```

## Scope and limitations

- The implementation is a local, single-user terminal demonstration. It can also run using the included Docker Compose configuration; it is not a FastAPI web-service deployment.
- It supports text-based PDFs. Scanned/image-only PDFs require OCR before useful text can be extracted.
- Semantic scores are retrieval signals, not factual confidence values.
- Answers include the page/chunk source so they can be checked against the uploaded document.
