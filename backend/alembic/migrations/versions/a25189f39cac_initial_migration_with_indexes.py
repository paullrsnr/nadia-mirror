from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a25189f39cac'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS threads")
    op.execute("DROP TABLE IF EXISTS schema_version")

    with op.batch_alter_table('emails') as batch_op:
        batch_op.alter_column('id',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   nullable=False)
        batch_op.alter_column('thread_id',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   nullable=True)
        batch_op.alter_column('subject',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   existing_nullable=True)
        batch_op.alter_column('from_name',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   existing_nullable=True)
        batch_op.alter_column('from_email',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   nullable=False)
        batch_op.alter_column('date',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   existing_nullable=False)
        batch_op.alter_column('provider',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   nullable=False,
                   existing_server_default=sa.text("'gmail'"))
        batch_op.drop_index('idx_date')
        batch_op.drop_index('idx_from_email')
        batch_op.drop_index('idx_thread_id')
        batch_op.create_index('ix_emails_date', ['date'], unique=False)
        batch_op.create_index('ix_emails_from_email', ['from_email'], unique=False)
        batch_op.create_index('ix_emails_thread_id', ['thread_id'], unique=False)
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    with op.batch_alter_table('sync_metadata') as batch_op:
        batch_op.alter_column('id',
                   existing_type=sa.INTEGER(),
                   nullable=False,
                   autoincrement=True)
        batch_op.alter_column('last_sync_time',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   nullable=False)
        batch_op.alter_column('sync_count',
                   existing_type=sa.INTEGER(),
                   nullable=False,
                   existing_server_default=sa.text('0'))


def downgrade() -> None:
    with op.batch_alter_table('sync_metadata') as batch_op:
        batch_op.alter_column('sync_count',
                   existing_type=sa.INTEGER(),
                   nullable=True,
                   existing_server_default=sa.text('0'))
        batch_op.alter_column('last_sync_time',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   nullable=True)
        batch_op.alter_column('id',
                   existing_type=sa.INTEGER(),
                   nullable=True,
                   autoincrement=True)

    with op.batch_alter_table('emails') as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.TEXT(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.TEXT(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
        batch_op.drop_index('ix_emails_thread_id')
        batch_op.drop_index('ix_emails_from_email')
        batch_op.drop_index('ix_emails_date')
        batch_op.create_index('idx_thread_id', ['thread_id'], unique=False)
        batch_op.create_index('idx_from_email', ['from_email'], unique=False)
        batch_op.create_index('idx_date', ['date'], unique=False)
        batch_op.alter_column('provider',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   nullable=True,
                   existing_server_default=sa.text("'gmail'"))
        batch_op.alter_column('date',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   existing_nullable=False)
        batch_op.alter_column('from_email',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   nullable=True)
        batch_op.alter_column('from_name',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   existing_nullable=True)
        batch_op.alter_column('subject',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   existing_nullable=True)
        batch_op.alter_column('thread_id',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   nullable=False)
        batch_op.alter_column('id',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   nullable=True)

    op.create_table('schema_version',
        sa.Column('version', sa.INTEGER(), nullable=True),
        sa.Column('applied_at', sa.TEXT(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('version')
    )
    op.create_table('threads',
        sa.Column('thread_id', sa.TEXT(), nullable=True),
        sa.Column('subject', sa.TEXT(), nullable=True),
        sa.Column('last_message_date', sa.TEXT(), nullable=True),
        sa.Column('unread_count', sa.INTEGER(), server_default=sa.text('0'), nullable=True),
        sa.Column('updated_at', sa.TEXT(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('thread_id')
    )
