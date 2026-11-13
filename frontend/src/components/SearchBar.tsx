"use client";

import { useRouter } from "next/navigation";

export default function SearchBar() {
  const router = useRouter();

  return (
    <button
      type="button"
      className="home-search-bar"
      onClick={() => router.push("/search")}
    >
      <span>당신이 재미있게 본 K-콘텐츠를 검색해보세요!</span>

      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
      >
        <path
          d="M11 19A8 8 0 1 0 11 3a8 8 0 0 0 0 16ZM21 21l-4.35-4.35"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    </button>
  );
}