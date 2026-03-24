import os
from pydantic_settings import BaseSettings


class LlmSettings(BaseSettings):
    DEFAULT_N_CTX: int = 2048
    DEFAULT_N_THREADS: int = 4
    AUTO_THREADS: bool = True
    MODELS_DIR: str = "resources/models"
    DEFAULT_MODEL_ID: str | None = None

    class Config:
        env_prefix = "LLM_"
        env_file = ".env"
        extra = "ignore"
