"""Create the messages table used by Hermes Agent.

Usage:
  python init_db.py
"""

import asyncio
import os

import asyncpg
from dotenv import load_dotenv

from main import connect_kwargs, normalize_dsn

CREATE_MESSAGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id           BIGSERIAL PRIMARY KEY,
    user_id      TEXT,
    role         TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content      TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS messages_user_id_created_at_idx
    ON messages (user_id, created_at DESC);
"""


async def init_db() -> None:
    load_dotenv()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required")

    conn = await asyncpg.connect(**connect_kwargs(normalize_dsn(url)))
    try:
        await conn.execute(CREATE_MESSAGES_TABLE_SQL)
        print("messages table is ready")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_db())
