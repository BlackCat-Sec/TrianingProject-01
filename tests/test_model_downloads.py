from app.download_models import EMBEDDING_FILES, GENERATOR_FILES


def test_predownload_allowlists_exclude_unused_model_variants():
    selected = " ".join((*EMBEDDING_FILES, *GENERATOR_FILES)).lower()
    assert "onnx" not in selected
    assert "openvino" not in selected
    assert "avx" not in selected
    assert "arm" not in selected


def test_predownload_includes_required_weight_files():
    assert "model.safetensors" in EMBEDDING_FILES
    assert "model.safetensors" in GENERATOR_FILES
