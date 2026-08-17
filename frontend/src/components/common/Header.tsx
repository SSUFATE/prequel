"use client";

import Link from "next/link";

export default function Header() {
  // 임시값: 나중에 실제 로그인 상태로 교체
  const isLoggedIn = true;

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link href="/" className="logo">
          Prequel
        </Link>

        <nav className="header-nav">
          {isLoggedIn ? (
            <>
              <button type="button" className="logout-button">
                로그아웃
              </button>

              <Link href="/favorites">
                찜
              </Link>

              <Link
                href="/mypage"
                className="profile-link"
                aria-label="마이페이지"
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="9"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  />
                  <circle
                    cx="12"
                    cy="9"
                    r="2.5"
                    fill="currentColor"
                  />
                  <path
                    d="M7.5 17C8.4 14.8 10 13.7 12 13.7C14 13.7 15.6 14.8 16.5 17"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </Link>
            </>
          ) : (
            <>
              <Link href="/signup">회원가입</Link>
              <Link href="/login">로그인</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}