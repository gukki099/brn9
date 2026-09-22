import os
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

pool: Optional[asyncpg.Pool] = None

INSERT_MESSAGE_SQL = """
INSERT INTO messages (user_id, role, content)
VALUES ($1, $2, $3)
"""


def normalize_dsn(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


def connect_kwargs(dsn: str) -> dict:
    needs_ssl = (
        "supabase.co" in dsn
        or os.getenv("DATABASE_SSL", "").lower() in ("1", "true", "require")
    )
    return {
        "dsn": dsn,
        "statement_cache_size": 0,
        "ssl": "require" if needs_ssl else None,
    }


def pool_kwargs(dsn: str) -> dict:
    return {
        **connect_kwargs(dsn),
        "min_size": 1,
        "max_size": 5,
    }


async def get_pool() -> asyncpg.Pool:
    if pool is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    return pool


async def create_db_pool() -> asyncpg.Pool:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required")
    return await asyncpg.create_pool(**pool_kwargs(normalize_dsn(url)))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global pool
    pool = await create_db_pool()
    try:
        yield
    finally:
        await pool.close()
        pool = None


app = FastAPI(
    title="Hermes Agent",
    version="0.1.0",
    description="JSON API for the Hermes agent. LLM logic can be plugged into /chat later.",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


class HealthResponse(BaseModel):
    status: str


@app.get("/", response_model=dict)
async def root() -> dict:
    return {
        "name": "Hermes Agent",
        "status": "online",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    db = await get_pool()
    reply = f"Hermes received: {body.message}"
    async with db.acquire() as conn:
        async with conn.transaction():
            await conn.execute(INSERT_MESSAGE_SQL, body.user_id, "user", body.message)
            await conn.execute(INSERT_MESSAGE_SQL, body.user_id, "assistant", reply)
    return ChatResponse(reply=reply)
