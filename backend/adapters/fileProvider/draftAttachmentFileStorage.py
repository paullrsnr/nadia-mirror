import mimetypes
import shutil
import uuid
from pathlib import Path

from backend.config.settings import storage_settings
from backend.core.exceptions import NotFoundError
from backend.core.models.email import AttachmentContent, EmailAttachment
from backend.ports.attachmentStorage import AttachmentStorage


class DraftAttachmentFileStorage(AttachmentStorage):

    def _draft_dir(self, draft_id: str) -> Path:
        return storage_settings.DATA_DIR / "draft_attachments" / draft_id

    def _attachment_dir(self, draft_id: str, attachment_id: str) -> Path:
        return self._draft_dir(draft_id) / attachment_id

    def _find_file(self, draft_id: str, attachment_id: str) -> Path:
        attachment_dir = self._attachment_dir(draft_id, attachment_id)
        files = list(attachment_dir.glob("*")) if attachment_dir.is_dir() else []
        if not files:
            raise NotFoundError(f"Pièce jointe introuvable : {attachment_id}")
        return files[0]

    def save_attachment(self, draft_id: str, filename: str, content: bytes) -> EmailAttachment:
        attachment_id = str(uuid.uuid4())
        attachment_dir = self._attachment_dir(draft_id, attachment_id)
        attachment_dir.mkdir(parents=True, exist_ok=True)
        file_path = attachment_dir / filename
        file_path.write_bytes(content)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        return EmailAttachment(
            filename=filename,
            mime_type=mime_type,
            size=len(content),
            attachment_id=attachment_id,
        )

    def list_attachments(self, draft_id: str) -> list[EmailAttachment]:
        draft_dir = self._draft_dir(draft_id)
        if not draft_dir.is_dir():
            return []
        attachments = []
        for attachment_dir in sorted(draft_dir.iterdir()):
            files = list(attachment_dir.glob("*")) if attachment_dir.is_dir() else []
            if not files:
                continue
            file_path = files[0]
            mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            attachments.append(
                EmailAttachment(
                    filename=file_path.name,
                    mime_type=mime_type,
                    size=file_path.stat().st_size,
                    attachment_id=attachment_dir.name,
                )
            )
        return attachments

    def read_attachment(self, draft_id: str, attachment_id: str) -> AttachmentContent:
        file_path = self._find_file(draft_id, attachment_id)
        mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        return AttachmentContent(
            filename=file_path.name,
            mime_type=mime_type,
            content=file_path.read_bytes(),
        )

    def delete_attachment(self, draft_id: str, attachment_id: str) -> None:
        attachment_dir = self._attachment_dir(draft_id, attachment_id)
        shutil.rmtree(attachment_dir, ignore_errors=True)

    def delete_draft_attachments(self, draft_id: str) -> None:
        shutil.rmtree(self._draft_dir(draft_id), ignore_errors=True)
