const API_BASE_URL = (process.env.API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

export type Project = {
  id: number;
  name: string;
  description: string;
  created_at: string;
};

export type Agent = {
  id: string;
  name: string;
  role: string;
  status: string;
};

export type Memory = {
  id: number;
  kind: string;
  content: string;
  created_at: string;
};

export type Health = {
  status: string;
  platform: string;
  version: string;
};

async function get<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getDashboardData() {
  const [health, projects, agents, memories] = await Promise.all([
    get<Health>("/api/health"),
    get<Project[]>("/api/projects"),
    get<Agent[]>("/api/agents"),
    get<Memory[]>("/api/memory"),
  ]);

  return { health, projects, agents, memories };
}
