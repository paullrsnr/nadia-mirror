"""Remplace la colonne category (string) par une table categories + FK category_id."""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = 'f9c4d3e2b1a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CATEGORIES = ["travail", "personnel", "finance", "shopping", "marketing", "notification", "autre"]


def upgrade() -> None:
    # 1. Créer la table categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # 2. Insérer les catégories standard
    categories_table = sa.table("categories", sa.column("name", sa.String()))
    op.bulk_insert(categories_table, [{"name": n} for n in _CATEGORIES])

    # 3. Ajouter category_id sur emails (nullable)
    op.add_column("emails", sa.Column("category_id", sa.Integer(), nullable=True))

    # 4. Migrer les données existantes
    op.execute(
        "UPDATE emails SET category_id = ("
        "  SELECT id FROM categories WHERE categories.name = emails.category"
        ") WHERE emails.category IS NOT NULL"
    )

    # 5. Supprimer l'ancienne colonne category (batch pour SQLite)
    with op.batch_alter_table("emails") as batch_op:
        batch_op.drop_column("category")
        batch_op.create_foreign_key("fk_emails_category_id", "categories", ["category_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("emails") as batch_op:
        batch_op.drop_constraint("fk_emails_category_id", type_="foreignkey")
        batch_op.add_column(sa.Column("category", sa.String(), nullable=True))

    op.execute(
        "UPDATE emails SET category = ("
        "  SELECT name FROM categories WHERE categories.id = emails.category_id"
        ") WHERE emails.category_id IS NOT NULL"
    )

    with op.batch_alter_table("emails") as batch_op:
        batch_op.drop_column("category_id")

    op.drop_table("categories")
