
"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import {
  ApiError,
  signup,
  login as loginRequest,
  checkLoginId,
  checkEmail,
} from "@/api/auth";
import { useAuth } from "@/app/lib/authContext";
import "./signup.css";

const LANGUAGES = [
  { value: "", label: "선호 언어 선택" },
  { value: "ko", label: "한국어" },
  { value: "en", label: "English" },
  { value: "ja", label: "日本語" },
  { value: "zh", label: "中文" },
];

type FieldState = "default" | "error" | "success";

// 서버 중복 확인 상태
type CheckStatus =
  | "idle"
  | "checking"
  | "available"
  | "taken"
  | "error";

type CheckResult = {
  value: string;
  status: CheckStatus;
};

export default function SignupPage() {
  const router = useRouter();
  const auth = useAuth();

  // =========================
  // 회원가입 입력값
  // =========================

  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("");

  // =========================
  // 입력 및 제출 상태
  // =========================

  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // 서버에서 확인한 아이디·이메일 중복 검사 결과
  // value를 함께 저장해 이전 입력값의 검사 결과가
  // 현재 입력값에 적용되지 않도록 처리
  const [idCheck, setIdCheck] = useState<CheckResult>({
    value: "",
    status: "idle",
  });

  const [emailCheck, setEmailCheck] = useState<CheckResult>({
    value: "",
    status: "idle",
  });

  // =========================
  // 입력값 형식 검사
  // =========================

  const idFormatValid = id.length >= 4;

  const emailFormatValid =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  // =========================
  // 아이디 중복 확인
  // =========================

  useEffect(() => {
    // 아이디가 4자 미만이면 서버 요청하지 않음
    if (!idFormatValid) return;

    const controller = new AbortController();

    // 입력이 멈춘 후 500ms가 지나면 중복 확인
    const timer = setTimeout(async () => {
      setIdCheck({
        value: id,
        status: "checking",
      });

      try {
        const available = await checkLoginId(
          id,
          controller.signal
        );

        if (!controller.signal.aborted) {
          setIdCheck({
            value: id,
            status: available ? "available" : "taken",
          });
        }
      } catch {
        // 취소된 요청은 오류로 표시하지 않음
        if (!controller.signal.aborted) {
          setIdCheck({
            value: id,
            status: "error",
          });
        }
      }
    }, 500);

    // 입력값이 바뀌면 이전 타이머 및 요청 취소
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [id, idFormatValid]);

  // =========================
  // 이메일 중복 확인
  // =========================

  useEffect(() => {
    // 이메일 형식이 올바르지 않으면 서버 요청하지 않음
    if (!emailFormatValid) return;

    const controller = new AbortController();

    // 입력이 멈춘 후 500ms가 지나면 중복 확인
    const timer = setTimeout(async () => {
      setEmailCheck({
        value: email,
        status: "checking",
      });

      try {
        const available = await checkEmail(
          email,
          controller.signal
        );

        if (!controller.signal.aborted) {
          setEmailCheck({
            value: email,
            status: available ? "available" : "taken",
          });
        }
      } catch {
        // 취소된 요청은 오류로 표시하지 않음
        if (!controller.signal.aborted) {
          setEmailCheck({
            value: email,
            status: "error",
          });
        }
      }
    }, 500);

    // 입력값이 바뀌면 이전 타이머 및 요청 취소
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [email, emailFormatValid]);

  // =========================
  // 아이디 검증 상태 및 안내 문구
  // =========================

  // 현재 입력값과 서버 검사 대상이 일치할 때만 결과 사용
  const currentIdStatus: CheckStatus =
    idCheck.value === id ? idCheck.status : "idle";

  const idState: FieldState = useMemo(() => {
    if (!touched.id || id.length === 0) return "default";

    if (!idFormatValid || currentIdStatus === "taken") {
      return "error";
    }

    if (currentIdStatus === "available") {
      return "success";
    }

    return "default";
  }, [id, touched.id, idFormatValid, currentIdStatus]);

  const idMessage = useMemo(() => {
    if (!touched.id || id.length === 0) return null;

    if (!idFormatValid) {
      return "아이디는 4자 이상이어야 합니다.";
    }

    if (currentIdStatus === "taken") {
      return "이미 사용 중인 아이디입니다.";
    }

    if (currentIdStatus === "available") {
      return "사용 가능한 아이디입니다.";
    }

    if (currentIdStatus === "error") {
      return "중복 확인에 실패했습니다. 다시 입력해주세요.";
    }

    return "아이디 중복 확인 중...";
  }, [id, touched.id, idFormatValid, currentIdStatus]);

  // =========================
  // 비밀번호 검증
  // =========================

  const passwordValid = password.length >= 8;

  const passwordState: FieldState = useMemo(() => {
    if (!touched.password || password.length === 0) {
      return "default";
    }

    return passwordValid ? "success" : "error";
  }, [password, passwordValid, touched.password]);

  const passwordMessage = useMemo(() => {
    if (password.length === 0) {
      return touched.password
        ? "비밀번호는 8자 이상이어야 합니다."
        : null;
    }

    return passwordValid
      ? null
      : "비밀번호는 8자 이상이어야 합니다.";
  }, [password, passwordValid, touched.password]);

  // =========================
  // 비밀번호 확인 검증
  // =========================

  const passwordConfirmState: FieldState = useMemo(() => {
    if (!touched.passwordConfirm || passwordConfirm.length === 0) {
      return "default";
    }

    return passwordConfirm === password ? "success" : "error";
  }, [passwordConfirm, password, touched.passwordConfirm]);

  const passwordConfirmMessage = useMemo(() => {
    if (!touched.passwordConfirm || passwordConfirm.length === 0) {
      return null;
    }

    return passwordConfirm === password
      ? "비밀번호가 일치합니다."
      : "비밀번호가 일치하지 않습니다.";
  }, [passwordConfirm, password, touched.passwordConfirm]);

  // =========================
  // 이메일 검증 상태 및 안내 문구
  // =========================

  const currentEmailStatus: CheckStatus =
    emailCheck.value === email ? emailCheck.status : "idle";

  const emailState: FieldState = useMemo(() => {
    if (!touched.email || email.length === 0) {
      return "default";
    }

    if (!emailFormatValid || currentEmailStatus === "taken") {
      return "error";
    }

    if (currentEmailStatus === "available") {
      return "success";
    }

    return "default";
  }, [email, emailFormatValid, touched.email, currentEmailStatus]);

  const emailMessage = useMemo(() => {
    if (!touched.email || email.length === 0) return null;

    if (!emailFormatValid) {
      return "올바른 이메일 형식을 입력해주세요.";
    }

    if (currentEmailStatus === "taken") {
      return "이미 가입된 이메일입니다.";
    }

    if (currentEmailStatus === "available") {
      return "사용 가능한 이메일입니다.";
    }

    if (currentEmailStatus === "error") {
      return "중복 확인에 실패했습니다. 다시 입력해주세요.";
    }

    return "이메일 중복 확인 중...";
  }, [email, emailFormatValid, touched.email, currentEmailStatus]);

  // =========================
  // 회원가입 가능 여부
  // =========================

  // 아이디와 이메일은 서버 중복 확인까지 성공해야
  // 회원가입 버튼을 활성화함
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

  // =========================
  // 회원가입 요청
  // =========================

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
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

      // 회원가입 성공 후 자동 로그인
      await loginRequest(id.trim(), password);
      await auth.login();

      router.replace("/");
    } catch (err) {
      // 회원가입 직전 다른 사용자가 동일한 아이디나
      // 이메일로 가입했을 경우 서버의 409 응답 처리
      if (err instanceof ApiError && err.status === 409) {
        if (err.message.includes("아이디")) {
          setIdCheck({
            value: id,
            status: "taken",
          });
          markTouched("id");
        } else if (err.message.includes("이메일")) {
          setEmailCheck({
            value: email,
            status: "taken",
          });
          markTouched("email");
        } else {
          setSubmitError(err.message);
        }
      } else if (err instanceof ApiError) {
        setSubmitError(err.message);
      } else {
        setSubmitError(
          "회원가입 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="signup-page">
      <section className="signup-card">rm
        <div className="signup-heading">
          <h1>Prequel</h1>

          <p>
            Prequel과 함께
            <br />
            새로운 한국 문학을 발견해보세요.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="signup-form">
          {/* 아이디 */}
          <div className="signup-field">
            <label htmlFor="id">아이디</label>

            <input
              id="id"
              type="text"
              autoComplete="username"
              className={`signup-input ${idState}`}
              placeholder="4자 이상 입력해주세요"
              value={id}
              onChange={(e) => {
                setId(e.target.value);
              }}
              onBlur={() => markTouched("id")}
            />

            {idMessage && (
              <p className={`signup-helper ${idState}`}>
                {idMessage}
              </p>
            )}
          </div>

          {/* 비밀번호 */}
          <div className="signup-field">
            <label htmlFor="password">비밀번호</label>

            <input
              id="password"
              type="password"
              autoComplete="new-password"
              className={`signup-input ${passwordState}`}
              placeholder="8자 이상 입력해주세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => markTouched("password")}
            />

            {passwordMessage && (
              <p className={`signup-helper ${passwordState}`}>
                {passwordMessage}
              </p>
            )}
          </div>

          {/* 비밀번호 확인 */}
          <div className="signup-field">
            <label htmlFor="passwordConfirm">비밀번호 확인</label>

            <input
              id="passwordConfirm"
              type="password"
              autoComplete="new-password"
              className={`signup-input ${passwordConfirmState}`}
              placeholder="비밀번호를 다시 입력해주세요"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              onBlur={() => markTouched("passwordConfirm")}
            />

            {passwordConfirmMessage && (
              <p className={`signup-helper ${passwordConfirmState}`}>
                {passwordConfirmMessage}
              </p>
            )}
          </div>

          {/* 사용자 이름 */}
          <div className="signup-field">
            <label htmlFor="username">사용자 이름</label>

            <input
              id="username"
              type="text"
              autoComplete="nickname"
              className="signup-input"
              placeholder="사용자 이름을 입력해주세요"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onBlur={() => markTouched("username")}
            />
          </div>

          {/* 이메일 */}
          <div className="signup-field">
            <label htmlFor="email">이메일</label>

            <input
              id="email"
              type="email"
              autoComplete="email"
              className={`signup-input ${emailState}`}
              placeholder="example@email.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              onBlur={() => markTouched("email")}
            />

            {emailMessage && (
              <p className={`signup-helper ${emailState}`}>
                {emailMessage}
              </p>
            )}
          </div>

          {/* 선호 언어 */}
          <div className="signup-field">
            <label htmlFor="preferredLanguage">사용자 선호 언어</label>

            <select
              id="preferredLanguage"
              className={`signup-input signup-select ${
                preferredLanguage ? "" : "placeholder"
              }`}
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

          {submitError && (
            <p className="signup-submit-error" role="alert">
              {submitError}
            </p>
          )}

          <button
            type="submit"
            className="signup-submit"
            disabled={!isFormValid || isSubmitting}
          >
            {isSubmitting ? "가입 처리 중..." : "회원가입"}
          </button>
        </form>

        <p className="signup-login">
          이미 회원이신가요?{" "}
          <Link href="/login">로그인</Link>
        </p>
      </section>
    </main>
  );
}
