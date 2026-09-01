import json

from backend.core.models.email import EmailAddress


def to_json(addresses: list[EmailAddress]) -> str:
    return json.dumps([{"name": a.name, "email": a.email} for a in addresses])


def from_json(data: str | None) -> list[EmailAddress]:
    if not data or data == "null":
        return []
    return [EmailAddress(email=a["email"], name=a.get("name")) for a in json.loads(data)]
