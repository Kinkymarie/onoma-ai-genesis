# Database foundation

`database/schema.sql` is the canonical PostgreSQL initial schema. It defines
the relational core for identity, organizations, workspaces, project
collaboration, agents, automation, memory, knowledge graphs, search, API keys,
integrations, audit, billing, usage, and notifications. UUID foreign keys,
uniqueness/check constraints, deletion behavior, and query indexes are part of
the schema. JSONB is reserved for user-defined configuration and event data;
the core relationships remain relational.

The schema requires PostgreSQL with the `pgcrypto` and `vector` extensions
available. Embeddings use pgvector's `vector(1536)` type and cosine HNSW
indexes. Configure the extension in the database environment before applying
the migration if the database role cannot create extensions.

Apply the initial migration from the repository root with:

```sh
psql "$DATABASE_URL" -f database/migrations/001_initial.sql
```

`prisma/schema.prisma` describes the same tables and relations for Prisma
clients. Prisma does not model PostgreSQL check constraints, partial indexes,
or pgvector indexes, so those remain in the SQL migration. The two embedding
fields are represented as `Unsupported("vector(1536)")` and need raw SQL for
vector operations.

The 2FA seed and integration credentials are opaque `bytea`/`Bytes` values.
Encrypt them with an application-managed key before persistence; do not store
plaintext secrets in these fields.

## Current runtime boundary

The included FastAPI MVP currently persists projects, memories, documents, and
audit events in SQLite (`backend/app/db.py`). The PostgreSQL migration and
Prisma models are a separate database foundation; the MVP does not yet connect
its API routes to PostgreSQL, implement account authentication, or expose CRUD
routes for every schema model.
