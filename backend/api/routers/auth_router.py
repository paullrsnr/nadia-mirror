from fastapi import APIRouter, HTTPException, Query
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import json
from pathlib import Path

from backend.config.settings import settings
from backend.api.schemas import AuthUrlResponse, AuthCallbackRequest, AuthStatusResponse

router = APIRouter()


def get_flow() -> Flow:
    """Crée le flux OAuth2 pour Gmail"""
    if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
        raise ValueError("GMAIL_CLIENT_ID et GMAIL_CLIENT_SECRET doivent être configurés")
    
    client_config = {
        "web": {
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GMAIL_REDIRECT_URI],
        }
    }
    
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=settings.GMAIL_SCOPES,
            redirect_uri=settings.GMAIL_REDIRECT_URI,
        )
        return flow
    except Exception as e:
        raise ValueError(f"Erreur lors de la création du flux OAuth2: {str(e)}")


def save_credentials(credentials: Credentials) -> None:
    """Sauvegarde les credentials de manière sécurisée"""
    from backend.utils.encryption import encrypt_data
    
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    creds_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    
    # Chiffrer les données sensibles
    encrypted_dict = {
        "token": encrypt_data(creds_dict["token"]) if creds_dict["token"] else None,
        "refresh_token": encrypt_data(creds_dict["refresh_token"]) if creds_dict["refresh_token"] else None,
        "token_uri": creds_dict["token_uri"],
        "client_id": creds_dict["client_id"],
        "client_secret": encrypt_data(creds_dict["client_secret"]) if creds_dict["client_secret"] else None,
        "scopes": creds_dict["scopes"],
    }
    
    with open(settings.TOKENS_FILE, "w") as f:
        json.dump(encrypted_dict, f)
    
    # Sécuriser le fichier (permissions restrictives)
    os.chmod(settings.TOKENS_FILE, 0o600)


def load_credentials() -> Credentials | None:
    """Charge les credentials sauvegardés"""
    from backend.utils.encryption import decrypt_data
    
    if not settings.TOKENS_FILE.exists():
        return None
    
    try:
        with open(settings.TOKENS_FILE, "r") as f:
            encrypted_dict = json.load(f)
        
        # Déchiffrer les données sensibles
        creds_dict = {
            "token": decrypt_data(encrypted_dict["token"]) if encrypted_dict.get("token") else None,
            "refresh_token": decrypt_data(encrypted_dict["refresh_token"]) if encrypted_dict.get("refresh_token") else None,
            "token_uri": encrypted_dict.get("token_uri"),
            "client_id": encrypted_dict.get("client_id"),
            "client_secret": decrypt_data(encrypted_dict["client_secret"]) if encrypted_dict.get("client_secret") else None,
            "scopes": encrypted_dict.get("scopes", []),
        }
        
        credentials = Credentials(
            token=creds_dict.get("token"),
            refresh_token=creds_dict.get("refresh_token"),
            token_uri=creds_dict.get("token_uri"),
            client_id=creds_dict.get("client_id"),
            client_secret=creds_dict.get("client_secret"),
            scopes=creds_dict.get("scopes"),
        )
        
        # Rafraîchir le token s'il est expiré
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_credentials(credentials)
        
        return credentials
    except Exception as e:
        print(f"Erreur lors du chargement des credentials: {e}")
        return None


@router.get("/url", response_model=AuthUrlResponse)
async def get_auth_url():
    """Génère l'URL d'authentification OAuth2"""
    try:
        if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Les identifiants OAuth2 de l'application ne sont pas configurés. Veuillez contacter le développeur de l'application.",
            )
        
        flow = get_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        
        return AuthUrlResponse(auth_url=auth_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de l'URL d'authentification: {str(e)}",
        )


@router.get("/callback")
async def auth_callback(code: str, state: str = None):
    """Traite le callback OAuth2 et sauvegarde les tokens"""
    try:
        flow = get_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        save_credentials(credentials)
        
        # Retourner une page HTML de succès qui peut fermer la fenêtre
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentification réussie</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                }
                .container {
                    text-align: center;
                    padding: 40px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #4CAF50; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Authentification réussie !</h1>
                <p>Vous pouvez fermer cette fenêtre et retourner à l'application.</p>
                <script>
                    // Fermer automatiquement la fenêtre après 2 secondes
                    setTimeout(() => {
                        window.close();
                    }, 2000);
                </script>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        error_msg = str(e)
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erreur d'authentification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                }}
                .container {{
                    text-align: center;
                    padding: 40px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #f44336; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✗ Erreur d'authentification</h1>
                <p>{error_msg}</p>
                <p>Veuillez réessayer.</p>
            </div>
        </body>
        </html>
        """, 400


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status():
    """Vérifie le statut d'authentification"""
    credentials = load_credentials()
    
    if not credentials:
        return AuthStatusResponse(is_authenticated=False)
    
    # Vérifier si les credentials sont valides
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            save_credentials(credentials)
        except Exception:
            return AuthStatusResponse(is_authenticated=False)
    
    # Récupérer l'email de l'utilisateur depuis Gmail API
    try:
        from googleapiclient.discovery import build
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        user_email = profile.get("emailAddress")
        return AuthStatusResponse(is_authenticated=True, email=user_email)
    except Exception:
        return AuthStatusResponse(is_authenticated=True, email=None)


@router.post("/logout")
async def logout():
    """Déconnecte l'utilisateur en supprimant les tokens"""
    if settings.TOKENS_FILE.exists():
        settings.TOKENS_FILE.unlink()
    return {"status": "success", "message": "Déconnexion réussie"}


def get_credentials() -> Credentials | None:
    """Fonction utilitaire pour récupérer les credentials (pour les autres modules)"""
    return load_credentials()
