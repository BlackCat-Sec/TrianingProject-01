# AI Track: Tokenization Techniques

This folder contains one small, runnable program for each required technique. Each program uses the same sample sentence so that the token output can be compared.

## Install

From the repository root:

```powershell
python -m pip install -r requirements.txt
```

## Run every demonstration

```powershell
python -m tokenization_demos.run_all
```

Or run an individual technique:

```powershell
python -m tokenization_demos.bpe_demo
python -m tokenization_demos.spacy_demo
python -m tokenization_demos.nltk_demo
python -m tokenization_demos.tiktoken_demo
```

## 1. BPE: Byte Pair Encoding

BPE begins with characters and repeatedly merges the most frequent adjacent pair. The `bpe_demo.py` file implements this learning process from scratch. It shows the learned merges and then applies them to a new word. BPE is useful for unknown words because they can be represented with smaller subword units.

## 2. spaCy

`spacy_demo.py` uses `spacy.blank("en")`, which provides spaCy's fast rule-based English tokenizer without requiring a downloaded language model. It prints each token and its position in the original text.

## 3. NLTK

`nltk_demo.py` uses NLTK's `wordpunct_tokenize`. It separates words and punctuation without requiring an extra NLTK corpus download. This is useful for a reproducible classroom demonstration.

## 4. tiktoken

`tiktoken_demo.py` uses OpenAI's `cl100k_base` encoding. It prints the numeric token IDs, decoded token pieces, and count. Token IDs are the representation passed to compatible language models, rather than ordinary words.

## Comparison

| Technique | Main unit | Key point |
| --- | --- | --- |
| BPE | learned subwords | frequent pairs are merged |
| spaCy | linguistic tokens | fast, language-aware tokenization |
| NLTK | words and punctuation | simple classical NLP preprocessing |
| tiktoken | model token IDs | estimates/model input token representation |
