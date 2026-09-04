\# VECTOR DATABASE SETUP



\## Purpose



The Vector Database Setup module is a part of the RAG system. It is responsible for storing document embeddings along with their corresponding document chunks and metadata so that relevant information can be retrieved efficiently.



\## Technology Used



\- Python

\- ChromaDB

\- Vector Embeddings



\## Input



The module receives document chunks, their generated embeddings, and metadata such as document name, page number, and chunk ID.



\## Working



1\. Receive document chunks and their embeddings.

2\. Store the embeddings in a ChromaDB collection.

3\. Store the corresponding document chunks and metadata.

4\. Perform similarity search using query embeddings.

5\. Return the most relevant document chunks to the Retrieval module.



\## Output



The output is a ChromaDB collection containing document embeddings, document chunks, metadata, and unique IDs that can be searched during the retrieval stage of the RAG pipeline.

