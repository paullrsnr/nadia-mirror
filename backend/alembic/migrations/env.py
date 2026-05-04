import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from backend.adapters.bddProvider.sqlLite.models import Base
from backend.config.settings import storage_settings

target_metadata = Base.metadata

db_path = storage_settings.DATA_DIR / "emails.db"
db_url = f"sqlite:///{db_path}"
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
