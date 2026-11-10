"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { logout as logoutApi } from "@/api/auth";
import { getMyInfo } from "@/api/users";

type AuthContextValue = {
  isLoggedIn: boolean;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// 인증 상태 확인 주기: 60초
const AUTH_CHECK_INTERVAL = 60 * 1000;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // 최초 접속 및 주기적인 인증 상태 확인
  useEffect(() => {
    let active = true;

    async function checkAuth() {
      try {
        await getMyInfo();

        if (active) {
          setIsLoggedIn(true);
        }
      } catch {
        if (active) {
          setIsLoggedIn(false);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    void checkAuth();

    const interval = setInterval(() => {
      void checkAuth();
    }, AUTH_CHECK_INTERVAL);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  // API에서 인증 만료(401) 발생 시 로그인 상태 해제
  useEffect(() => {
    const handleUnauthorized = () => {
      setIsLoggedIn(false);
    };

    window.addEventListener("auth:unauthorized", handleUnauthorized);

    return () => {
      window.removeEventListener("auth:unauthorized", handleUnauthorized);
    };
  }, []);

   // 로그인 API 성공 후 인증 상태 갱신
  const login = useCallback(async () => {
    setIsLoggedIn(true);
  }, []);

  // 서버에서 쿠키 삭제 후 로그아웃 처리
  const logout = useCallback(async () => {
    try {
      await logoutApi();
    } finally {
      setIsLoggedIn(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isLoggedIn,
        isLoading,
        login,
        logout,
      }}
    >
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