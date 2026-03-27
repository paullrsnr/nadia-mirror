from pathlib import Path

from dotenv import load_dotenv

from backend.config.settings.auth import AuthSettings
from backend.config.settings.storage import StorageSettings
from backend.config.settings.email import EmailSettings
from backend.config.settings.api import ApiSettings
from backend.config.settings.llm import LlmSettings

load_dotenv(Path(__file__).parent.parent.parent / ".env")

auth_settings = AuthSettings()
storage_settings = StorageSettings()
email_settings = EmailSettings()
api_settings = ApiSettings()
llm_settings = LlmSettings()
