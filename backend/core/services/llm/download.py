import json
import logging
from pathlib import Path
from typing import AsyncGenerator

from backend.config.settings import llm_settings

logger = logging.getLogger(__name__)


def get_models_dir() -> Path:
    models_dir = Path(llm_settings.MODELS_DIR)
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


async def stream_download_sse(repo: str, filename: str) -> AsyncGenerator[str, None]:
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        yield f"data: {json.dumps({'error': 'huggingface_hub non installé'})}\n\n"
        return

    models_dir = get_models_dir()
    target_path = models_dir / filename

    if target_path.exists():
        yield f"data: {json.dumps({'status': 'exists', 'path': str(target_path)})}\n\n"
        return

    yield f"data: {json.dumps({'status': 'starting', 'repo': repo, 'filename': filename})}\n\n"

    try:
        downloaded_path = hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir=str(models_dir),
        )

        yield f"data: {json.dumps({'status': 'completed', 'path': downloaded_path})}\n\n"

    except Exception as e:
        logger.exception("Erreur de téléchargement: %s", e)
        yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
