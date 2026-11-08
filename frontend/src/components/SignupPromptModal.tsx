"use client";

import Link from "next/link";
import { useEffect } from "react";
import "./signup-prompt-modal.css";

type Props = {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
};

export default function SignupPromptModal({
  open,
  onClose,
  title = "로그인이 필요한 기능이에요",
  description = "회원가입하고 마음에 드는 문학 작품을 찜해 보세요.",
}: Props) {
  useEffect(() => {
    if (!open) return;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="signup-prompt-overlay" onClick={onClose}>
      <div
        className="signup-prompt"
        role="dialog"
        aria-modal="true"
        aria-labelledby="signup-prompt-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          className="signup-prompt-close"
          aria-label="닫기"
          onClick={onClose}
        >
          ✕
        </button>

        <div className="signup-prompt-icon" aria-hidden="true">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path
              d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78Z"
              fill="currentColor"
            />
          </svg>
        </div>

        <h2 id="signup-prompt-title" className="signup-prompt-title">
          {title}
        </h2>
        <p className="signup-prompt-description">{description}</p>

        <div className="signup-prompt-actions">
          <Link href="/signup" className="signup-prompt-primary">
            회원가입하기
          </Link>
          <Link href="/login" className="signup-prompt-secondary">
            이미 계정이 있어요 · 로그인
          </Link>
        </div>
      </div>
    </div>
  );
}