# API Reference

Base URL: `/api`. Interactive docs: `/docs` (disabled when `ENVIRONMENT=production`).
All endpoints except `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/oauth/*` and `/health*`
require an `Authorization` header with a bearer access token.
Errors: `{"success": false, "error": {"code", "message"}}`.

Roles: `admin` (all), `member` (read/write/delete), `viewer` (read only). Workspace-scoped resources are only
accessible to the workspace owner, its members, and admins. The first registered user becomes `admin`.

| Area | Method & path | Notes |
|------|---------------|-------|
| Auth | `POST /auth/register` | Strong password required |
| | `POST /auth/login` | Optional `totp_code` |
| | `POST /auth/refresh` | Rotates refresh token |
| | `POST /auth/logout` | Revokes access (and optional refresh) token |
| | `GET /auth/me` | |
| | `POST /auth/password` | |
| | `POST /auth/2fa/setup`, `/2fa/confirm`, `/2fa/disable` | TOTP |
| | `GET /auth/oauth/{google\|github}/login`, `/callback` | Needs client id/secret |
| Users | `GET /users` (admin), `GET/PATCH/DELETE /users/{id}`, `PUT /users/{id}/role?role=` (admin) | |
| | `GET /users/me/notifications`, `POST /users/me/notifications/{id}/read` | |
| Organizations | `POST/GET /organizations`, `GET/PATCH/DELETE /organizations/{id}` | |
| Workspaces | `POST/GET /workspaces`, `GET/PATCH/DELETE /workspaces/{id}` | |
| | `POST /workspaces/{id}/members`, `DELETE /workspaces/{id}/members/{user_id}` | |
| Projects | `POST /projects`, `GET /projects?workspace_id=`, `GET/PATCH/DELETE /projects/{id}` | |
| Documents | `POST /documents`, `GET /documents?workspace_id=`, `GET/PATCH/DELETE /documents/{id}` | |
| Tasks | `POST /tasks`, `GET /tasks?workspace_id=&status=&project_id=`, `GET/PATCH/DELETE /tasks/{id}` | |
| Agents | `POST /agents`, `GET /agents?workspace_id=`, `GET/PATCH/DELETE /agents/{id}`, `GET /agents/tools` | |
| | `POST /agents/{id}/run` | `{input, max_steps}` |
| Automations | `POST /automations`, `GET /automations?workspace_id=`, `GET/PATCH/DELETE /automations/{id}` | |
| Memory | `POST /memory`, `GET /memory?workspace_id=`, `GET /memory/recall`, `DELETE /memory/{id}` | |
| | `POST /memory/entities`, `POST /memory/relationships`, `GET /memory/graph` | Knowledge graph |
| Search | `GET /search?workspace_id=&q=`, `GET /search/semantic` | |
| Chat | `POST /chat`, `POST /chat/stream` (SSE), `GET /chat/conversations`, `GET/DELETE /chat/conversations/{id}` | |
| Embeddings | `POST /embeddings` | `{texts: [...]}` |
| Audit | `GET /audit?user_id=&limit=` | admin only |
| Health | `GET /health`, `GET /health/ready` | unauthenticated |
