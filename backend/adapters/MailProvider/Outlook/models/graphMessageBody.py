from pydantic import BaseModel, Field, ConfigDict


class GraphMessageBody(BaseModel):
    content_type: str = Field(default="text", alias="contentType")
    content: str = ""

    model_config = ConfigDict(populate_by_name=True)
