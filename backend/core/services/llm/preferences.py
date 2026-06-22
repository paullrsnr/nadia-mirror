from pathlib import Path

from backend.core.services.llm.download import get_models_dir

_SELECTED_MODEL_FILE = "selected_model.txt"


def save_selected_model_id(model_id: str) -> None:
    (get_models_dir() / _SELECTED_MODEL_FILE).write_text(model_id, encoding="utf-8")


def load_selected_model_id() -> str | None:
    path: Path = get_models_dir() / _SELECTED_MODEL_FILE
    if not path.exists():
        return None
    model_id = path.read_text(encoding="utf-8").strip()
    return model_id or None
