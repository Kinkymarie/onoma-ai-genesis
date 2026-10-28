"use client";
import { createContext, useState, type ReactNode } from "react";

export const WorkspaceContext = createContext<{ workspaceId: string | null; setWorkspaceId: (id: string) => void }>({
  workspaceId: null,
  setWorkspaceId: () => {},
});

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  return <WorkspaceContext.Provider value={{ workspaceId, setWorkspaceId }}>{children}</WorkspaceContext.Provider>;
}
