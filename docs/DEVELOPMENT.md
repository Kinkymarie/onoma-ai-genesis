# Development Guide

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Layout
`config/` settings · `models/schemas.py` Pydantic models · `db/repositories.py` data access ·
`auth/` JWT, bcrypt, TOTP, OAuth, RBAC · `services/` business logic (enforces workspace access) ·
`routes/` HTTP API · `ai/` providers, embeddings, agents, RAG, tools · `middleware/` · `jobs/` · `utils/`.

## Storage
Repositories are in-memory by default (data is lost on restart). To use PostgreSQL, implement
`BaseRepository` on SQLAlchemy (see `requirements.txt`) and wire it into `Repositories`.

## AI providers
`DEFAULT_PROVIDER` selects `openai`, `anthropic`, `local` (OpenAI-compatible server such as Ollama) or `echo`.
When the selected cloud provider has no API key, the offline `echo` provider is used and a warning is logged.

## Production
Set `ENVIRONMENT=production` and `JWT_SECRET_KEY` (startup fails otherwise). The in-memory token blacklist and
rate limiter are per-process; use a single worker or back them with Redis for multi-worker deployments.
Run with `docker compose -f docker-compose.prod.yml up -d` (nginx fronts the API).
