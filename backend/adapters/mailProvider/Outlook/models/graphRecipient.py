from pydantic import BaseModel, Field, ConfigDict

from backend.adapters.mailProvider.Outlook.models.graphEmailAddress import GraphEmailAddress


class GraphRecipient(BaseModel):
    email_address: GraphEmailAddress = Field(alias="emailAddress")

    model_config = ConfigDict(populate_by_name=True)
