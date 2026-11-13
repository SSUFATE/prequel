"use client";

import "./login.css";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ApiError, login as loginRequest } from "@/app/lib/api";
import { useAuth } from "@/app/lib/authContext";

type LoginError =
  | null
  | "ID_REQUIRED"
  | "PASSWORD_REQUIRED"
  | "MISMATCH"
  | "INACTIVE"
  | "SERVER_ERROR";

const ERROR_MESSAGE: Record<Exclude<LoginError, null>, string> = {
  ID_REQUIRED: "아이디를 입력해주세요.",
  PASSWORD_REQUIRED: "비밀번호를 입력해주세요.",
  MISMATCH: "아이디 또는 비밀번호가 일치하지 않습니다.",
  INACTIVE: "비활성화된 사용자입니다.",
  SERVER_ERROR: "로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
};

export default function LoginPage() {
  const router = useRouter();
  const auth = useAuth();

  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<LoginError>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const idHasError = error === "ID_REQUIRED" || error === "MISMATCH";
  const passwordHasError =
    error === "PASSWORD_REQUIRED" || error === "MISMATCH";

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (id.trim().length === 0) {
      setError("ID_REQUIRED");
      return;
    }

    if (password.length === 0) {
      setError("PASSWORD_REQUIRED");
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      const { access_token } = await loginRequest(id.trim(), password);

      auth.login(access_token);
      router.push("/");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("MISMATCH");
        } else if (err.status === 403) {
          setError("INACTIVE");
        } else {
          setError("SERVER_ERROR");
        }
      } else {
        setError("SERVER_ERROR");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-heading">
          <h1>Prequel</h1>

          <p>
            좋아하는 K-콘텐츠에서
            <br />
            새로운 한국 문학을 발견해보세요.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <label htmlFor="id">아이디</label>

            <input
              id="id"
              type="text"
              autoComplete="username"
              className={idHasError ? "login-input error" : "login-input"}
              placeholder="아이디를 입력해주세요"
              value={id}
              onChange={(e) => {
                setId(e.target.value);
                if (error) setError(null);
              }}
            />
          </div>

          <div className="login-field">
            <label htmlFor="password">비밀번호</label>

            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className={
                passwordHasError ? "login-input error" : "login-input"
              }
              placeholder="비밀번호를 입력해주세요"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) setError(null);
              }}
            />
          </div>

          {error && (
            <p className="login-error" role="alert">
              {ERROR_MESSAGE[error]}
            </p>
          )}

          <button
            type="submit"
            className="login-submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <p className="login-signup">
          아직 회원이 아니신가요?{" "}
          <Link href="/signup">회원가입</Link>
        </p>
      </section>
    </main>
  );
}