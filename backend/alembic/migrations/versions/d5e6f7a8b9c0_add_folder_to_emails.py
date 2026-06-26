"""Ajoute la colonne folder (inbox/sent) à emails pour distinguer les emails envoyés."""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("emails", sa.Column("folder", sa.String(), nullable=False, server_default="inbox"))


def downgrade() -> None:
    with op.batch_alter_table("emails") as batch_op:
        batch_op.drop_column("folder")
