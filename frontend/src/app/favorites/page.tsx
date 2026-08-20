"use client";

import Link from "next/link";
import { useState } from "react";
import "./favorite.css";

type favoriteBook = {
  id: string;
  title: string;
  author: string;
  publishedYear: string;
};

//API 연동 시 이 목데이터를 서버에서 받아온 찜 목록으로 교체.
const mockfavoriteBooks: favoriteBook[] = [
  { id: "1", title: "토지", author: "박경리", publishedYear: "1994" },
  { id: "2", title: "토지", author: "박경리", publishedYear: "1994" },
  { id: "3", title: "토지", author: "박경리", publishedYear: "1994" },
  { id: "4", title: "토지", author: "박경리", publishedYear: "1994" },
  { id: "5", title: "토지", author: "박경리", publishedYear: "1994" },
];

export default function favoritePage() {
  const [books, setBooks] = useState<favoriteBook[]>(mockfavoriteBooks);

  const handleRemove = (id: string) => {
    setBooks((prev) => prev.filter((book) => book.id !== id));
  };

  return (
    <div className="favorite-page">
      {/* <header className="favorite-header">
        <Link href="/" className="favorite-logo">
          Prequel
        </Link>

        <nav className="favorite-nav">
          <button type="button" className="nav-text-link">
            로그아웃
          </button>
          <Link href="/favorite" className="nav-text-link nav-text-link--active">
            찜
          </Link>
          <button type="button" className="icon-button" aria-label="마이페이지">
            <UserIcon />
          </button>
        </nav>
      </header> */}

      <main className="favorite-main">
        <h1 className="favorite-title">찜</h1>

        {books.length === 0 ? (
          <EmptyState />
        ) : (
          <ul className="favorite-grid">
            {books.map((book) => (
              <li key={book.id}>
                <BookCard book={book} onRemove={() => handleRemove(book.id)} />
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}

function BookCard({
  book,
  onRemove,
}: {
  book: favoriteBook;
  onRemove: () => void;
}) {
  return (
    <Link href={`/literatures/${book.id}`} className="book-card">
      <div className="book-cover">
        <span className="book-cover-eyebrow">장편소설</span>
        <span className="book-cover-title">{book.title}</span>
        <p className="book-cover-tagline">
          한 집안 4세대 걸쳐 한국의 근현대사를 담아낸
          <br />
          우리 시대 최고의 고전
        </p>
        <div className="book-cover-footer">
          <span className="book-cover-chip" />
          <span className="book-cover-chip" />
        </div>
      </div>

      <div className="book-info">
        <p className="book-title">
          {book.title}
          <button
            type="button"
            className="heart-button heart-button--active"
            aria-label="찜 해제"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onRemove();
            }}
          >
            <HeartIcon filled />
          </button>
        </p>
        <p className="book-meta">
          {book.author} · {book.publishedYear}
        </p>
      </div>
    </Link>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <p className="empty-state-text">
        찜한 책이 없어요
        <br />
        지금 찜을 시작해보세요!
      </p>
      <BookmarkIcon />
    </div>
  );
}

function UserIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
      <path
        d="M4 20c0-3.3137 3.134-6 7-6h2c3.866 0 7 2.6863 7 6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function HeartIcon({ filled = false }: { filled?: boolean }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M12 20.5s-7.5-4.35-10-9.02C0.4 8.1 2.2 4.5 5.7 4.5c2 0 3.6 1.1 4.3 2.7.7-1.6 2.3-2.7 4.3-2.7 3.5 0 5.3 3.6 3.7 6.98C19.5 16.15 12 20.5 12 20.5Z"
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function BookmarkIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M6 3.5h12a1 1 0 0 1 1 1V21l-7-4.2L5 21V4.5a1 1 0 0 1 1-1Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}