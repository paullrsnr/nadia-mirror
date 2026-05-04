from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c3e8f1a2b4d5'
down_revision: Union[str, Sequence[str], None] = 'a25189f39cac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('emails', sa.Column('category', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('emails', 'category')
