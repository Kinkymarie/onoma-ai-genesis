import { api } from "../api";

export const listProjects = () => api.get("/api/projects").then((r) => r.data);
export const createProject = (name: string, description = "") =>
  api.post("/api/projects", { name, description }).then((r) => r.data);
