import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api, clearTokens, getAccessToken, setTokens } from "../api/client";
import type { User } from "../api/types";

interface AuthState {
  user: User | null;
  loading: boolean;
  isAuthed: boolean;
  isAdmin: boolean;
  refresh: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    if (!getAccessToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get<User>("/auth/me");
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function logout() {
    clearTokens();
    setUser(null);
  }

  const value = useMemo<AuthState>(
    () => ({
      user,
      loading,
      isAuthed: !!user,
      isAdmin: user?.role === "admin",
      refresh,
      logout,
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

// Called by the OAuth callback page once tokens arrive in the URL fragment.
export function consumeTokensFromHash(hash: string): boolean {
  const params = new URLSearchParams(hash.replace(/^#/, ""));
  const access = params.get("access_token");
  const refreshTok = params.get("refresh_token");
  if (access && refreshTok) {
    setTokens(access, refreshTok);
    return true;
  }
  return false;
}
