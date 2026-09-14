"""Inspect model-style token IDs with tiktoken's cl100k_base encoding."""
import tiktoken


def main() -> None:
    text = "Linux-based systems are powerful, secure, and flexible."
    encoding = tiktoken.get_encoding("cl100k_base")
    token_ids = encoding.encode(text)
    print("Input:", text)
    print("Token IDs:", token_ids)
    print("Decoded pieces:", [encoding.decode([token_id]) for token_id in token_ids])
    print("Token count:", len(token_ids))


if __name__ == "__main__":
    main()
