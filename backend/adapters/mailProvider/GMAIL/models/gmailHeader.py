from pydantic import BaseModel


class GmailHeader(BaseModel):
    name: str
    value: str
