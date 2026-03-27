from dataclasses import dataclass, field

from backend.core.models.llm.installedModelResponse import InstalledModelResponse


@dataclass
class LLMStatusResponse:
    available: bool
    message: str
    resolved_model_path: str | None = None
    resolved_model_exists: bool | None = None
    resources_path: str | None = None
    selected_model_id: str | None = None
    installed_models: list[InstalledModelResponse] = field(default_factory=list)
