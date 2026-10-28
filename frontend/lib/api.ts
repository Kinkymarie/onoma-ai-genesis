import axios from "axios";

export const api = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000" });

export const tokenStore = {
  get: () => (typeof window === "undefined" ? null : window.localStorage.getItem("access_token")),
  set: (access: string, refresh: string) => {
    window.localStorage.setItem("access_token", access);
    window.localStorage.setItem("refresh_token", refresh);
  },
  clear: () => {
    window.localStorage.removeItem("access_token");
    window.localStorage.removeItem("refresh_token");
  },
};

api.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config;
    const refresh = typeof window === "undefined" ? null : window.localStorage.getItem("refresh_token");
    if (error.response?.status === 401 && refresh && !original._retry && !original.url?.startsWith("/auth/")) {
      original._retry = true;
      try {
        const { data } = await axios.post(`${api.defaults.baseURL}/auth/refresh`, { refresh_token: refresh });
        tokenStore.set(data.access_token, data.refresh_token);
        return api(original);
      } catch {
        tokenStore.clear();
      }
    }
    return Promise.reject(error);
  }
);
