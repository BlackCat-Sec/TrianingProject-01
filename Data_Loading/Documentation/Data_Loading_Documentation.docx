# 📄 Data Loading Module — Documentation

**Project:** Simple RAG (Retrieval-Augmented Generation) System
**Module:** 03 — Data Loading
**Prepared by:** Srishti K R
**USN:** 4BB23CS048
**Department:** Computer Science and Engineering

---

## 1. Introduction

This document explains **Module 03 — Data Loading**, one part of a 15-module RAG project built by our team. This module's job is simple: take a document file, read its content, and pass it to the next module.

---

## 2. What is RAG?

RAG (Retrieval-Augmented Generation) is a technique where a chatbot doesn't just rely on what it already "knows" — it first looks up relevant information from documents we give it, and then uses that information to answer a user's question. This makes the chatbot's answers more accurate and based on real content instead of guesses.

---

## 3. Where Data Loading Fits

Data Loading is the **first step** of the pipeline. Before the system can clean, chunk, or search through a document, it first has to be read into the program. That's what this module does.

```
Document File → Data Loading → Data Cleaning → ... → Chatbot Answer
```

---

## 4. Objective

To read a document (PDF, TXT, DOCX, or CSV), extract its text content, and hand it over to the Data Cleaning module in a simple, consistent format.

---

## 5. Responsibilities

**This module does:**
- Check if the file exists
- Detect the file type
- Read the document and extract its text
- Return the text along with basic details (filename, type)

**This module does NOT do:**
- Clean or format the text (Data Cleaning module's job)
- Split text into chunks (Text Chunking module's job)
- Create embeddings or store in a database (later modules)
- Anything related to answering the user's question

---

## 6. Supported Formats

| Format | Extension |
|--------|-----------|
| PDF    | `.pdf`    |
| Text   | `.txt`    |
| Word   | `.docx`   |
| CSV    | `.csv`    |

---

## 7. Workflow

1. Take the file path as input
2. Check the file exists
3. Look at the file extension to know its type
4. Use the matching method to read the file
5. Extract the text
6. Return the text + basic info (filename, type)

---

## 8. Technologies Used

| Library | Used For |
|---------|----------|
| `pypdf` | Reading text from PDF files |
| `docx2txt` | Reading text from Word (.docx) files |
| `csv` (built-in) | Reading CSV files |
| `os` (built-in) | Checking if a file exists |

Simple, lightweight libraries — no heavy frameworks needed for this small project.

---

## 9. Input

A file path, e.g. `"Data/sample_documents/sample.pdf"`

---

## 10. Output

A simple dictionary:

```python
{
    "status": "success",
    "content": "extracted text goes here...",
    "filename": "sample.pdf",
    "file_type": "pdf"
}
```

If something goes wrong, `status` becomes `"error"` and an `"error"` message is included instead.

---

## 11. Error Handling

- **File not found** → returns a clear error message instead of crashing.
- **Unsupported file type** → returns a clear error message listing supported formats.

---

## 12. Example Usage

```python
from data_loader import load_document

result = load_document("Data/sample_documents/sample.pdf")

if result["status"] == "success":
    print(result["content"][:200])   # preview first 200 characters
else:
    print("Error:", result["error"])
```

---

## 13. Connection to Data Cleaning

Once this module returns the extracted text, the Data Cleaning module takes that text and removes unwanted formatting, extra spaces, and noise, before passing it further down the pipeline.

```
load_document() output → Data Cleaning module input
```

---

## 14. Limitations

- Only supports PDF, TXT, DOCX, CSV (no images or scanned documents).
- Doesn't handle badly corrupted files.
- Built for one file at a time, not folders of files.

---

## 15. Conclusion

This module keeps things simple: read the document, get the text out, pass it along. It's a small but necessary first step that lets the rest of the RAG pipeline work with clean, ready-to-process text.
