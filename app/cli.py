"""Terminal entry point for PDF question answering with open Hugging Face models."""
from __future__ import annotations

import argparse
from pathlib import Path

from .rag import HuggingFaceRag

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def print_answer(rag: HuggingFaceRag, question: str) -> None:
    response = rag.answer(question)
    print(f"\n{response.answer}\n")
    for warning in response.warnings:
        print(f"{warning}")
    if response.citations:
        print("Sources")
        for citation in response.citations:
            print(f"[{citation.source_id}] {citation.title} (page {citation.location['page']}, chunk {citation.location['chunk']})")
            print(f"    {citation.excerpt}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions about local documents with open Hugging Face models.")
    parser.add_argument("question", nargs="*", help="Question to ask; omit for interactive mode.")
    parser.add_argument("--pdf", type=Path, action="append", default=[], help="PDF to index; repeat for more files.")
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--generator-model", default="Qwen/Qwen2.5-1.5B-Instruct",
                        help="Hugging Face instruction model used to answer from retrieved PDF evidence.")
    args = parser.parse_args()
    # PDFs placed in the project's data folder are the default corpus.
    documents = args.pdf or sorted(DATA_DIR.glob("*.pdf"))
    if not documents:
        parser.error("Put a PDF in the data folder or provide one with --pdf path-to-file.pdf")
    rag = HuggingFaceRag(args.embedding_model, args.generator_model)
    print("Reading documents and building the local search index...")
    try:
        count = rag.index(documents)
    except (ValueError, OSError) as error:
        parser.exit(f"Indexing failed: {error}\n")
    if args.question:
        print_answer(rag, " ".join(args.question))
        return
    print(f"Indexed {count} chunks. Type 'exit' to quit.")
    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if question.lower() in {"exit", "quit"}:
            return
        if question:
            print_answer(rag, question)


if __name__ == "__main__":
    main()
