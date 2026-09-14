from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Citation:
    source_id: str
    doc_id: str
    title: str
    location: dict[str, int]
    excerpt: str
    document_version: str = "local"


@dataclass(frozen=True)
class AnswerResponse:
    request_id: str
    status: Literal["answered", "insufficient_evidence", "clarification_needed"]
    answer: str
    citations: list[Citation]
    corpus_version: str
    schema_version: str = "1.0"
    warnings: list[str] = field(default_factory=list)
