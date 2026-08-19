"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  colors,
  inputStyle,
  helperTextStyle,
  labelStyle,
  submitButtonStyle,
} from "@/app/lib/authStyles";

// TODO: 백엔드 붙이면 이 목록/판정 로직을 실제 API 호출로 교체
const TAKEN_IDS = ["admin", "test", "prequel"];
const TAKEN_EMAILS = ["taken@example.com"];

const LANGUAGES = [
  { value: "", label: "선호 언어 선택" },
  { value: "ko", label: "한국어" },
  { value: "en", label: "English" },
  { value: "ja", label: "日本語" },
  { value: "zh", label: "中文" },
];

type FieldState = "default" | "error" | "success";

export default function SignupPage() {
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("");
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const idState: FieldState = useMemo(() => {
    if (!touched.id || id.length === 0) return "default";
    return TAKEN_IDS.includes(id) ? "error" : "success";
  }, [id, touched.id]);

  const idMessage = useMemo(() => {
    if (!touched.id || id.length === 0) return null;
    return idState === "error" ? "이미 사용 중인 아이디입니다." : "사용 가능한 아이디입니다.";
  }, [idState, touched.id, id]);

  const passwordValid = password.length >= 8;
  const passwordState: FieldState = useMemo(() => {
    if (!touched.password || password.length === 0) return "default";
    return passwordValid ? "success" : "error";
  }, [password, passwordValid, touched.password]);

  const passwordMessage = useMemo(() => {
    if (password.length === 0) return touched.password ? "비밀번호는 8자 이상이어야 합니다." : null;
    return passwordValid ? null : "비밀번호는 8자 이상이어야 합니다.";
  }, [password, passwordValid, touched.password]);

  const passwordConfirmState: FieldState = useMemo(() => {
    if (!touched.passwordConfirm || passwordConfirm.length === 0) return "default";
    return passwordConfirm === password ? "success" : "error";
  }, [passwordConfirm, password, touched.passwordConfirm]);

  const passwordConfirmMessage = useMemo(() => {
    if (!touched.passwordConfirm || passwordConfirm.length === 0) return null;
    return passwordConfirm === password ? "비밀번호가 일치합니다." : "비밀번호가 일치하지 않습니다.";
  }, [passwordConfirm, password, touched.passwordConfirm]);

  const emailFormatValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const emailState: FieldState = useMemo(() => {
    if (!touched.email || email.length === 0) return "default";
    if (!emailFormatValid) return "error";
    return TAKEN_EMAILS.includes(email) ? "error" : "success";
  }, [email, emailFormatValid, touched.email]);

  const emailMessage = useMemo(() => {
    if (!touched.email || email.length === 0) return null;
    if (!emailFormatValid) return "올바른 이메일 형식을 입력해주세요.";
    if (TAKEN_EMAILS.includes(email)) return "이미 사용 중인 이메일입니다.";
    return "사용 가능한 이메일입니다.";
  }, [email, emailFormatValid, touched.email]);

  const isFormValid =
    idState === "success" &&
    passwordValid &&
    passwordConfirm === password &&
    passwordConfirm.length > 0 &&
    username.trim().length > 0 &&
    emailState === "success" &&
    preferredLanguage.length > 0;

  function markTouched(field: string) {
    setTouched((prev) => ({ ...prev, [field]: true }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid) return;
    // TODO: 회원가입 API 연동
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
          <Link href="/signup" style={{ color: colors.textPrimary, fontWeight: 600 }}>
            회원가입
          </Link>
          <Link href="/login" style={{ color: colors.textSecondary }}>
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
          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle} htmlFor="id">
              아이디
            </label>
            <input
              id="id"
              style={inputStyle(idState)}
              placeholder="아이디"
              value={id}
              onChange={(e) => setId(e.target.value)}
              onBlur={() => markTouched("id")}
            />
            {idMessage && <p style={helperTextStyle(idState)}>{idMessage}</p>}
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle} htmlFor="password">
              비밀번호
            </label>
            <input
              id="password"
              type="password"
              style={inputStyle(passwordState)}
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => markTouched("password")}
            />
            {passwordMessage && <p style={helperTextStyle(passwordState)}>{passwordMessage}</p>}
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle} htmlFor="passwordConfirm">
              비밀번호 확인
            </label>
            <input
              id="passwordConfirm"
              type="password"
              style={inputStyle(passwordConfirmState)}
              placeholder="비밀번호 다시 입력"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              onBlur={() => markTouched("passwordConfirm")}
            />
            {passwordConfirmMessage && (
              <p style={helperTextStyle(passwordConfirmState)}>{passwordConfirmMessage}</p>
            )}
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle} htmlFor="username">
              사용자 이름
            </label>
            <input
              id="username"
              style={inputStyle("default")}
              placeholder="사용자 이름 입력"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onBlur={() => markTouched("username")}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle} htmlFor="email">
              이메일
            </label>
            <input
              id="email"
              type="email"
              style={inputStyle(emailState)}
              placeholder="example@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onBlur={() => markTouched("email")}
            />
            {emailMessage && <p style={helperTextStyle(emailState)}>{emailMessage}</p>}
          </div>

          <div style={{ marginBottom: 28 }}>
            <label style={labelStyle} htmlFor="preferredLanguage">
              사용자 선호 언어
            </label>
            <select
              id="preferredLanguage"
              style={{ ...inputStyle("default"), color: preferredLanguage ? colors.textPrimary : colors.placeholder }}
              value={preferredLanguage}
              onChange={(e) => setPreferredLanguage(e.target.value)}
              onBlur={() => markTouched("preferredLanguage")}
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" style={submitButtonStyle(isFormValid)} disabled={!isFormValid}>
            회원가입
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: 24, fontSize: 13, color: colors.textSecondary }}>
          이미 회원이신가요?{" "}
          <Link href="/login" style={{ color: colors.coral, fontWeight: 600 }}>
            로그인
          </Link>
        </p>
      </main>
    </div>
  );
}