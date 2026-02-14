"""Chargement du .env et instanciation des settings.

Module exécuté une seule fois à l'import : charge .env, crée les instances.
"""
from pathlib import Path

from dotenv import load_dotenv

from backend.config.Settings.authSettings import AuthSettings
from backend.config.Settings.storageSettings import StorageSettings
from backend.config.Settings.emailSettings import EmailSettings
from backend.config.Settings.apiSettings import ApiSettings

# Chargement du .env une seule fois
BACKEND_DIR = Path(__file__).parent.parent.parent
load_dotenv(BACKEND_DIR / ".env")

# Instances par domaine : chaque module importe la sienne
auth_settings = AuthSettings()
storage_settings = StorageSettings()
email_settings = EmailSettings()
api_settings = ApiSettings()
