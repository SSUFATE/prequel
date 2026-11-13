"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/lib/authContext";
import {
  getAccessToken,
  logout as apiLogout,
} from "@/app/lib/api";

import {
  getMyInfo,
  updateMyInfo,
  uploadProfileImage,
  deleteProfileImage,
  deleteMyAccount,
  getProfileImageUrl,
  type UserResponse,
  type Language,
} from "@/api/users";

import "./mypage.css";

const LANGUAGE_LABELS: Record<Language, string> = {
  ko: "한국어",
  en: "English",
  ja: "日本語",
};

export default function MyPage() {
  const router = useRouter();
  const { logout } = useAuth();

  const fileInputRef = useRef<HTMLInputElement>(null);

  const [user, setUser] = useState<UserResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [language, setLanguage] = useState<Language>("ko");

  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [withdrawPassword, setWithdrawPassword] = useState("");
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [withdrawError, setWithdrawError] = useState("");

  // =========================
  // 회원정보 조회
  // =========================

  useEffect(() => {
    let cancelled = false;

    async function loadUser() {
      try {
        const data = await getMyInfo();

        if (cancelled) return;

        setUser(data);
        setUsername(data.username);
        setEmail(data.email);
        setLanguage(data.language);
      } catch (err) {
        if (cancelled) return;

        setError(
          err instanceof Error
            ? err.message
            : "회원정보를 불러오지 못했습니다."
        );
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      cancelled = true;
    };
  }, []);

  // =========================
  // 회원정보 수정
  // =========================

  async function handleSave() {
    if (!user || isSaving) return;

    if (!username.trim()) {
      setError("닉네임을 입력해주세요.");
      return;
    }

    if (!email.trim()) {
      setError("이메일을 입력해주세요.");
      return;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const updatedUser = await updateMyInfo({
        username: username.trim(),
        email: email.trim(),
        language,
      });

      setUser(updatedUser);
      setUsername(updatedUser.username);
      setEmail(updatedUser.email);
      setLanguage(updatedUser.language);

      setIsEditing(false);
      setMessage("회원정보가 수정되었습니다.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "회원정보 수정에 실패했습니다."
      );
    } finally {
      setIsSaving(false);
    }
  }

  function handleCancel() {
    if (!user) return;

    setUsername(user.username);
    setEmail(user.email);
    setLanguage(user.language);

    setIsEditing(false);
    setError("");
    setMessage("");
  }

  // =========================
  // 프로필 이미지 변경
  // =========================

  async function handleImageChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError("JPG, PNG, WEBP 이미지만 업로드할 수 있습니다.");
      event.target.value = "";
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("이미지는 5MB 이하만 업로드할 수 있습니다.");
      event.target.value = "";
      return;
    }

    setIsUploading(true);
    setError("");
    setMessage("");

    try {
      const updatedUser = await uploadProfileImage(file);

      setUser(updatedUser);
      setMessage("프로필 이미지가 변경되었습니다.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "이미지 업로드에 실패했습니다."
      );
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  // =========================
  // 프로필 이미지 삭제
  // =========================

  async function handleImageDelete() {
    if (!user?.profile_image_url || isUploading) return;

    setIsUploading(true);
    setError("");
    setMessage("");

    try {
      const updatedUser = await deleteProfileImage();

      setUser(updatedUser);
      setMessage("프로필 이미지가 삭제되었습니다.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "이미지 삭제에 실패했습니다."
      );
    } finally {
      setIsUploading(false);
    }
  }

  // =========================
  // 로그아웃
  // =========================

  async function handleLogout() {
    const token = getAccessToken();

    if (token) {
      try {
        await apiLogout(token);
      } catch {
        // 서버 요청이 실패해도 로컬 로그인 상태는 해제
      }
    }

    logout();
    router.replace("/");
  }

  // =========================
  // 회원 탈퇴
  // =========================

  async function handleWithdraw() {
  if (!withdrawPassword.trim() || isWithdrawing) return;

  setIsWithdrawing(true);
  setWithdrawError("");

  try {
    await deleteMyAccount(withdrawPassword);

    setShowWithdrawModal(false);
    setWithdrawPassword("");

    logout();
    router.replace("/");
  } catch (err) {
    setWithdrawError(
      err instanceof Error
        ? err.message
        : "회원 탈퇴에 실패했습니다."
    );
  } finally {
    setIsWithdrawing(false);
  }
}

  // =========================
  // Loading
  // =========================

  if (isLoading) {
    return (
      <main className="mypage">
        <div className="mypage-container">
          <p className="mypage-loading">
            회원정보를 불러오는 중...
          </p>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="mypage">
        <div className="mypage-container">
          <h1 className="mypage-title">마이페이지</h1>

          <p className="mypage-error">
            {error || "회원정보를 불러올 수 없습니다."}
          </p>

          <button
            type="button"
            className="mypage-primary-button"
            onClick={() => router.push("/login")}
          >
            로그인하러 가기
          </button>
        </div>
      </main>
    );
  }

  const profileImageUrl = getProfileImageUrl(
    user.profile_image_url
  );

  return (
    <main className="mypage">
      <div className="mypage-container">

        {/* =========================
            Page Heading
        ========================= */}

        <div className="mypage-heading">
          <span className="mypage-eyebrow">
            MY ACCOUNT
          </span>

          <h1 className="mypage-title">
            마이페이지
          </h1>

          <p className="mypage-description">
            나의 프로필과 계정 정보를 관리해보세요.
          </p>
        </div>

        {/* =========================
            Profile
        ========================= */}

        <section className="mypage-profile">

          <div className="mypage-avatar-wrapper">

            <div className="mypage-avatar">
              {profileImageUrl ? (
                <img
                  src={profileImageUrl}
                  alt="프로필 이미지"
                  className="mypage-avatar-image"
                />
              ) : (
                <UserIcon />
              )}
            </div>

            <button
              type="button"
              className="mypage-avatar-edit"
              aria-label="프로필 이미지 변경"
              disabled={isUploading}
              onClick={() => fileInputRef.current?.click()}
            >
              <CameraIcon />
            </button>

          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            hidden
            onChange={handleImageChange}
          />

          <h2 className="mypage-profile-name">
            {user.username}
          </h2>

          <p className="mypage-profile-email">
            {user.email}
          </p>

          <div className="mypage-image-actions">
            <button
              type="button"
              className="mypage-image-button"
              disabled={isUploading}
              onClick={() => fileInputRef.current?.click()}
            >
              {isUploading ? "처리 중..." : "사진 변경"}
            </button>

            {user.profile_image_url && (
              <button
                type="button"
                className="mypage-image-button secondary"
                disabled={isUploading}
                onClick={handleImageDelete}
              >
                사진 삭제
              </button>
            )}
          </div>

        </section>

        {/* =========================
            Messages
        ========================= */}

        {message && (
          <p className="mypage-success">
            {message}
          </p>
        )}

        {error && (
          <p className="mypage-error">
            {error}
          </p>
        )}

        {/* =========================
            Account Information
        ========================= */}

        <section className="mypage-section">

          <div className="mypage-section-heading">
            <h2>회원정보</h2>

            {!isEditing && (
              <button
                type="button"
                className="mypage-edit-button"
                onClick={() => {
                  setIsEditing(true);
                  setError("");
                  setMessage("");
                }}
              >
                수정하기
                <EditIcon />
              </button>
            )}
          </div>

          <div className="mypage-fields">

            {/* 닉네임 */}

            <div className="mypage-field">
              <label htmlFor="mypage-username">
                닉네임
              </label>

              {isEditing ? (
                <input
                  id="mypage-username"
                  className="mypage-input"
                  value={username}
                  maxLength={50}
                  onChange={(e) => setUsername(e.target.value)}
                />
              ) : (
                <div className="mypage-field-value">
                  {user.username}
                </div>
              )}
            </div>

            {/* 이메일 */}

            <div className="mypage-field">
              <label htmlFor="mypage-email">
                이메일
              </label>

              {isEditing ? (
                <input
                  id="mypage-email"
                  type="email"
                  className="mypage-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              ) : (
                <div className="mypage-field-value">
                  {user.email}
                </div>
              )}
            </div>

            {/* 언어 */}

            <div className="mypage-field">
              <label htmlFor="mypage-language">
                사용 언어
              </label>

              {isEditing ? (
                <select
                  id="mypage-language"
                  className="mypage-input mypage-select"
                  value={language}
                  onChange={(e) =>
                    setLanguage(e.target.value as Language)
                  }
                >
                  <option value="ko">한국어</option>
                  <option value="en">English</option>
                  <option value="ja">日本語</option>
                </select>
              ) : (
                <div className="mypage-field-value">
                  {LANGUAGE_LABELS[user.language]}
                </div>
              )}
            </div>

          </div>

          {/* 수정 버튼 */}

          {isEditing && (
            <div className="mypage-edit-actions">
              <button
                type="button"
                className="mypage-cancel-button"
                disabled={isSaving}
                onClick={handleCancel}
              >
                취소
              </button>

              <button
                type="button"
                className="mypage-primary-button"
                disabled={isSaving}
                onClick={handleSave}
              >
                {isSaving ? "저장 중..." : "변경사항 저장"}
              </button>
            </div>
          )}

        </section>

        {/* =========================
            Account Management
        ========================= */}

        <section className="mypage-section mypage-account-section">

          <div className="mypage-section-heading">
            <h2>계정 관리</h2>
          </div>

          <div className="mypage-account-row">
            <div>
              <h3>로그아웃</h3>
              <p>현재 계정에서 로그아웃합니다.</p>
            </div>

            <button
              type="button"
              className="mypage-outline-button"
              onClick={handleLogout}
            >
              로그아웃
            </button>
          </div>

          <div className="mypage-account-row">
            <div>
              <h3>회원 탈퇴</h3>
              <p>
                탈퇴 시 계정 정보가 삭제되며 복구할 수 없습니다.
              </p>
            </div>

            <button
              type="button"
              className="mypage-danger-button"
              onClick={() => {
                setWithdrawPassword("");
                setWithdrawError("");
                setShowWithdrawModal(true);
              }}
            >
              회원 탈퇴
            </button>
          </div>

        </section>

      </div>
      {/* 회원 탈퇴 모달 */}
      {showWithdrawModal && (
        <div
          className="mypage-modal-overlay"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget && !isWithdrawing) {
              setShowWithdrawModal(false);
              setWithdrawPassword("");
              setWithdrawError("");
            }
          }}
        >
          <div
            className="mypage-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="withdraw-modal-title"
          >
            <div className="mypage-modal-icon">
              !
            </div>

            <h2 id="withdraw-modal-title">
              정말 탈퇴하시겠어요?
            </h2>

            <p className="mypage-modal-description">
              회원 탈퇴 시 계정 정보와 찜한 문학 목록이
              <br />
              모두 삭제되며 복구할 수 없습니다.
            </p>

            <div className="mypage-modal-notice">
              탈퇴를 진행하려면 현재 비밀번호를 입력해주세요.
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                void handleWithdraw();
              }}
            >
              <label
                htmlFor="withdraw-password"
                className="mypage-modal-label"
              >
                비밀번호 확인
              </label>

              <input
                id="withdraw-password"
                type="password"
                className="mypage-modal-input"
                placeholder="현재 비밀번호 입력"
                autoComplete="current-password"
                value={withdrawPassword}
                onChange={(e) => {
                  setWithdrawPassword(e.target.value);
                  setWithdrawError("");
                }}
                disabled={isWithdrawing}
                autoFocus
                required
              />

              {withdrawError && (
                <p className="mypage-modal-error" role="alert">
                  {withdrawError}
                </p>
              )}

              <div className="mypage-modal-actions">
                <button
                  type="button"
                  className="mypage-modal-cancel"
                  disabled={isWithdrawing}
                  onClick={() => {
                    setShowWithdrawModal(false);
                    setWithdrawPassword("");
                    setWithdrawError("");
                  }}
                >
                  취소
                </button>

                <button
                  type="submit"
                  className="mypage-modal-confirm"
                  disabled={!withdrawPassword.trim() || isWithdrawing}
                >
                  {isWithdrawing ? "탈퇴 처리 중..." : "회원 탈퇴"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

// =========================
// Icons
// =========================

function UserIcon() {
  return (
    <svg
      width="62"
      height="62"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21v-2a8 8 0 0 1 16 0v2" />
    </svg>
  );
}

function CameraIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 7h4l2-3h6l2 3h4v13H3V7Z" />
      <circle cx="12" cy="13" r="4" />
    </svg>
  );
}

function EditIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L9 17l-4 1 1-4 10.5-10.5Z" />
    </svg>
  );
}