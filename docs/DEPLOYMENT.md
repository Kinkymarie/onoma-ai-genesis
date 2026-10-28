# Deployment

1. Copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL`, `JWT_SECRET` (long random value) and provider keys.
2. Local: `docker compose up --build` (PostgreSQL + Redis + backend; migrations run on start).
3. Single host: set `POSTGRES_PASSWORD`, then `docker compose -f docker-compose.prod.yml up -d`. Issue certificates with certbot and extend `infrastructure/nginx.conf` with a TLS server block.
4. Kubernetes: create secrets (`infrastructure/k8s/secrets.yaml` is a template; never commit values), then apply the manifests in `infrastructure/k8s/`. The `deploy.yml` workflow applies them using the `KUBE_CONFIG` secret.
5. AWS: `cd infrastructure/terraform && terraform init && terraform apply -var db_password=... -var image=...`.
6. Migrations: `cd backend && alembic upgrade head`.

Health: `/api/health`, `/api/health/db`. Metrics: `/metrics`.
