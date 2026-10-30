"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import "./favorite.css";

import {
  getMyFavoriteWorks,
  removeFavorite,
  type FavoriteWorkResponse,
} from "@/api/favorites";

type FavoriteBook = {
  id: number;
  title: string;
  author: string;
  genre: string;
  era: string;
  coverUrl: string | null;
};

function toFavoriteBook(fav: FavoriteWorkResponse): FavoriteBook {
  return {
    id: fav.work_id,
    title: fav.title,
    author: fav.author ?? "저자 미상",
    genre: fav.genre ?? "",
    era: fav.era ?? "",
    coverUrl: fav.cover_url,
  };
}

export default function FavoritePage() {
  const [books, setBooks] = useState<FavoriteBook[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removingIds, setRemovingIds] = useState<number[]>([]);

  useEffect(() => {
    let cancelled = false;

    getMyFavoriteWorks()
      .then((data) => {
        if (cancelled) return;
        setBooks(data.map(toFavoriteBook));
      })
      .catch((err) => {
        if (cancelled) return;

        setError(
          err instanceof Error
            ? err.message
            : "찜 목록을 불러오지 못했어요."
        );
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleRemove = async (id: number) => {
    if (removingIds.includes(id)) return;

    setRemovingIds((prev) => [...prev, id]);

    try {
      await removeFavorite(id);

      setBooks((prev) =>
        prev.filter((book) => book.id !== id)
      );
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "찜 해제에 실패했어요."
      );
    } finally {
      setRemovingIds((prev) =>
        prev.filter((removingId) => removingId !== id)
      );
    }
  };

  return (
    <div className="favorite-page">
      <main className="favorite-main">

        {/* 페이지 제목 */}
        <div className="favorite-heading">
          <div>
            <span className="favorite-eyebrow">
              MY LIBRARY
            </span>

            <h1 className="favorite-title">
              찜한 문학
            </h1>

            <p className="favorite-description">
              마음에 드는 문학 작품을 한곳에 모아보세요.
            </p>
          </div>

          {!isLoading && !error && books.length > 0 && (
            <span className="favorite-count">
              총 <strong>{books.length}</strong>개의 작품
            </span>
          )}
        </div>

        {/* 찜 목록 */}
        {isLoading ? (
          <div className="favorite-message">
            찜 목록을 불러오는 중...
          </div>
        ) : error ? (
          <div className="favorite-message favorite-error">
            {error}
          </div>
        ) : books.length === 0 ? (
          <EmptyState />
        ) : (
          <ul className="favorite-grid">
            {books.map((book) => (
              <li key={book.id}>
                <BookCard
                  book={book}
                  isRemoving={removingIds.includes(book.id)}
                  onRemove={() => handleRemove(book.id)}
                />
              </li>
            ))}
          </ul>
        )}

      </main>
    </div>
  );
}

/* ==============================
   Book Card
============================== */

function BookCard({
  book,
  onRemove,
  isRemoving,
}: {
  book: FavoriteBook;
  onRemove: () => void;
  isRemoving: boolean;
}) {
  const [imageError, setImageError] = useState(false);

  return (
    <article className="book-card">

      {/* 책 상세 페이지 이동 */}
      <Link
        href={`/literatures/${book.id}`}
        className="book-card-link"
      >

        {/* 책 표지 */}
        <div className="book-cover">
          {book.coverUrl && !imageError ? (
            <img
              src={book.coverUrl}
              alt={`${book.title} 표지`}
              className="book-cover-image"
              onError={() => setImageError(true)}
            />
          ) : (
            <div className="book-cover-placeholder">
              <span>BOOK TORI</span>
              <strong>{book.title}</strong>
            </div>
          )}
        </div>

        {/* 책 정보 */}
        <div className="book-info">

          <h2 className="book-title">
            {book.title}
          </h2>

          <p className="book-author">
            {book.author}
          </p>

          {book.genre && (
            <p className="book-genre">
              {book.genre}
            </p>
          )}

        </div>
      </Link>

      {/* 찜 해제 버튼 */}
      <button
        type="button"
        className="heart-button heart-button--active"
        aria-label={`${book.title} 찜 해제`}
        disabled={isRemoving}
        onClick={onRemove}
      >
        <HeartIcon filled />
      </button>

    </article>
  );
}

/* ==============================
   Empty State
============================== */

function EmptyState() {
  return (
    <div className="empty-state">

      <div className="empty-state-icon">
        <HeartIcon />
      </div>

      <h2 className="empty-state-title">
        아직 찜한 문학이 없어요
      </h2>

      <p className="empty-state-text">
        마음에 드는 작품을 발견하면
        <br />
        하트를 눌러 저장해 보세요.
      </p>

      <Link href="/" className="empty-state-button">
        작품 찾아보기 →
      </Link>

    </div>
  );
}

/* ==============================
   Heart Icon
============================== */

function HeartIcon({
  filled = false,
}: {
  filled?: boolean;
}) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78Z"
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}