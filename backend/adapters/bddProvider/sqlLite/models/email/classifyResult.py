from pydantic import BaseModel


class ClassifyResult(BaseModel):
    email_id: str
    category: str
