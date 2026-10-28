import { api, tokenStore } from "../api";

export async function login(email: string, password: string, totp_code?: string) {
  const { data } = await api.post("/auth/login", { email, password, totp_code });
  tokenStore.set(data.access_token, data.refresh_token);
  return data;
}
export const register = (email: string, password: string, full_name = "") =>
  api.post("/auth/register", { email, password, full_name }).then((r) => r.data);
export const forgotPassword = (email: string) => api.post("/auth/forgot-password", { email }).then((r) => r.data);
export const resetPassword = (token: string, new_password: string) =>
  api.post("/auth/reset-password", { token, new_password }).then((r) => r.data);
export const setup2fa = () => api.post("/auth/2fa/setup").then((r) => r.data);
export const verify2fa = (code: string) => api.post("/auth/2fa/verify", { code }).then((r) => r.data);
export async function logout() {
  try {
    await api.post("/auth/logout");
  } finally {
    tokenStore.clear();
  }
}
