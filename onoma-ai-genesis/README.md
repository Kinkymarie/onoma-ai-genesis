# Onoma AI Genesis MVP

A runnable first implementation of the Onoma AI platform specification.

## Included

- Onoma-branded desktop-style web interface
- FastAPI backend
- Workspace and project management
- Persistent project memory
- Document ingestion and full-text search
- Agent registry
- Model-router abstraction
- Command bar and unified chat endpoint
- SQLite persistence
- Audit events

## Run

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Current boundary

This is an operational MVP, not the complete final Onoma platform. External AI providers are represented by a provider-neutral router and deterministic local fallback. Add authorized model-provider adapters through `app/services.py`.
