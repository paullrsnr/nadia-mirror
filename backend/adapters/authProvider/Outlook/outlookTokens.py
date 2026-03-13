from pydantic import BaseModel


class OutlookTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_at_timestamp: float
