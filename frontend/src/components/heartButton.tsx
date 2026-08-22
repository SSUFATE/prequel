"use client";

import { useState } from "react";
import { addFavorite, removeFavorite } from "@/api/favorites";

interface HeartButtonProps {
  workId: number;
  initialIsFavorite?: boolean;
}

export default function HeartButton({
  workId,
  initialIsFavorite = false,
}: HeartButtonProps) {
  const [isFavorite, setIsFavorite] = useState(initialIsFavorite);
  const [isLoading, setIsLoading] = useState(false);

  const toggleFavorite = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (isLoading) return;

    const previousState = isFavorite;
    const nextState = !isFavorite;


    setIsFavorite(nextState);
    setIsLoading(true);

    try {
      if (nextState) {
        await addFavorite(workId);
      } else {
        await removeFavorite(workId);
      }
    } catch (err) {
      setIsFavorite(previousState);
      alert(err instanceof Error ? err.message : "처리에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      type="button"
      className={`heart-button ${isFavorite ? "heart-button--active" : ""}`}
      aria-label={isFavorite ? "찜 해제" : "찜하기"}
      onClick={toggleFavorite}
      disabled={isLoading}
      style={{
        background: "none",
        border: "none",
        cursor: "pointer",
        padding: "4px",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <svg
        width="22"
        height="22"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 20.5s-7.5-4.35-10-9.02C0.4 8.1 2.2 4.5 5.7 4.5c2 0 3.6 1.1 4.3 2.7.7-1.6 2.3-2.7 4.3-2.7 3.5 0 5.3 3.6 3.7 6.98C19.5 16.15 12 20.5 12 20.5Z"
          fill={isFavorite ? "#E5484D" : "none"}
          stroke={isFavorite ? "#E5484D" : "currentColor"}
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
}