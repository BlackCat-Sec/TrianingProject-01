"""Run the four AI Track tokenization demonstrations in sequence."""
from . import bpe_demo, nltk_demo, spacy_demo, tiktoken_demo


def main() -> None:
    for title, demo in (("BPE", bpe_demo), ("spaCy", spacy_demo), ("NLTK", nltk_demo), ("tiktoken", tiktoken_demo)):
        print(f"\n{'=' * 14} {title} {'=' * 14}")
        demo.main()


if __name__ == "__main__":
    main()
