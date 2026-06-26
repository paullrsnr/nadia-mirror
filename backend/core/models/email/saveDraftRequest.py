from dataclasses import dataclass, field


@dataclass
class SaveDraftRequest:
    provider: str
    subject: str = ""
    body_text: str = ""
    body_html: str = ""
    to: list[str] = field(default_factory=list)
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    in_reply_to_email_id: str | None = None
