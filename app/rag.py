from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from .contracts import AnswerResponse, Citation


def clean_extracted_text(raw_text: str) -> str:
    """Normalize whitespace and repair runs of separately extracted letters."""
    text = " ".join(raw_text.replace("\ufffd", " ").split())
    # Some pages in the supplied PDF encode words as `l i n u x`. Join only
    # runs of three or more one-character tokens so normal prose is retained.
    return re.sub(r"\b(?:[A-Za-z0-9]\s+){2,}[A-Za-z0-9]\b", lambda match: match.group(0).replace(" ", ""), text)


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    title: str
    text: str
    index: int
    page: int


class HuggingFaceRag:
    """RAG indexes documents; the open model weights are never fine-tuned."""

    def __init__(self, embedding_model: str, generator_model: str = "Qwen/Qwen2.5-1.5B-Instruct",
                 chunk_words: int = 180, overlap: int = 35, evidence_threshold: float = 0.20,
                 retrieval_k: int = 4):
        self.embedding_model = embedding_model
        self.generator_model = generator_model
        self.chunk_words, self.overlap = chunk_words, overlap
        self.evidence_threshold = evidence_threshold
        self.retrieval_k = retrieval_k
        self.chunks: list[Chunk] = []
        self.corpus_version = "empty"
        self._embedder = self._vectors = self._tokenizer = self._llm = None

    def index(self, paths: list[Path]) -> int:
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in {".pdf", ".txt", ".md"}:
                raise ValueError(f"Unsupported or missing document: {path}")
        import fitz
        from sentence_transformers import SentenceTransformer

        chunks: list[Chunk] = []
        digest = sha256()
        for path in paths:
            pages = ([(number, page.get_text()) for number, page in enumerate(fitz.open(str(path)), 1)]
                     if path.suffix.lower() == ".pdf" else [(1, path.read_text(encoding="utf-8"))])
            for page_number, raw_text in pages:
                text = clean_extracted_text(raw_text)
                if not text:
                    continue
                digest.update(text.encode())
                tokens = text.split()
                for start in range(0, len(tokens), self.chunk_words - self.overlap):
                    passage = " ".join(tokens[start:start + self.chunk_words])
                    if passage:
                        chunks.append(Chunk(path.stem, path.stem.replace("_", " ").title(), passage, len(chunks) + 1, page_number))
                    if start + self.chunk_words >= len(tokens):
                        break
        if not chunks:
            raise ValueError("No readable text was found. The PDF may be scanned and require OCR.")
        self.chunks, self.corpus_version = chunks, digest.hexdigest()[:12]
        self._embedder = SentenceTransformer(self.embedding_model)
        self._vectors = self._embedder.encode([chunk.text for chunk in chunks], normalize_embeddings=True, show_progress_bar=True)
        return len(chunks)

    def answer(self, question: str) -> AnswerResponse:
        if not question.strip():
            raise ValueError("Question cannot be empty.")
        if self._embedder is None or self._vectors is None:
            raise RuntimeError("Index documents before asking a question.")
        if question.strip().lower() in {"hi", "hello", "hey", "good morning", "good afternoon"}:
            return AnswerResponse(str(uuid4()), "clarification_needed",
                "Ask a question about the indexed PDF. For example: What is Linux?", [], self.corpus_version)
        query = self._embedder.encode([question], normalize_embeddings=True)[0]
        scores = self._vectors @ query
        ranked_indices = scores.argsort()[-self.retrieval_k:][::-1]
        best_index = int(ranked_indices[0])
        score = float(scores[best_index])
        if score < self.evidence_threshold:
            return self._no_evidence(score)
        evidence = [self.chunks[int(index)] for index in ranked_indices]
        generated = self._generate_answer(question, evidence)
        if not generated or "INSUFFICIENT_EVIDENCE" in generated.upper():
            return self._no_evidence(score)
        if not re.search(r"\[S[1-4]\]", generated):
            generated = f"{generated} [S1]"
        citations = [Citation(f"S{number}", chunk.doc_id, chunk.title,
                              {"page": chunk.page, "chunk": chunk.index},
                              chunk.text[:360] + ("…" if len(chunk.text) > 360 else ""))
                     for number, chunk in enumerate(evidence, 1)]
        return AnswerResponse(str(uuid4()), "answered", generated, citations, self.corpus_version,
                              warnings=[f"Best retrieved evidence score: {score:.2f}"])

    def _generate_answer(self, question: str, evidence: list[Chunk]) -> str:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if self._tokenizer is None or self._llm is None:
            print(f"Loading answer model {self.generator_model}. This first download is several GB and may take a few minutes...")
            self._tokenizer = AutoTokenizer.from_pretrained(self.generator_model)
            self._llm = AutoModelForCausalLM.from_pretrained(self.generator_model, dtype="auto")
            self._llm.eval()
            # This project uses deterministic generation. Some model configs
            # retain sampling defaults which trigger an irrelevant warning.
            self._llm.generation_config.temperature = None
            self._llm.generation_config.top_p = None
            self._llm.generation_config.top_k = None
        context = "\n\n".join(
            f"[{number}] {chunk.title}, page {chunk.page}\n{chunk.text}"
            for number, chunk in enumerate(evidence, 1)
        )
        messages = [
            {"role": "system", "content": (
                "Answer only from the supplied PDF evidence. Do not use outside knowledge. "
                "Give a clear, concise answer. Cite one or more source labels such as [S1]. "
                "If the evidence does not answer the question, reply exactly INSUFFICIENT_EVIDENCE."
            )},
            {"role": "user", "content": f"Question: {question}\n\nPDF evidence:\n{context}"},
        ]
        prompt = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=6000)
        with torch.inference_mode():
            output = self._llm.generate(**inputs, max_new_tokens=180, do_sample=False,
                                        pad_token_id=self._tokenizer.eos_token_id)
        generated_tokens = output[0][inputs.input_ids.shape[1]:]
        return self._tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    @staticmethod
    def _best_sentence(text: str, question: str) -> str:
        ignored = {"what", "which", "when", "where", "who", "why", "how", "is", "are", "the", "a", "an", "of", "to", "in"}
        keywords = {word.lower() for word in re.findall(r"[A-Za-z0-9]+", question) if word.lower() not in ignored}
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
        if not sentences:
            return text[:360]
        definition = re.fullmatch(r"\s*what\s+(?:is|are|was|were)\s+(.+?)[?!.]*\s*", question, re.IGNORECASE)
        if definition:
            topic = re.escape(definition.group(1).strip())
            pattern = re.compile(rf"\b{topic}\s+(?:is|are|was|were)\b", re.IGNORECASE)
            matches = [(match.start(), sentence[match.start():])
                       for sentence in sentences for match in [pattern.search(sentence)] if match]
            if matches:
                _, answer = min(matches, key=lambda item: item[0])
                return answer
        return max(sentences, key=lambda part: sum(word in part.lower() for word in keywords))

    def _no_evidence(self, score: float | None = None) -> AnswerResponse:
        warnings = [] if score is None else [f"Best evidence score: {score:.2f} (below threshold)."]
        return AnswerResponse(str(uuid4()), "insufficient_evidence",
            "I couldn't find enough information in the available documents to answer that.", [], self.corpus_version,
            warnings=warnings)
