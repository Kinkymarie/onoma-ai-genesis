# FastAPI MVP

This runnable MVP currently provides project and memory CRUD, text document
ingestion, full-text search, agent routing, chat orchestration, and audit
events. It uses SQLite locally; see [`../docs/DATABASE.md`](../docs/DATABASE.md)
for the separate PostgreSQL schema and Prisma foundation.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Interactive OpenAPI documentation is available
at `/docs`; health status is at `/api/health`.
