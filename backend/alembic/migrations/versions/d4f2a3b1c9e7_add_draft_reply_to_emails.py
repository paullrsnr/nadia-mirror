from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd4f2a3b1c9e7'
down_revision: Union[str, Sequence[str], None] = 'c3e8f1a2b4d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('emails', sa.Column('draft_reply', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('emails', 'draft_reply')
