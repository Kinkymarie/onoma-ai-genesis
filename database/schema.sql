CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE user_status AS ENUM ('ACTIVE', 'INVITED', 'SUSPENDED', 'DELETED');
CREATE TYPE organization_role AS ENUM ('OWNER', 'ADMIN', 'MEMBER', 'GUEST');
CREATE TYPE project_status AS ENUM ('ACTIVE', 'ARCHIVED', 'DELETED');
CREATE TYPE task_status AS ENUM ('TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED');
CREATE TYPE task_priority AS ENUM ('LOW', 'NORMAL', 'HIGH', 'URGENT');
CREATE TYPE agent_status AS ENUM ('DRAFT', 'ACTIVE', 'PAUSED', 'ARCHIVED');
CREATE TYPE automation_status AS ENUM ('DRAFT', 'ACTIVE', 'PAUSED', 'ARCHIVED');
CREATE TYPE automation_run_status AS ENUM ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED');
CREATE TYPE memory_kind AS ENUM ('SESSION', 'PROJECT', 'DOCUMENT', 'RESEARCH', 'WORKFLOW', 'PREFERENCE');
CREATE TYPE integration_status AS ENUM ('PENDING', 'CONNECTED', 'ERROR', 'DISCONNECTED');
CREATE TYPE subscription_status AS ENUM ('TRIALING', 'ACTIVE', 'PAST_DUE', 'CANCELLED', 'EXPIRED');
CREATE TYPE notification_status AS ENUM ('UNREAD', 'READ', 'ARCHIVED');

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    display_name text NOT NULL,
    status user_status NOT NULL DEFAULT 'ACTIVE',
    email_verified_at timestamptz,
    two_factor_secret bytea,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    deleted_at timestamptz
);

CREATE TABLE sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash text NOT NULL UNIQUE,
    expires_at timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX sessions_user_expiry_idx ON sessions(user_id, expires_at);

CREATE TABLE user_preferences (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_key text NOT NULL,
    value jsonb NOT NULL DEFAULT '{}'::jsonb,
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(user_id, preference_key)
);

CREATE TABLE organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    slug text NOT NULL UNIQUE,
    settings jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE organization_members (
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role organization_role NOT NULL DEFAULT 'MEMBER',
    joined_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (organization_id, user_id)
);
CREATE INDEX organization_members_user_idx ON organization_members(user_id, organization_id);

CREATE TABLE workspaces (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name text NOT NULL,
    slug text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(organization_id, slug)
);
CREATE TABLE workspace_members (
    workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role organization_role NOT NULL DEFAULT 'MEMBER',
    joined_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (workspace_id, user_id)
);
CREATE INDEX workspace_members_user_idx ON workspace_members(user_id, workspace_id);

CREATE TABLE projects (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    created_by uuid REFERENCES users(id) ON DELETE SET NULL,
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    status project_status NOT NULL DEFAULT 'ACTIVE',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX projects_workspace_status_idx ON projects(workspace_id, status);

CREATE TABLE documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_by uuid REFERENCES users(id) ON DELETE SET NULL,
    name text NOT NULL,
    media_type text NOT NULL DEFAULT 'text/plain',
    content text NOT NULL DEFAULT '',
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX documents_project_updated_idx ON documents(project_id, updated_at DESC);
CREATE TABLE document_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number integer NOT NULL CHECK (version_number > 0),
    content text NOT NULL,
    created_by uuid REFERENCES users(id) ON DELETE SET NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(document_id, version_number)
);
CREATE TABLE notes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_by uuid REFERENCES users(id) ON DELETE SET NULL,
    title text NOT NULL,
    content text NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE tasks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_by uuid REFERENCES users(id) ON DELETE SET NULL,
    assigned_to uuid REFERENCES users(id) ON DELETE SET NULL,
    title text NOT NULL,
    description text NOT NULL DEFAULT '',
    status task_status NOT NULL DEFAULT 'TODO',
    priority task_priority NOT NULL DEFAULT 'NORMAL',
    due_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX tasks_project_status_idx ON tasks(project_id, status);
CREATE INDEX tasks_assignee_status_idx ON tasks(assigned_to, status);

CREATE TABLE agents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    agent_key text NOT NULL,
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    configuration jsonb NOT NULL DEFAULT '{}'::jsonb,
    status agent_status NOT NULL DEFAULT 'DRAFT',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(organization_id, agent_key)
);
CREATE TABLE agent_instances (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id uuid REFERENCES users(id) ON DELETE SET NULL,
    project_id uuid REFERENCES projects(id) ON DELETE SET NULL,
    state jsonb NOT NULL DEFAULT '{}'::jsonb,
    started_at timestamptz NOT NULL DEFAULT now(),
    ended_at timestamptz
);
CREATE INDEX agent_instances_agent_started_idx ON agent_instances(agent_id, started_at DESC);

