# 📥 Module 03 — Data Loading

**RAG System Project | Module 3 of 15**

**Author:** Srishti K R

**USN:** 4BB23CS048

**Department:** Computer Science and Engineering

---

## 🧭 Overview

The **Data Loading** module is the entry gate of the RAG (Retrieval-Augmented Generation) pipeline. Before a document can be cleaned, chunked, embedded, or retrieved, it first has to be *read* — and that's exactly what this module does. It takes a raw file (PDF, TXT, DOCX, or CSV), figures out what it is, loads it with the right tool, and hands back clean, structured content ready for the next stage.

Think of it as the **receptionist** of the RAG pipeline: it checks what's coming in, verifies it's valid, and passes it along in a standard format everyone downstream can rely on.

---

## 🎯 Objective

To reliably accept documents in multiple formats and convert them into a **consistent internal structure** — content + metadata — that any other module in the pipeline can consume, without needing to know how the original file was formatted.

---

## 🔗 Role in the RAG Pipeline

```
Raw Document
     ↓
📥 Data Loading   ← (this module)
     ↓
🧹 Data Cleaning
     ↓
📄 Document Processing
     ↓
✂️ Text Chunking
     ↓
🔢 Embedding Generation
     ↓
🗄️ Vector Database
     ↓
🔍 Retriever
     ↓
📝 Prompt Engineering
     ↓
🤖 LLM / Chat Model
     ↓
📤 Output
```

This module owns **only** the first step. Everything after loading (cleaning, chunking, embeddings, etc.) is handled by other teammates' modules.

---

## ⚙️ Simple Workflow

1. Accept a file path as input
2. Detect the file type from its extension
3. Select the matching loader (PDF / TXT / DOCX / CSV)
4. Load and extract the raw text content
5. Attach metadata (filename, file type, source path)
6. Return a clean, standardized document object
7. Hand it off to the **Data Cleaning** module

---

## 📂 Supported Input Formats

| Format | Extension | Loader Used |
|--------|-----------|-------------|
| PDF    | `.pdf`    | LangChain `PyPDFLoader` |
| Text   | `.txt`    | LangChain `TextLoader` |
| Word   | `.docx`   | LangChain `Docx2txtLoader` |
| CSV    | `.csv`    | LangChain `CSVLoader` |

Unsupported formats and missing files are handled gracefully with clear error messages.

---

## 🔄 Input & Output

**Input:** A file path to a PDF, TXT, DOCX, or CSV document.

**Output:** A structured dictionary/object containing:
- `content` — extracted text from the document
- `metadata` — filename, file type, source path, and other useful info
- `status` — success/failure indicator

---

## 🛠️ Technologies Used

- Python 3.x
- LangChain Document Loaders
- `pypdf` (for PDF parsing)
- `python-docx` / `docx2txt` (for Word documents)
- Standard library (`os`, `pathlib`) for file handling

---

## 🤝 Connecting to Data Cleaning

Once a document is loaded, the output object is passed directly to **Module 04 — Data Cleaning**. That module takes the raw extracted `content`, removes noise (extra whitespace, special characters, headers/footers, etc.), and prepares it for chunking. Data Loading does **not** perform any cleaning — it strictly focuses on getting the document *in* correctly.

```
Loaded Document (content + metadata)
              ↓
     Data Cleaning Module
```

---

## ✅ Conclusion

Module 03 keeps things simple on purpose: **one job, done well.** By standardizing how documents enter the pipeline regardless of their original format, it lets every other module — cleaning, chunking, embedding, and beyond — work with predictable, consistent input. A small module, but a foundational one. 🚀
