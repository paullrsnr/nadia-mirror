from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'b7d9e1f3a2c4'
down_revision: Union[str, Sequence[str], None] = '1b2c3d4e5f6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('emails', sa.Column('is_starred', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('emails', 'is_starred')
