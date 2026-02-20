# pylint: disable=invalid-name
"""Service de téléchargement de modèles LLM depuis HuggingFace."""
import asyncio
import json
import logging
import queue
import threading
from typing import AsyncGenerator

import httpx

from backend.core.services.llm.llmPaths import get_resources_dir

logger = logging.getLogger(__name__)


def _download_streaming_into_queue(repo: str, filename: str, progress_queue: "queue.Queue") -> None:
    """Télécharge un modèle en stream et envoie (loaded, total) ou ('done', path) ou ('error', msg) dans la queue."""
    resources_dir = get_resources_dir()
    resources_dir.mkdir(parents=True, exist_ok=True)
    dest = resources_dir / filename
    if dest.exists():
        logger.info("Modèle déjà présent: %s", dest)
        progress_queue.put(("done", str(dest)))
        return
    url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=60.0) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0) or 0)
            loaded = 0
            chunk_size = 1024 * 512  # 512 KB
            with open(dest, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=chunk_size):
                    f.write(chunk)
                    loaded += len(chunk)
                    progress_queue.put((loaded, total if total else loaded))
            progress_queue.put(("done", str(dest)))
    except Exception as e:
        logger.exception("Erreur téléchargement streaming: %s", e)
        if dest.exists():
            dest.unlink()
        progress_queue.put(("error", str(e)))


async def stream_download_sse(repo: str, filename: str) -> AsyncGenerator[str, None]:
    """Génère des événements SSE (data: {...}\\n\\n) pour la progression du téléchargement."""
    progress_queue = queue.Queue()
    loop = asyncio.get_running_loop()
    thread = threading.Thread(target=_download_streaming_into_queue, args=(repo, filename, progress_queue))
    thread.start()
    while True:
        item = await loop.run_in_executor(None, progress_queue.get)
        if item[0] == "done":
            yield f"data: {json.dumps({'done': True, 'path': item[1]})}\n\n"
            break
        if item[0] == "error":
            yield f"data: {json.dumps({'error': item[1]})}\n\n"
            break
        loaded, total = item
        percent = round(loaded / total * 100, 1) if total and total > 0 else 0
        yield f"data: {json.dumps({'loaded': loaded, 'total': total, 'percent': percent})}\n\n"
