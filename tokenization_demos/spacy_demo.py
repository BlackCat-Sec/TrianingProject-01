"""spaCy English tokenization without an external language-model download."""
import spacy


def main() -> None:
    text = "Linux-based systems are powerful, secure, and flexible."
    tokenizer = spacy.blank("en")
    document = tokenizer(text)
    print("Input:", text)
    print("\nToken                 Start  End")
    for token in document:
        print(f"{token.text:<20} {token.idx:<6} {token.idx + len(token.text)}")


if __name__ == "__main__":
    main()
