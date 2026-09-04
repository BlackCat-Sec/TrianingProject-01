# Embedding Generation
## Created by: Nisarga M Jain
## USN: 4BB23CS028

---

## Purpose

This module is a part of the RAG system. It is responsible for converting document chunks into numerical vector representations called embeddings. These embeddings capture the semantic meaning of the text and help the system retrieve relevant information based on user queries.

---

## Technologies
- Python
- Sentence Transformers
- Hugging Face
- LangChain

---

## Basic Flow

Document Chunks  
→ Embedding Model  
→ Vector Embeddings  
→ Vector Database  
→ Retrieval

---

## Working

1. The processed documents are divided into smaller text chunks.
2. Each text chunk is passed to an embedding model.
3. The embedding model converts the text into numerical vector representations.
4. These vector embeddings represent the semantic meaning of the document content.
5. The generated embeddings are sent to the vector database for storage.
6. When a user enters a query, the query is also converted into an embedding.
7. Similarity search is performed to identify the most relevant document chunks.

---

## Input

- Processed document chunks

---

## Output

- Numerical vector embeddings representing the semantic meaning of the document chunks.


