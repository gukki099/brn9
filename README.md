# Hermes Agent

Minimal production-ready FastAPI JSON API for the Hermes agent. Messages are stored in Supabase Postgres. LLM logic (LangChain / LangGraph) can replace the dummy reply in `POST /chat` later.

## Stack

- Python 3.11
- FastAPI + Pydantic
- asyncpg (async Postgres)
- Deploy target: Render (paid, always-on)
- Database: Supabase Free Postgres

## API

| Method | Path | Body | Response |
| --- | --- | --- | --- |
| `GET` | `/health` | — | `{"status":"ok"}` |
| `POST` | `/chat` | `{"message":"...", "user_id": null}` | `{"reply":"..."}` |

`POST /chat` writes a `user` row and an `assistant` row to `messages`, then returns a dummy reply:

```text
Hermes received: <message>
```

Interactive docs: `http://127.0.0.1:8000/docs`

## Local setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set DATABASE_URL
python init_db.py
python run_local.py
```

Example request:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello","user_id":"demo"}'
```

## Database

`init_db.py` creates:

```sql
messages (
  id         BIGSERIAL PRIMARY KEY,
  user_id    TEXT,
  role       TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content    TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
```

Supabase connection notes:

- Use the **URI** from Project Settings → Database.
- SSL is required; this app enables `ssl=require` for `*.supabase.co` URLs.
- Prefer the **Session** pooler. The **Transaction** pooler (port `6543`) also works because `statement_cache_size=0`.
- Convert `postgres://` to `postgresql://` if needed; the app does this automatically.

## Deploy on Render

1. Push this repo to GitHub (or connect the local git remote Render uses).
2. In Render: **New → Web Service** → select the repo.
3. Settings:

   | Setting | Value |
   | --- | --- |
   | Runtime | Python 3 |
   | Instance | Paid / always-on |
   | Build command | `pip install -r requirements.txt` |
   | Start command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

4. Environment variables:

   | Key | Value |
   | --- | --- |
   | `DATABASE_URL` | Supabase pooler URI (with password) |
   | `PYTHON_VERSION` | `3.11.11` (or any 3.11.x Render supports) |

5. After the first deploy, run the schema once (Render Shell, or locally against the same `DATABASE_URL`):

   ```bash
   python init_db.py
   ```

6. Confirm:

   ```bash
   curl https://<your-service>.onrender.com/health
   ```

Render injects `PORT`. Do not hard-code a port in the start command.

## Extending with an LLM

Replace the dummy reply in `chat()` in `main.py` with a LangChain / LangGraph call. Keep the same request/response models and the `messages` inserts so conversation history stays in Postgres.
