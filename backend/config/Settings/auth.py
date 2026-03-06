from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    # Gmail
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:3333/auth/callback/gmail"
    GMAIL_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    # Outlook
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_REDIRECT_URI: str = "http://localhost:3333/auth/callback/outlook"
    OUTLOOK_TENANT: str = "common"
    OUTLOOK_SCOPES: list[str] = [
        "https://graph.microsoft.com/Mail.Read",
        "https://graph.microsoft.com/Mail.ReadWrite",
        "https://graph.microsoft.com/User.Read",
        "offline_access",
    ]
    FRONTEND_AUTH_CALLBACK_URL: str = "http://localhost:5173/auth/callback"
