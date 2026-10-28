"use client";
import { createContext, useCallback, useState, type ReactNode } from "react";
import * as authApi from "@/lib/api/auth";
import { tokenStore } from "@/lib/api";

export interface AuthState {
  authenticated: boolean;
  login: (email: string, password: string, totp?: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState(() => !!tokenStore.get());
  const login = useCallback(async (email: string, password: string, totp?: string) => {
    await authApi.login(email, password, totp);
    setAuthenticated(true);
  }, []);
  const logout = useCallback(async () => {
    await authApi.logout();
    setAuthenticated(false);
  }, []);
  return <AuthContext.Provider value={{ authenticated, login, logout }}>{children}</AuthContext.Provider>;
}
