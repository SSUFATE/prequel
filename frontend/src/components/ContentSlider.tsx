"use client";

import { useRef, useState, useEffect } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import ContentCard from "@/components/ContentCard";
import type { HomeContent } from "@/types/kcontent";

interface ContentSliderProps {
  contents: HomeContent[];
}

export default function ContentSlider({ contents }: ContentSliderProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // 스크롤 가능 여부 확인
  const updateScrollButtons = () => {
    const container = scrollRef.current;
    if (!container) return;

    setCanScrollLeft(container.scrollLeft > 1);
    setCanScrollRight(
      container.scrollLeft + container.clientWidth <
        container.scrollWidth - 1
    );
  };

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;

    updateScrollButtons();

    const observer = new ResizeObserver(updateScrollButtons);
    observer.observe(container);

    return () => observer.disconnect();
  }, [contents]);

  // 화살표 클릭 시 카드 목록 이동
  const handleScroll = (direction: "left" | "right") => {
    const container = scrollRef.current;
    if (!container) return;

    const scrollAmount = container.clientWidth * 0.8;

    container.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  };

  return (
    <div className="content-slider">
      {canScrollLeft && (
        <button
          type="button"
          className="slider-arrow slider-arrow-left"
          onClick={() => handleScroll("left")}
          aria-label="이전 콘텐츠"
        >
          <ChevronLeft size={26} strokeWidth={2} />
        </button>
      )}

      <div
        className="content-grid"
        ref={scrollRef}
        onScroll={updateScrollButtons}
      >
        {contents.map((content) => (
          <Link
            key={content.content_id}
            href={`/k-contents/${content.content_id}/recommendations`}
            className="content-card-link"
          >
            <ContentCard
              title={content.title}
              image={content.poster_url ?? undefined}
            />
          </Link>
        ))}
      </div>

      {canScrollRight && (
        <button
          type="button"
          className="slider-arrow slider-arrow-right"
          onClick={() => handleScroll("right")}
          aria-label="다음 콘텐츠"
        >
          <ChevronRight size={26} strokeWidth={2} />
        </button>
      )}
    </div>
  );
}