"""Download the Hugging Face models once into the local cache."""
import argparse

from huggingface_hub import snapshot_download


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_GENERATOR_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

# The embedding repository also contains ONNX, OpenVINO and other runtime
# variants. This terminal project uses PyTorch/SafeTensors only.
EMBEDDING_FILES = (
    "config.json", "config_sentence_transformers.json", "modules.json",
    "sentence_bert_config.json", "tokenizer.json", "tokenizer_config.json",
    "special_tokens_map.json", "vocab.txt", "model.safetensors",
    "1_Pooling/config.json",
)
GENERATOR_FILES = (
    "config.json", "generation_config.json", "tokenizer.json",
    "tokenizer_config.json", "special_tokens_map.json", "vocab.json",
    "merges.txt", "model.safetensors",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the selected local RAG models into the Hugging Face cache.")
    parser.add_argument("--generator-model", default=DEFAULT_GENERATOR_MODEL,
                        help="Answer model to cache; must match the value used with app.cli.")
    args = parser.parse_args()
    print("Downloading models into the local Hugging Face cache. This is needed only once.")
    # Qwen is downloaded first because it is the larger answer model and the
    # user may stop setup after verifying the core model is available.
    for step, (model_id, files) in enumerate(((args.generator_model, GENERATOR_FILES), (EMBEDDING_MODEL, EMBEDDING_FILES)), 1):
        print(f"\nStep {step} of 2: Downloading {model_id}...")
        path = snapshot_download(repo_id=model_id, allow_patterns=files)
        print(f"Ready: {path}")
    print("\nAll models are cached locally. You can now run: python -m app.cli")


if __name__ == "__main__":
    main()
