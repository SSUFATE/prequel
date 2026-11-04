"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  colors,
  inputStyle,
  helperTextStyle,
  labelStyle,
  submitButtonStyle,
} from "@/app/lib/authStyles";
import { ApiError, signup } from "@/app/lib/api";

const LANGUAGES = [
  { value: "", label: "선호 언어 선택" },
  { value: "ko", label: "한국어" },
  { value: "en", label: "English" },
  { value: "ja", label: "日本語" },
  { value: "zh", label: "中文" },
];

type FieldState = "default" | "error" | "success";

export default function SignupPage() {
  const router = useRouter();

  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("");
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);



  const [idTakenByServer, setIdTakenByServer] = useState(false);
  const [emailTakenByServer, setEmailTakenByServer] = useState(false);

  const idFormatValid = id.length >= 4; 
  const idState: FieldState = useMemo(() => {
    if (idTakenByServer) return "error";
    if (!touched.id || id.length === 0) return "default";
    return idFormatValid ? "success" : "error";
  }, [id, touched.id, idFormatValid, idTakenByServer]);

  const idMessage = useMemo(() => {
    if (idTakenByServer) return "이미 사용 중인 아이디입니다.";
    if (!touched.id || id.length === 0) return null;
    return idFormatValid ? "사용 가능한 아이디입니다." : "아이디는 4자 이상이어야 합니다.";
  }, [idFormatValid, idTakenByServer, touched.id, id]);

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
    if (emailTakenByServer) return "error";
    if (!touched.email || email.length === 0) return "default";
    return emailFormatValid ? "success" : "error";
  }, [email, emailFormatValid, touched.email, emailTakenByServer]);

  const emailMessage = useMemo(() => {
    if (emailTakenByServer) return "이미 가입된 이메일입니다.";
    if (!touched.email || email.length === 0) return null;
    return emailFormatValid ? "사용 가능한 이메일입니다." : "올바른 이메일 형식을 입력해주세요.";
  }, [email, emailFormatValid, touched.email, emailTakenByServer]);

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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid || isSubmitting) return;

    setSubmitError(null);
    setIsSubmitting(true);
    try {
      await signup({
        login_id: id,
        password,
        username: username.trim(),
        email,
        language: preferredLanguage,
      });
      router.push("/login");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        if (err.message.includes("아이디")) {
          setIdTakenByServer(true);
          markTouched("id");
        } else if (err.message.includes("이메일")) {
          setEmailTakenByServer(true);
          markTouched("email");
        } else {
          setSubmitError(err.message);
        }
      } else if (err instanceof ApiError) {
        setSubmitError(err.message);
      } else {
        setSubmitError("회원가입 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#FFFFFF" }}>

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
              onChange={(e) => {
                setId(e.target.value);
                if (idTakenByServer) setIdTakenByServer(false);
              }}
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
              onChange={(e) => {
                setEmail(e.target.value);
                if (emailTakenByServer) setEmailTakenByServer(false);
              }}
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

          {submitError && <p style={{ ...helperTextStyle("error"), marginBottom: 16 }}>{submitError}</p>}

          <button
            type="submit"
            style={submitButtonStyle(isFormValid && !isSubmitting)}
            disabled={!isFormValid || isSubmitting}
          >
            {isSubmitting ? "가입 처리 중..." : "회원가입"}
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