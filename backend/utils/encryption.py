"""Utilitaires de chiffrement pour les données sensibles."""
import base64
import os

from cryptography.fernet import Fernet

from backend.config.settings import storage_settings


def get_encryption_key() -> bytes:
    """Retourne la clé Fernet persistée sur disque, en la créant si absente."""
    key_file = storage_settings.DATA_DIR / ".encryption_key"

    if key_file.exists():
        with open(key_file, "rb") as f:
            return f.read()

    # Première exécution : génération d'une clé aléatoire sécurisée
    key = Fernet.generate_key()

    storage_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(key_file, "wb") as f:
        f.write(key)

    os.chmod(key_file, 0o600)
    return key


def encrypt_data(data: str) -> str:
    """Chiffre une chaîne de caractères."""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    # Double-encodage base64 maintenu pour la compatibilité avec les tokens existants
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Déchiffre une chaîne de caractères."""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted = fernet.decrypt(encrypted_bytes)
    return decrypted.decode()
