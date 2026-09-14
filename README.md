# Evidence — Simple RAG System

A small, terminal-only, document-grounded question answering demo based on this repository's RAG plan. It indexes PDFs, retrieves relevant chunks with an open Hugging Face embedding model, and uses an open Hugging Face instruction model to answer from those passages with page citations. It declines questions without adequate evidence.

This submission also includes the four AI Track tokenization assignments in `tokenization_demos/`. See [the assignment guide](tokenization_demos/README.md).

See [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) for the runnable system architecture, source-code locations, models, Docker deployment, verification commands, and the difference between this assignment implementation and the larger planned architecture in the numbered module documents.

## Run

### 1. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Python packages

```powershell
python -m pip install -r requirements.txt
```

### 3. Download models once

```powershell
python -m app.download_models
```

This downloads only the standard SafeTensors/PyTorch files used by this project into the local Hugging Face cache; it deliberately skips optional ONNX and OpenVINO variants. It downloads the Qwen answer model first and then the MiniLM embedding model. Do not stop the command before both steps finish.

### 4. Start the terminal application

```powershell
python -m app.cli "What is Linux?"
```

PDF files in `data/` are indexed automatically. The first run downloads `sentence-transformers/all-MiniLM-L6-v2` and `Qwen/Qwen2.5-1.5B-Instruct` from Hugging Face. Qwen is a 1.5B-parameter model, so allow several GB of disk space and a few minutes for the initial download/load. Later runs use the local Hugging Face cache. Qwen receives only the retrieved PDF passages and is instructed to cite them or decline unsupported questions. Provide a different PDF with `--pdf`.

Run `python -m app.download_models` once after installing requirements to download both models before starting the app. They are saved in the local Hugging Face cache and reused by every later run.

Expected terminal flow:

```text
Indexed <number> chunks. Type 'exit' to quit.
Question: what is linux
<cited sentence> [S1]
Sources
[S1] <document title> (page <number>, chunk <number>)
```

## Commands

`python -m app.cli --pdf "path-to-book.pdf" "your question"` asks one question. Omit the question to start an interactive prompt. The open-source Hugging Face models are `sentence-transformers/all-MiniLM-L6-v2` for retrieval and `Qwen/Qwen2.5-1.5B-Instruct` for answers. This is RAG, not fine-tuning: the model's weights are unchanged and answers are grounded in the indexed PDF.

### Common commands

```powershell
# Interactive question mode; PDFs in data/ are indexed automatically.
python -m app.cli

# Ask one question directly.
python -m app.cli "What is Linux?"

# Use a PDF outside the data/ folder.
python -m app.cli --pdf "D:\path\to\book.pdf" "What is Linux?"

# Use a smaller answer model when disk space or RAM is limited.
python -m app.download_models --generator-model "Qwen/Qwen2.5-0.5B-Instruct"
python -m app.cli --generator-model "Qwen/Qwen2.5-0.5B-Instruct"
```

## Model choices

| Role | Default model | Approximate download | Purpose |
| --- | --- | --- | --- |
| Retrieval | `sentence-transformers/all-MiniLM-L6-v2` | ~90 MB | Finds relevant PDF passages |
| Answer generation | `Qwen/Qwen2.5-1.5B-Instruct` | 3.09 GB | Produces grounded answers from retrieved passages |
| Smaller option | `Qwen/Qwen2.5-0.5B-Instruct` | ~1 GB | Lower disk/RAM use, but less capable answers |

Use the default 1.5B Qwen model when your computer has at least 5–6 GB free disk space and 8 GB or more RAM. Use the 0.5B model when resources are limited. Model files are cached at `C:\Users\gowda\.cache\huggingface\hub` and reused on later runs.

## Troubleshooting

- **Initial run takes time:** model files are downloading or loading; wait until the terminal shows the `Question:` prompt.
- **Windows symlink warning:** this is harmless. The cache still works; it may use more disk space.
- **`INSUFFICIENT_EVIDENCE`:** the PDF may not contain enough relevant text for that question. Rephrase the question with terms from the book.
- **Garbled PDF text:** this project uses PyMuPDF to preserve word spacing in the supplied PDF. Image-only PDFs require OCR.
- **Stop the program:** press `Ctrl+C`, or type `exit` in interactive mode.

## Verify

```powershell
python -m pytest -q
python -m tokenization_demos.run_all
```

The current project checks pass: `7 passed`.

## Run with Docker

Docker is optional. It runs the same terminal application inside a Linux container and stores downloaded Hugging Face models in a named Docker volume, so they are not downloaded again after the container stops. Install and start Docker Desktop before using these commands.

### 1. Build the image

```powershell
docker compose build
```

### 2. Download models once into the Docker volume

```powershell
docker compose run --rm rag python -m app.download_models
```

### 3. Run interactively

```powershell
docker compose run --rm -it rag
```

### 4. Ask one question directly

```powershell
docker compose run --rm rag python -m app.cli "What is Linux?"
```

The `data/` folder is mounted read-only in the container. Add or replace PDFs in the local `data/` folder, then run the command again. The model cache persists in the `hf_model_cache` Docker volume. To deliberately remove Docker-cached models and download them again, run:

```powershell
docker compose down --volumes
```
and u can run this system in any file 
