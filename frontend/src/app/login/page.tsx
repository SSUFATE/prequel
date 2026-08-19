"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  colors,
  inputStyle,
  helperTextStyle,
  labelStyle,
  submitButtonStyle,
} from "@/app/lib/authStyles";
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
  const passwordHasError = error === "PASSWORD_REQUIRED" || error === "MISMATCH";

  async function handleSubmit(e: React.FormEvent) {
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
    <div style={{ minHeight: "100vh", background: "#FFFFFF" }}>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "20px 32px",
          borderBottom: `1px solid ${colors.border}`,
        }}
      >
        <span style={{ fontSize: 20, fontWeight: 700, color: colors.textPrimary }}>Prequel</span>
        <nav style={{ display: "flex", gap: 20, fontSize: 14 }}>
          <Link href="/signup" style={{ color: colors.textSecondary }}>
            회원가입
          </Link>
          <Link href="/login" style={{ color: colors.textPrimary, fontWeight: 600 }}>
            로그인
          </Link>
        </nav>
      </header>

      <main
        style={{
          maxWidth: 400,
          margin: "0 auto",
          padding: "56px 24px 80px",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: colors.textPrimary, marginBottom: 10 }}>
            Prequel
          </h1>
          <p style={{ fontSize: 14, color: colors.textSecondary }}>
            K콘텐츠로 한국 문학을 탐색해보세요!
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={labelStyle} htmlFor="id">
              아이디
            </label>
            <input
              id="id"
              style={inputStyle(idHasError ? "error" : "default")}
              placeholder="아이디"
              value={id}
              onChange={(e) => {
                setId(e.target.value);
                if (error) setError(null);
              }}
            />
          </div>

          <div style={{ marginBottom: 10 }}>
            <label style={labelStyle} htmlFor="password">
              비밀번호
            </label>
            <input
              id="password"
              type="password"
              style={inputStyle(passwordHasError ? "error" : "default")}
              placeholder="비밀번호"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) setError(null);
              }}
            />
          </div>

          {error && <p style={helperTextStyle("error")}>{ERROR_MESSAGE[error]}</p>}

          <button
            type="submit"
            style={{ ...submitButtonStyle(true), marginTop: 18 }}
            disabled={isSubmitting}
          >
            {isSubmitting ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: 24, fontSize: 13, color: colors.textSecondary }}>
          아직 회원이 아니신가요?{" "}
          <Link href="/signup" style={{ color: colors.coral, fontWeight: 600 }}>
            회원가입
          </Link>
        </p>
      </main>
    </div>
  );
}