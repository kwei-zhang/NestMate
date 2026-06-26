import axios from "axios";

// All backend calls go through /api (proxied to FastAPI in dev).
export const api = axios.create({ baseURL: "/api" });

const ACCESS_KEY = "nm_access";
const REFRESH_KEY = "nm_refresh";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401, try a one-time refresh, then replay the request.
let refreshing: Promise<string | null> | null = null;

async function refreshAccess(): Promise<string | null> {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return null;
  try {
    const { data } = await axios.post("/api/auth/refresh", { refresh_token: refresh });
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

api.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      refreshing = refreshing ?? refreshAccess();
      const token = await refreshing;
      refreshing = null;
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      }
    }
    return Promise.reject(error);
  },
);
