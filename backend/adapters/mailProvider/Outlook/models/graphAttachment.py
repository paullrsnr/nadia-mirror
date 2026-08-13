from pydantic import BaseModel, Field


class GraphAttachment(BaseModel):
    id: str = ""
    name: str = ""
    content_type: str = Field(default="application/octet-stream", alias="contentType")
    size: int = 0
