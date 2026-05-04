from pydantic import BaseModel


class AutoArchiveConfig(BaseModel):
    rules: str
    enabled: bool
