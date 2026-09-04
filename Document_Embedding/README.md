Document Embedding

Created by: Usha N
USN: 4BB23AI044

Purpose

This module is a part of the RAG system. It stores the embeddings of document chunks along with their related information so that relevant documents can be retrieved during a search.

Technologies

Python
Sentence Transformers
FAISS

Basic Flow

Document chunks
→ Embedding Generation
→ Document Embedding
→ FAISS Vector Index
→ Retrieval
