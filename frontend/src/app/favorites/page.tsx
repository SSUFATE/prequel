"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import "./favorite.css";
import { getMyFavoriteWorks, removeFavorite, type FavoriteWorkResponse } from "@/api/favorites";

type favoriteBook = {
  id: string;
  title: string;
  author: string;
  publishedYear: string;
};

function toFavoriteBook(fav: FavoriteWorkResponse): favoriteBook {
  return {
    id: String(fav.work_id),
    title: fav.title,
    author: fav.author ?? "저자 미상",
    publishedYear: fav.era ?? "",
  };
}

export default function favoritePage() {
  const [books, setBooks] = useState<favoriteBook[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getMyFavoriteWorks()
      .then((data) => {
        if (cancelled) return;
        setBooks(data.map(toFavoriteBook));
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "찜 목록을 불러오지 못했어요.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleRemove = async (id: string) => {
    const removedBook = books.find((b) => b.id === id);
    setBooks((prev) => prev.filter((book) => book.id !== id));

    try {
      await removeFavorite(Number(id));
    } catch (err) {
      if (removedBook) {
        setBooks((prev) => [...prev, removedBook]);
      }
      alert(err instanceof Error ? err.message : "찜 해제에 실패했어요.");
    }
  };

  return (
    <div className="favorite-page">

      <main className="favorite-main">
        <h1 className="favorite-title">찜</h1>

        {isLoading ? (
          <p style={{ textAlign: "center", padding: "40px 0", color: "#999" }}>불러오는 중...</p>
        ) : error ? (
          <p style={{ textAlign: "center", padding: "40px 0", color: "#E5484D" }}>{error}</p>
        ) : books.length === 0 ? (
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