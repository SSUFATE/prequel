"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useParams } from "next/navigation";

import "./recommendations.css";

import { getKContentById } from "@/api/kcontents";
import { getRecommendations } from "@/api/recommendations";

import type { KContent } from "@/types/kcontent"
import type {
  Recommendation,
  TagCategory,
} from "@/types/recommendation";

type Theme = "ALL" | TagCategory;

const themes: {
  key: Theme;
  label: string;
}[] = [
  {
    key: "ALL",
    label: "전체",
  },
  {
    key: "ERA_SETTING",
    label: "시대·배경",
  },
  {
    key: "GENRE",
    label: "장르",
  },
  {
    key: "SUBJECT",
    label: "소재·주제",
  },
  {
    key: "MOOD",
    label: "정서",
  },
  {
    key: "RELATIONSHIP",
    label: "관계",
  },
  {
    key: "CULTURAL_CONTEXT",
    label: "문화맥락",
  },
];


export default function RecommendationPage() {
  const router = useRouter();

  const params = useParams<{
    contentId: string;
  }>();

  const contentId = Number(params.contentId);

  const [selectedContent, setSelectedContent] = 
    useState<KContent | null>(null);

  const [recommendations, setRecommendations] = 
    useState<Recommendation[]>([]);

  const [selectedTheme, setSelectedTheme] =
    useState<Theme>("ALL");

  const [sortOrder, setSortOrder] =
    useState<"similarity" | "title">("similarity");

  const [isContentLoading, setIsContentLoading] = 
    useState(true);

  const [isRecommendationsLoading, setIsRecommendationsLoading] =
    useState(true);

  const [error, setError] = useState<string | null>(null);

  // 선택한 K콘텐츠 조회
  useEffect(() => {
    if (!Number.isFinite(contentId)) return;

    const fetchContent = async () => {
      try {
        setIsContentLoading(true);
        setError(null);

        const data = await getKContentById(contentId);

        setSelectedContent(data);
      } catch (error) {
        console.error("K콘텐츠 조회 실패:", error);

        setError("K콘텐츠 정보를 불러오지 못했어요.");
      } finally {
        setIsContentLoading(false);
      }
    }

    fetchContent();
  }, [contentId]);

  // 전체 / 테마별 추천 문학 목록 조회
  useEffect(() => {
    if (!Number.isFinite(contentId)) return;

    const fetchRecommendations = async() => {
      try {
        setIsRecommendationsLoading(true);
        setError(null);

        const data = await getRecommendations(
          contentId,
          {
            limit: 20,
            category:
              selectedTheme === "ALL"
                ? undefined
                : selectedTheme,
          }
        );

        console.log("추천 API 응답:", data);
        console.log(
          "recommendations 배열?",
          Array.isArray(data.recommendations)
        );

        setRecommendations(data.recommendations);
      } catch (error) {
        console.error("추천 목록 조회 실패:", error);

        setRecommendations([]);

        setError("추천 작품을 불러오지 못했어요.");
      } finally {
        setIsRecommendationsLoading(false);
      }
    };

    fetchRecommendations();
  }, [contentId, selectedTheme]);

  // 백엔드 api에서 기본 유사도 정렬을 함
  // 제목 순을 선택했을 때만 프론트에서 정렬
  const sortedRecommendations = useMemo(() => {
    const result = [...recommendations];

    if (sortOrder === "title") {
      result.sort((a, b) =>
        a.title.localeCompare(b.title, "ko")
      );
    }

    if (sortOrder === "similarity") {
      result.sort((a, b) => 
        b.similarity_score -
        a.similarity_score
      )
    }

    return result;
  }, [recommendations, sortOrder]);

  const selectedThemeLabel = 
    themes.find(
      (theme) => theme.key === selectedTheme
    )?.label ?? "전체";

  if (isContentLoading) {
    return (
      <main className="recommendation-page">
        <div className="recommendation-inner">
          <p>콘텐츠 정보를 불러오는 중...</p>
        </div>
      </main>
    );
  }

  if (!selectedContent) {
    return (
      <main className="recommendation-page">
        <div className="recommendation-inner">
          <p>콘텐츠 정보를 찾을 수 없어요.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="recommendation-page">
      <div className="recommendation-inner">

        {/* 뒤로가기 */}
        <button
          type="button"
          className="recommendation-back"
          onClick={() => router.back()}
        >
          <span aria-hidden="true">←</span>
          검색 결과로 돌아가기
        </button>

        {/* 선택한 K 콘텐츠 */}
        <section className="selected-content">
          <div className="selected-content-poster">
            {selectedContent.poster_url ? (
              <img
                src={selectedContent.poster_url}
                alt={`${selectedContent.title} 포스터`}
              />
            ) : (
              <div className="selected-content-placeholder" />
            )}
          </div>

          <div className="selected-content-info">
            <span className="selected-content-label">
              선택한 K-콘텐츠
            </span>

            <h1>{selectedContent.title}</h1>

            <p>
              {selectedContent.content_type ===
              "MOVIE"
                ? "영화"
                : "드라마"
              }

              {selectedContent.release_date && (
                <>
                  <span>·</span>
                  {new Date(
                    selectedContent.release_date
                  ).getFullYear()}
                </>
              )}
            </p>
          </div>
        </section>

        {/* 제목 */}
        <section className="recommendation-heading">
          <p className="recommendation-eyebrow">
            문학 추천
          </p>

          <h2>
            <strong>
              &apos;{selectedContent.title}&apos;
            </strong>
            과 닮은 한국 문학이에요.
          </h2>

          <p>
            분위기와 시대적 배경, 주제, 관계 등을
            바탕으로 비슷한 작품을 찾아봤어요.
          </p>
        </section>

        {/* 테마 필터 */}
        <div className="recommendation-toolbar">
          <div
            className="theme-filter"
            role="group"
            aria-label="추천 테마"
          >
            {themes.map((theme) => (
              <button
                type="button"
                key={theme.key}
                className={
                  selectedTheme === theme.key
                    ? "theme-button active"
                    : "theme-button"
                }
                onClick={() =>
                  setSelectedTheme(theme.key)
                }
              >
                {theme.label}
              </button>
            ))}
          </div>

          <select
            className="recommendation-sort"
            value={sortOrder}
            onChange={(event) =>
              setSortOrder(
                event.target.value as
                  | "similarity"
                  | "title"
              )
            }
            aria-label="정렬 기준"
          >
            <option value="similarity">
              유사도 순
            </option>

            <option value="title">
              제목 순
            </option>
          </select>
        </div>

        {/* 현재 테마 설명 */}
        {selectedTheme !== "ALL" && (
          <p className="theme-description">
            <strong>{selectedThemeLabel}</strong>
            테마를 기준으로 유사한 작품이에요.
          </p>
        )}

        {/* 추천 목록 */}
        {isRecommendationsLoading ? (
          <section className="recommendation-empty">
            <p>추천 작품을 불러오는 중...</p>
          </section>
        ) : error ? (
          <section className="recommendation-empty">
            <p>{error}</p>
          </section>
        ) : sortedRecommendations.length > 0 ?(
          <section className="recommendation-list">
            {sortedRecommendations.map(
              (item) => (
                <article
                  key={item.work_id}
                  className="recommendation-card"
                  onClick={() =>
                    router.push(
                      `/literatures/${item.work_id}`
                    )
                  }
                >
                  <div className="literature-poster">
                      {item.cover_url ? (
                        <img
                          src={item.cover_url}
                          alt={`${item.title} 표지`}
                        />
                      ) : (
                        <div className="literature-placeholder">
                          {item.title}
                        </div>
                      )}
                    </div>

                    <div className="literature-main">
                      <div className="literature-title-row">
                        <div>
                          <h3>{item.title}</h3>

                          <p className="literature-meta">
                            {item.author}

                            {item.genre && (
                              <>
                                <span>·</span>
                                {item.genre}
                              </>
                            )}

                            {item.published_year && (
                              <>
                                <span>·</span>
                                {item.published_year}
                              </>
                            )}
                          </p>
                        </div>

                        <span className="similarity-badge">
                          {Math.round(
                            item.similarity_score * 
                            100
                          )}
                          % 유사
                        </span>
                      </div>

                      {item.summary && (
                        <p className="recommendation-reason">
                          {item.summary}
                        </p>
                      )}

                      <div className="literature-tags">
                        {item.matched_tags.map(
                          (tag) => (
                            <span 
                              key={tag.tag_id}
                            >
                              # {tag.name}
                            </span>
                          )
                        )}
                      </div>
                    </div>

                    <button
                      type="button"
                      className="favorite-button"
                      aria-label={`${item.title} 찜하기`}
                      onClick={(event) => {
                        event.stopPropagation();

                        console.log(
                          "찜:",
                          item.work_id
                        );
                      }}
                    >
                      ♡
                    </button>
                  </article>
              )
            )}
          </section>
        ) : (
          <section className="recommendation-empty">
            <div>
              <h3>
                아직 이 콘텐츠와 연결된 책이
                없어요.
              </h3>

              <p>
                다른 테마를 선택하거나 다른
                K-콘텐츠를 검색해보세요.
              </p>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}