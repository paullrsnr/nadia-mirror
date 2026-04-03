"""Ajoute la table settings (clé/valeur) pour les paramètres applicatifs."""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '1b2c3d4e5f6a'
down_revision: Union[str, Sequence[str], None] = '0a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("settings")
