from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e8b3c2d1f5a6'
down_revision: Union[str, Sequence[str], None] = 'd4f2a3b1c9e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('emails', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('emails', 'is_archived')
