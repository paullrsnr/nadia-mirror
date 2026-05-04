from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'f9c4d3e2b1a7'
down_revision: Union[str, Sequence[str], None] = 'e8b3c2d1f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('emails', sa.Column('pending_archive', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('emails', 'pending_archive')
