from pathlib import Path
from app.rag import Chunk, HuggingFaceRag, clean_extracted_text


def test_requires_a_readable_document(tmp_path: Path):
    rag = HuggingFaceRag("unused")
    try:
        rag.index([tmp_path / "missing.pdf"])
    except ValueError as error:
        assert "missing document" in str(error)
    else:
        raise AssertionError("Expected missing document to be rejected")


def test_repairs_character_spaced_pdf_text():
    assert clean_extracted_text("l i n u x is p o w e r f u l") == "linux is powerful"


def test_selects_the_question_relevant_sentence():
    text = "Linux is an open-source operating system. It includes many command-line tools."
    assert HuggingFaceRag._best_sentence(text, "What is Linux?") == "Linux is an open-source operating system."


def test_definition_question_skips_an_unrelated_leading_fragment():
    text = "Working with Linux is useful. Linux is granular and gives detailed system control."
    assert HuggingFaceRag._best_sentence(text, "What is Linux?") == "Linux is granular and gives detailed system control."


def test_greeting_does_not_search_the_pdf():
    rag = HuggingFaceRag("unused")
    rag._embedder = object()
    rag._vectors = object()
    response = rag.answer("hi")
    assert response.status == "clarification_needed"
    assert response.citations == []
