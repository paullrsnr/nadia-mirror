from pydantic_settings import BaseSettings


class LlmSettings(BaseSettings):
    DEFAULT_N_CTX: int = 4096
    DEFAULT_N_THREADS: int = 4
    AUTO_THREADS: bool = False
    MODELS_DIR: str = "resources/models"
    DEFAULT_MODEL_ID: str | None = None
