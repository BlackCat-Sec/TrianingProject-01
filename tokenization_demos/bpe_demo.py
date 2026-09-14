"""A compact educational implementation of Byte Pair Encoding (BPE)."""
from collections import Counter


TRAINING_WORDS = {"low": 5, "lower": 2, "newest": 6, "widest": 3}


def pair_counts(vocabulary: dict[tuple[str, ...], int]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for symbols, frequency in vocabulary.items():
        for left, right in zip(symbols, symbols[1:]):
            counts[(left, right)] += frequency
    return counts


def merge_pair(pair: tuple[str, str], vocabulary: dict[tuple[str, ...], int]) -> dict[tuple[str, ...], int]:
    merged: dict[tuple[str, ...], int] = {}
    for symbols, frequency in vocabulary.items():
        output, index = [], 0
        while index < len(symbols):
            if index + 1 < len(symbols) and symbols[index:index + 2] == pair:
                output.append("".join(pair))
                index += 2
            else:
                output.append(symbols[index])
                index += 1
        merged[tuple(output)] = frequency
    return merged


def train_bpe(words: dict[str, int], merges: int = 8) -> list[tuple[str, str]]:
    vocabulary = {tuple(word) + ("</w>",): frequency for word, frequency in words.items()}
    learned: list[tuple[str, str]] = []
    for _ in range(merges):
        counts = pair_counts(vocabulary)
        if not counts:
            break
        pair, _ = counts.most_common(1)[0]
        learned.append(pair)
        vocabulary = merge_pair(pair, vocabulary)
    return learned


def encode(word: str, learned: list[tuple[str, str]]) -> list[str]:
    symbols = tuple(word) + ("</w>",)
    for pair in learned:
        symbols = next(iter(merge_pair(pair, {symbols: 1})))
    return list(symbols)


def main() -> None:
    learned = train_bpe(TRAINING_WORDS)
    print("BPE training words:", TRAINING_WORDS)
    print("Learned merges:", [" + ".join(pair) for pair in learned])
    print("Tokens for 'newer':", encode("newer", learned))


if __name__ == "__main__":
    main()
