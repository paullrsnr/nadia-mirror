"""Ajoute la colonne body_html à email_drafts pour le corps enrichi (HTML) des brouillons."""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, Sequence[str], None] = 'd5e6f7a8b9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("email_drafts", sa.Column("body_html", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("email_drafts") as batch_op:
        batch_op.drop_column("body_html")
