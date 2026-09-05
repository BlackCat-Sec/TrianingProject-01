
1. Module Title

Module Name: Text Chunking and Data PPreprocessing

---

2. Objective

Write:

> The objective of this module is to preprocess the collected domain-specific documents and divide the extracted text into smaller meaningful chunks. These chunks are used for generating embeddings and retrieving relevant information in the Domain-Specific RAG system.




---

3. Tools and Technologies Used


---

4. Input Data

Mention what data you are using.

Example:

> The input data consists of domain-specific documents collected in PDF format. These documents contain information related to the selected domain. The documents are stored in a separate data folder before preprocessing.



Folder structure

Domain_RAG/
│
├── data/
│   ├── document1.pdf
│   ├── document2.pdf
│   └── document3.pdf
│
├── chunking.py
│
└── output/

Take a screenshot of your project folder and add it here.


---

5. Step-by-Step Implementation

Step 1: Install Required Library

Install the PDF reading library.

pip install pypdf

Documentation text:

> The PyPDF library was installed to extract textual information from PDF documents.



Take a screenshot of the terminal after installation.


---

Step 2: Import Required Libraries

from pypdf import PdfReader

Documentation text:

> The PdfReader module from the PyPDF library was imported to read and extract textual content from the uploaded PDF documents.



Take a screenshot of this code.


---

Step 3: Load the Document

reader = PdfReader("data/document.pdf")

Documentation text:

> The domain-specific PDF document was loaded using the PdfReader function. The document is stored inside the data folder of the project.




---

Step 4: Extract Text from PDF

text = ""

for page in reader.pages:
    text += page.extract_text()

Documentation text:

> The system reads each page of the PDF document and extracts the available textual content. The extracted text from all pages is combined into a single variable for further preprocessing.




---

Step 5: Clean the Extracted Text

cleaned_text = " ".join(text.split())

Documentation text:

> The extracted text may contain unnecessary spaces, line breaks, and formatting issues. Therefore, basic text cleaning is performed to normalize the data before chunking.




---

Step 6: Define the Text Chunking Function

def chunk_text(text, chunk_size=500, overlap=100):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

Documentation text:

> A text chunking function was developed to divide the large extracted document into smaller text segments. Each chunk contains a maximum of 500 characters. An overlap of 100 characters is maintained between consecutive chunks to preserve contextual continuity.




---

Step 7: Generate Text Chunks

chunks = chunk_text(cleaned_text)

Documentation text:

> The cleaned document text is passed to the chunking function. The function generates multiple smaller text chunks from the original document.




---

Step 8: Display the Chunks

for i, chunk in enumerate(chunks):
    print(f"Chunk {i + 1}")
    print(chunk)
    print("-" * 50)

Documentation text:

> The generated chunks are displayed to verify the chunking process. Each chunk is assigned a unique sequence number.



Take a screenshot of the output.


---

6. Complete Code

Create a section called:

Implementation Code

from pypdf import PdfReader

reader = PdfReader("data/document.pdf")

text = ""

for page in reader.pages:
    extracted_text = page.extract_text()

    if extracted_text:
        text += extracted_text

cleaned_text = " ".join(text.split())


def chunk_text(text, chunk_size=500, overlap=100):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


chunks = chunk_text(cleaned_text)

print("Total Chunks:", len(chunks))

for i, chunk in enumerate(chunks):

    print("\nChunk", i + 1)
    print(chunk)
    print("-" * 50)


---

7. Output

Document your output like this:

Total Chunks: 25

Chunk 1:
Kidney stones are hard deposits made of minerals and salts...

--------------------------------------------------

Chunk 2:
Minerals and salts can accumulate inside the kidneys...

--------------------------------------------------

Documentation text:

> The system successfully divided the complete document into multiple smaller chunks. These chunks preserve portions of the original information and can be used as input for the embedding generation process.




---

8. Workflow Diagram

Include this in your documentation:

┌───────────────────┐
                │ Domain PDF Data   │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Text Extraction   │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Text Cleaning     │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Text Chunking     │
                │ 500 Characters    │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Chunk Overlap     │
                │ 100 Characters    │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Generated Chunks  │
                └───────────────────┘


---

9. Result

You can write this in your report:

> The text chunking module was successfully implemented for the Domain-Specific RAG system. The domain documents were read and converted into textual format. The extracted text was cleaned and divided into smaller chunks using a fixed-size chunking technique with overlap. The generated chunks will be used in the next stage of the RAG pipeline for embedding generation and vector database storage.




---

10. Screenshot Order for Your Documentation

Your Word/PDF documentation should contain screenshots in this order:

1. Project folder structure.


2. Dataset/PDF documents.


3. Library installation.


4. Import libraries.


5. PDF text extraction code.


6. Text cleaning code.


7. Text chunking function.


8. Complete code execution.


9. Generated chunks output.


10. Final workflow diagram.



Recommended Document Structure

CHAPTER 1 – INTRODUCTION

CHAPTER 2 – OBJECTIVE

CHAPTER 3 – TOOLS AND TECHNOLOGIES

CHAPTER 4 – DATA COLLECTION

CHAPTER 5 – TEXT EXTRACTION

CHAPTER 6 – DATA PREPROCESSING

CHAPTER 7 – TEXT CHUNKING IMPLEMENTATION

CHAPTER 8 – RESULTS AND OUTPUT

CHAPTER 9 – CONCLUSION

CHAPTER 10 – FUTURE WORK