CREATE TABLE automations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by uuid REFERENCES users(id) ON DELETE SET NULL,
    name text NOT NULL,
    trigger_config jsonb NOT NULL DEFAULT '{}'::jsonb,
    definition jsonb NOT NULL DEFAULT '{}'::jsonb,
    status automation_status NOT NULL DEFAULT 'DRAFT',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE automation_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    automation_id uuid NOT NULL REFERENCES automations(id) ON DELETE CASCADE,
    triggered_by uuid REFERENCES users(id) ON DELETE SET NULL,
    status automation_run_status NOT NULL DEFAULT 'QUEUED',
    input jsonb NOT NULL DEFAULT '{}'::jsonb,
    output jsonb,
    error text,
    started_at timestamptz,
    finished_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX automation_runs_history_idx ON automation_runs(automation_id, created_at DESC);

CREATE TABLE memory_stores (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    workspace_id uuid REFERENCES workspaces(id) ON DELETE CASCADE,
    owner_id uuid REFERENCES users(id) ON DELETE CASCADE,
    name text NOT NULL,
    settings jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (num_nonnulls(organization_id, workspace_id, owner_id) = 1)
);
CREATE TABLE memory_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_store_id uuid NOT NULL REFERENCES memory_stores(id) ON DELETE CASCADE,
    project_id uuid REFERENCES projects(id) ON DELETE CASCADE,
    kind memory_kind NOT NULL DEFAULT 'PROJECT',
    content text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(1536),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX memory_items_store_created_idx ON memory_items(memory_store_id, created_at DESC);
CREATE INDEX memory_items_embedding_idx ON memory_items USING hnsw (embedding vector_cosine_ops);

CREATE TABLE entities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    entity_type text NOT NULL,
    name text NOT NULL,
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(organization_id, entity_type, name)
);
CREATE TABLE relationships (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    source_entity_id uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type text NOT NULL,
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (source_entity_id <> target_entity_id),
    UNIQUE(source_entity_id, target_entity_id, relationship_type)
);
CREATE INDEX relationships_target_idx ON relationships(target_entity_id, relationship_type);
CREATE TABLE timelines (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
    title text NOT NULL,
    occurred_at timestamptz NOT NULL,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX timelines_org_occurred_idx ON timelines(organization_id, occurred_at DESC);

CREATE TABLE search_indexes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name text NOT NULL,
    configuration jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(organization_id, name)
);
CREATE TABLE indexed_content (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    search_index_id uuid NOT NULL REFERENCES search_indexes(id) ON DELETE CASCADE,
    document_id uuid REFERENCES documents(id) ON DELETE CASCADE,
    source_type text NOT NULL,
    source_id uuid NOT NULL,
    content text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(1536),
    indexed_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(search_index_id, source_type, source_id)
);
CREATE INDEX indexed_content_embedding_idx ON indexed_content USING hnsw (embedding vector_cosine_ops);

CREATE TABLE api_keys (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by uuid REFERENCES users(id) ON DELETE SET NULL,
    name text NOT NULL,
    key_prefix text NOT NULL,
    key_hash text NOT NULL UNIQUE,
    scopes jsonb NOT NULL DEFAULT '[]'::jsonb,
    expires_at timestamptz,
    last_used_at timestamptz,
    revoked_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX api_keys_org_active_idx ON api_keys(organization_id) WHERE revoked_at IS NULL;
CREATE TABLE integrations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider text NOT NULL,
    status integration_status NOT NULL DEFAULT 'PENDING',
    encrypted_credentials bytea NOT NULL,
    configuration jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(organization_id, provider)
);

CREATE TABLE audit_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid REFERENCES organizations(id) ON DELETE SET NULL,
    actor_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
    action text NOT NULL,
    entity_type text,
    entity_id uuid,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX audit_logs_org_created_idx ON audit_logs(organization_id, created_at DESC);
CREATE INDEX audit_logs_actor_created_idx ON audit_logs(actor_user_id, created_at DESC);

CREATE TABLE plans (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_key text NOT NULL UNIQUE,
    name text NOT NULL,
    price_cents integer NOT NULL CHECK (price_cents >= 0),
    currency char(3) NOT NULL DEFAULT 'USD',
    billing_interval text NOT NULL CHECK (billing_interval IN ('month', 'year')),
    features jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE subscriptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    plan_id uuid NOT NULL REFERENCES plans(id) ON DELETE RESTRICT,
    status subscription_status NOT NULL DEFAULT 'TRIALING',
    started_at timestamptz NOT NULL DEFAULT now(),
    current_period_end timestamptz,
    cancelled_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX subscriptions_org_status_idx ON subscriptions(organization_id, status);
CREATE TABLE usage_records (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    metric text NOT NULL,
    quantity bigint NOT NULL CHECK (quantity >= 0),
    recorded_at timestamptz NOT NULL DEFAULT now(),
    period_start date NOT NULL,
    period_end date NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    CHECK (period_end >= period_start)
);
CREATE INDEX usage_records_org_period_idx ON usage_records(organization_id, period_start, metric);

CREATE TABLE notifications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title text NOT NULL,
    body text NOT NULL DEFAULT '',
    status notification_status NOT NULL DEFAULT 'UNREAD',
    data jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    read_at timestamptz
);
CREATE INDEX notifications_user_status_created_idx ON notifications(user_id, status, created_at DESC);
