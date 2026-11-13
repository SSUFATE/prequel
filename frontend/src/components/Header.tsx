"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/app/lib/authContext";
import { getAccessToken, logout as apiLogout } from "@/app/lib/api";

export default function Header() {
  const { isLoggedIn, isLoading, logout } = useAuth();

  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    handleScroll();

    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  async function handleLogout() {
    const token = getAccessToken();
    if (token) {
      try {
        await apiLogout(token);
      } catch {
      }
    }
    logout();
  }

  if (isLoading) {
    return (
      <header className={`site-header ${scrolled ? "scrolled" : ""}`}>
        <div className="header-inner">
          <Link href="/" className="logo">
            <span className="logo-icon" aria-hidden="true">📚</span>
            <span>Prequel</span>
          </Link>
          <nav className="header-nav" />
        </div>
      </header>
    );
  }

  return (
    <header className={`site-header ${scrolled ? "scrolled" : ""}`}>
      <div className="header-inner">
        <Link href="/" className="logo">
          <span className="logo-icon" aria-hidden="true">
            📚
          </span>
          <span>Prequel</span>
        </Link>

        <nav className="header-nav">
          {!isLoggedIn ? (
            <>
              <Link href="/signup">회원가입</Link>
              <Link href="/login">로그인</Link>
            </>
          ) : (
            <>
              <button type="button" className="text-button" onClick={handleLogout}>
                로그아웃
              </button>

              <Link href="/favorites">찜</Link>

              <Link href="/mypage" className="profile-button" aria-label="마이페이지">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.7" />
                  <path
                    d="M5.5 19c.8-3.2 3.2-5 6.5-5s5.7 1.8 6.5 5"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinecap="round"
                  />
                </svg>
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}