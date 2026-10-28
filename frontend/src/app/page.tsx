import { getDashboardData } from "@/lib/api";

export const instant = false;

const navigation = [
  { label: "Overview", href: "#overview", icon: "⌂" },
  { label: "Projects", href: "#projects", icon: "▦" },
  { label: "Agents", href: "#agents", icon: "◈" },
  { label: "Memory", href: "#memory", icon: "◎" },
];

export default async function Home() {
  const { health, projects, agents, memories } = await getDashboardData();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" aria-label="Onoma AI Genesis home">
          <span className="brand-mark">O</span>
          <span className="brand-copy">
            <strong>ONOMA AI</strong>
            <span>GENESIS</span>
          </span>
        </a>

        <p className="nav-heading">WORKSPACE</p>
        <nav className="main-nav" aria-label="Main navigation">
          {navigation.map((item, index) => (
            <a
              className={`nav-link${index === 0 ? " active" : ""}`}
              href={item.href}
              key={item.label}
            >
              <span aria-hidden="true">{item.icon}</span>
              {item.label}
            </a>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <span className="sidebar-orbit" aria-hidden="true">✳</span>
          <p>Natural Artificial Intelligence</p>
          <span>Local Genesis Runtime</span>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Onoma</span>
            <span className="breadcrumb-separator">/</span>
            <strong>Overview</strong>
          </div>
          <div className={`runtime-status${health ? " online" : " offline"}`} role="status">
            <span className="status-dot" />
            {health ? "Runtime operational" : "Runtime unavailable"}
          </div>
        </header>

        <div className="page-content">
          <section className="hero">
            <div className="hero-copy">
              <p className="eyebrow"><span /> UNIVERSAL INTELLIGENCE OPERATING SYSTEM</p>
              <h1>One Intelligence.<br /><span>Infinite Possibilities.</span></h1>
              <p className="hero-description">
                Build, search, reason, and create in one connected intelligence workspace.
              </p>
              <a className="primary-link" href="#projects">
                Explore your workspace <span aria-hidden="true">↗</span>
              </a>
            </div>
            <div className="hero-art" aria-hidden="true">
              <div className="art-ring ring-one" />
              <div className="art-ring ring-two" />
              <div className="art-core">O</div>
              <span className="art-star star-one">✳</span>
              <span className="art-star star-two">✦</span>
              <span className="art-star star-three">·</span>
            </div>
          </section>

          <section className="metrics" aria-label="Workspace summary">
            <article className="metric-card">
              <span className="metric-icon violet">⌘</span>
              <div><p>Runtime</p><strong>{health ? health.version : "Not connected"}</strong></div>
              <span className={`metric-indicator${health ? " good" : ""}`} />
            </article>
            <article className="metric-card">
              <span className="metric-icon blue">▦</span>
              <div><p>Projects</p><strong>{projects?.length ?? "—"}</strong></div>
              <span className="metric-caption">workspaces</span>
            </article>
            <article className="metric-card">
              <span className="metric-icon green">◈</span>
              <div><p>Agent network</p><strong>{agents?.length ?? "—"}</strong></div>
              <span className="metric-caption">available</span>
            </article>
            <article className="metric-card">
              <span className="metric-icon amber">◎</span>
              <div><p>Memory</p><strong>{memories?.length ?? "—"}</strong></div>
              <span className="metric-caption">stored items</span>
            </article>
          </section>

          {!health && (
            <div className="connection-notice" role="note">
              <span aria-hidden="true">↗</span>
              <p>
                Connect the FastAPI service to load live workspace data. Configure
                <code> API_BASE_URL</code> in <code>frontend/.env.local</code>.
              </p>
            </div>
          )}

          <div className="content-grid">
            <section className="section-panel projects-panel" id="projects">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">YOUR WORK</p>
                  <h2>Recent projects</h2>
                </div>
                <span className="section-count">{projects?.length ?? 0}</span>
              </div>
              {projects?.length ? (
                <div className="project-list">
                  {projects.slice(0, 5).map((project) => (
                    <article className="project-row" key={project.id}>
                      <span className="project-icon">◇</span>
                      <div className="project-details">
                        <strong>{project.name}</strong>
                        <p>{project.description || "No description yet"}</p>
                      </div>
                      <span className="project-date">{formatDate(project.created_at)}</span>
                    </article>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title={health ? "Your workspace is ready" : "Waiting for your workspace"}
                  description={
                    health
                      ? "Projects from your Genesis workspace will appear here."
                      : "Start the API to see your projects and workspace activity."
                  }
                />
              )}
            </section>

            <section className="section-panel agents-panel" id="agents">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">OAN · ONOMA AGENT NETWORK</p>
                  <h2>Agent network</h2>
                </div>
                <span className="section-count">{agents?.length ?? 0}</span>
              </div>
              {agents?.length ? (
                <div className="agent-list">
                  {agents.slice(0, 5).map((agent) => (
                    <article className="agent-row" key={agent.id}>
                      <span className="agent-avatar">{agent.name.slice(0, 1)}</span>
                      <div className="agent-details">
                        <strong>{agent.name}</strong>
                        <p>{agent.role}</p>
                      </div>
                      <span className="agent-status"><span />{agent.status}</span>
                    </article>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="Agents will appear here"
                  description="The registered Genesis agents show up when the API is connected."
                />
              )}
            </section>
          </div>

          <section className="section-panel memory-panel" id="memory">
            <div className="section-heading">
              <div>
                <p className="eyebrow">OME · ONOMA MEMORY ENGINE</p>
                <h2>Recent memory</h2>
              </div>
              <span className="section-count">{memories?.length ?? 0}</span>
            </div>
            {memories?.length ? (
              <div className="memory-list">
                {memories.slice(0, 3).map((memory) => (
                  <article className="memory-row" key={memory.id}>
                    <span className="memory-kind">{memory.kind}</span>
                    <p>{memory.content}</p>
                    <time>{formatDate(memory.created_at)}</time>
                  </article>
                ))}
              </div>
            ) : (
              <EmptyState
                title="A thoughtful workspace remembers"
                description="Saved project and session context will be available here."
              />
            )}
          </section>

          <footer className="page-footer">
            <span>ONOMA AI GENESIS</span>
            <span>One Intelligence. Infinite Possibilities.</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="empty-state">
      <span className="empty-mark" aria-hidden="true">✳</span>
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Recently"
    : new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(date);
}
