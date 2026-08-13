import json
import logging
import re
from pathlib import Path

from backend.core.models.llm import LLMStatusResponse, InstalledModelResponse, CatalogModelResponse, SummarizeRequest, SummarizeResponse, SummarizeThreadRequest, ClassifyEmailRequest
from backend.core.services.llm.download import get_models_dir
from backend.core.services.llm.catalog import CATALOG, get_catalog_model
from backend.core.services.llm.preferences import save_selected_model_id, load_selected_model_id
from backend.config.settings import llm_settings
from backend.core.categories import EMAIL_CATEGORIES
from backend.core.archiveDecision import ArchiveDecision
from backend.core.services.llm.prompts import EMAIL_SUMMARIZER, THREAD_SUMMARIZER, EMAIL_CLASSIFIER, EMAIL_IMPORTANCE_SCORER, REPLY_DRAFTER, AUTO_ARCHIVE_EVALUATOR
from backend.ports.llm import LlmPort
from backend.core.models.llm import ChatMessage, ChatRole

logger = logging.getLogger(__name__)


class LlmService:

    def __init__(self, llm_adapter: LlmPort):
        self._adapter = llm_adapter
        self._selected_model_id: str | None = None

    def get_status(self) -> LLMStatusResponse:
        models_dir = get_models_dir()
        installed = self._list_installed_models(models_dir)

        loaded_path = self._adapter.get_loaded_model_path()
        resolved_path = str(loaded_path) if loaded_path else None

        return LLMStatusResponse(
            available=self._adapter.is_available(),
            message="LLM disponible" if self._adapter.is_available() else "LLM non disponible",
            resolved_model_path=resolved_path,
            resolved_model_exists=loaded_path.exists() if loaded_path else None,
            resources_path=str(models_dir),
            selected_model_id=self._selected_model_id,
            installed_models=installed,
        )

    def get_catalog(self) -> list[CatalogModelResponse]:
        return [
            CatalogModelResponse(
                id=m.id,
                name=m.name,
                repo=m.repo,
                filename=m.filename,
                description=m.description,
                category=m.category,
            )
            for m in CATALOG
        ]

    def load_model_by_id(self, model_id: str) -> dict:
        models_dir = get_models_dir()

        catalog_model = get_catalog_model(model_id)
        if catalog_model:
            model_path = models_dir / catalog_model.filename
        else:
            model_path = models_dir / f"{model_id}.gguf"
            if not model_path.exists():
                model_path = models_dir / model_id

        if not model_path.exists():
            logger.error("Modèle introuvable: %s (cherché à %s)", model_id, model_path)
            raise ValueError(f"Modèle introuvable: {model_id}")

        success = self._load_model_from_path(model_path)
        if not success:
            raise ValueError("Impossible de charger le modèle")

        return {"model_id": model_id, "message": "Modèle chargé"}

    def unload_model(self) -> None:
        self._adapter.unload_model()
        self._selected_model_id = None

    def _list_installed_models(self, models_dir: Path) -> list[InstalledModelResponse]:
        installed = []
        if models_dir.exists():
            for f in models_dir.glob("*.gguf"):
                model_id = f.stem
                installed.append(
                    InstalledModelResponse(id=model_id, name=f.name, path=str(f))
                )
        return installed

    def summarize_email(self, payload: SummarizeRequest) -> SummarizeResponse:
        if not self._adapter.is_loaded():
            raise ValueError("Aucun modèle LLM chargé")
        try:
            messages = [
                EMAIL_SUMMARIZER,
                ChatMessage(
                    role=ChatRole.USER,
                    content=(
                        f"Résume cet email en 2-3 phrases :\n\n"
                        f"De : {payload.from_address}\n"
                        f"Objet : {payload.subject}\n\n"
                        f"{payload.body[:1200]}"
                    ),
                ),
            ]
            return SummarizeResponse(summary=self._adapter.get_short_answer(messages))
        except Exception as exc:
            raise ValueError(f"Erreur lors du résumé : {exc}") from exc

    def analyze_email_category(self, payload: ClassifyEmailRequest) -> str:
        if not self._adapter.is_loaded():
            raise ValueError("Aucun modèle LLM chargé")
        try:
            messages = [
                EMAIL_CLASSIFIER,
                ChatMessage(
                    role=ChatRole.USER,
                    content=(
                        f"De : {payload.from_address}\n"
                        f"Objet : {payload.subject}\n\n"
                        f"{payload.snippet[:400]}"
                    ),
                ),
            ]
            raw = self._adapter.get_short_answer(messages).strip().lower()
        except Exception as exc:
            raise ValueError(f"Erreur lors de la classification : {exc}") from exc
        for cat in EMAIL_CATEGORIES:
            if cat in raw:
                return cat
        return "autre"

    def summarize_thread(self, payload: SummarizeThreadRequest) -> SummarizeResponse:
        if not self._adapter.is_loaded():
            raise ValueError("Aucun modèle LLM chargé")
        try:
            thread_text = "\n\n---\n\n".join(
                f"De : {msg.from_address}\nDate : {msg.date}\n\n{msg.body[:600]}"
                for msg in payload.messages
            )
            messages = [
                THREAD_SUMMARIZER,
                ChatMessage(
                    role=ChatRole.USER,
                    content=(
                        f"Résume cette discussion email :\n\n"
                        f"Objet : {payload.subject}\n\n"
                        f"{thread_text}"
                    ),
                ),
            ]
            return SummarizeResponse(summary=self._adapter.get_short_answer(messages))
        except Exception as exc:
            raise ValueError(f"Erreur lors du résumé de fil : {exc}") from exc

    def is_important(self, subject: str, snippet: str, from_address: str) -> bool:
        if not self._adapter.is_loaded():
            raise ValueError("Aucun modèle LLM chargé")
        try:
            messages = [
                EMAIL_IMPORTANCE_SCORER,
                ChatMessage(
                    role=ChatRole.USER,
                    content=f"De : {from_address}\nObjet : {subject}\n\n{snippet[:400]}",
                ),
            ]
            raw = self._adapter.get_json_answer(messages)
        except Exception as exc:
            raise ValueError(f"Erreur lors du scoring d'importance : {exc}") from exc

        return self._parse_importance(raw)

    @staticmethod
    def _parse_importance(raw: str) -> bool:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"Réponse d'importance non JSON : {raw!r}")
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Réponse d'importance JSON invalide : {raw!r}") from exc
        value = data.get("important")
        if not isinstance(value, bool):
            raise ValueError(f"Champ 'important' absent ou non booléen : {raw!r}")
        return value

    def draft_reply(self, subject: str, body: str, from_address: str) -> str:
        if not self._adapter.is_loaded():
            raise ValueError("Aucun modèle LLM chargé")
        try:
            messages = [
                REPLY_DRAFTER,
                ChatMessage(
                    role=ChatRole.USER,
                    content=f"De : {from_address}\nObjet : {subject}\n\n{body[:1200]}",
                ),
            ]
            return self._adapter.get_short_answer(messages).strip()
        except Exception as exc:
            raise ValueError(f"Erreur lors de la rédaction du brouillon : {exc}") from exc

    def evaluate_archive_decision(self, rules: str, subject: str, snippet: str, from_address: str) -> ArchiveDecision:
        if not self._adapter.is_loaded():
            raise ValueError("Aucun modèle LLM chargé")
        try:
            messages = [
                AUTO_ARCHIVE_EVALUATOR,
                ChatMessage(
                    role=ChatRole.USER,
                    content=(
                        f"Règles d'archivage : {rules}\n\n"
                        f"Email à évaluer :\n"
                        f"De : {from_address}\n"
                        f"Objet : {subject}\n\n"
                        f"{snippet[:400]}"
                    ),
                ),
            ]
            raw = self._adapter.get_short_answer(messages).strip().lower()
        except Exception as exc:
            raise ValueError(f"Erreur lors de l'évaluation d'archivage : {exc}") from exc
        if raw == ArchiveDecision.YES:
            return ArchiveDecision.YES
        if raw == ArchiveDecision.NO:
            return ArchiveDecision.NO
        return ArchiveDecision.UNCERTAIN

    def _load_model_from_path(self, model_path: Path) -> bool:
        success = self._adapter.load_model(model_path)
        if success:
            self._selected_model_id = model_path.stem
            save_selected_model_id(self._selected_model_id)
        return success

    def auto_load_last_model(self) -> None:
        model_id = load_selected_model_id() or llm_settings.DEFAULT_MODEL_ID
        if not model_id:
            return
        try:
            self.load_model_by_id(model_id)
        except ValueError as exc:
            logger.warning("Chargement automatique du modèle '%s' impossible: %s", model_id, exc)
