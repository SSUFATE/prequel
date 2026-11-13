"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { clearAccessToken, getAccessToken, saveAccessToken } from "@/app/lib/api";

type AuthContextValue = {
  isLoggedIn: boolean;
  isLoading: boolean;
  login: (accessToken: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);


  useEffect(() => {
    setToken(getAccessToken());
    setIsLoading(false);
  }, []);

  const login = useCallback((accessToken: string) => {
    saveAccessToken(accessToken);
    setToken(accessToken);
  }, []);

  const logout = useCallback(() => {
    clearAccessToken();
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn: Boolean(token), isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth는 AuthProvider 내부에서만 사용할 수 있습니다.");
  }
  return ctx;
}