import { api } from "../api";

export const listAgents = () => api.get("/api/agents").then((r) => r.data);
export const executeAgent = (agentId: string, input: string) =>
  api.post(`/api/agents/${agentId}/execute`, { input }).then((r) => r.data);
export const chat = (message: string) => api.post("/api/chat", { message }).then((r) => r.data);
export const search = (query: string) => api.post("/api/embeddings/search", { query }).then((r) => r.data);
