"""NLTK word-and-punctuation tokenization."""
from nltk.tokenize import wordpunct_tokenize


def main() -> None:
    text = "Linux-based systems are powerful, secure, and flexible."
    print("Input:", text)
    print("NLTK tokens:", wordpunct_tokenize(text))


if __name__ == "__main__":
    main()
