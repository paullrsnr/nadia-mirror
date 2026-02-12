# pylint: disable=invalid-name
"""V001 : schéma initial (emails + sync_metadata + index)."""
import sqlite3


def up(conn: sqlite3.Connection) -> None:
    """Crée les tables et index initiaux."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            thread_id TEXT NOT NULL,
            subject TEXT,
            from_name TEXT,
            from_email TEXT,
            to_addresses TEXT,
            cc_addresses TEXT,
            bcc_addresses TEXT,
            date TEXT NOT NULL,
            body_text TEXT,
            body_html TEXT,
            attachments TEXT,
            labels TEXT,
            snippet TEXT,
            provider TEXT DEFAULT 'gmail',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_sync_time TEXT,
            sync_count INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_thread_id ON emails(thread_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON emails(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_provider ON emails(provider)")
