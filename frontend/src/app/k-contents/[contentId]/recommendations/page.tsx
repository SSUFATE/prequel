"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import "./recommendations.css";

type Theme =
  | "ALL"
  | "ERA_SETTING"
  | "GENRE"
  | "SUBJECT"
  | "EMOTIONAL"
  | "RELATIONSHIP"
  | "CULTURAL_CONTEXT";

type Recommendation = {
  workId: number;
  title: string;
  author: string;
  literaryType: string;
  publicationYear?: number;
  poster?: string;
  similarityScore: number;
  categoryScores: Partial<Record<Exclude<Theme, "ALL">, number>>;
  tags: string[];
  description?: string;
};

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
    key: "EMOTIONAL",
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

/* API 연결 전 임시 콘텐츠 */
const selectedContent = {
  id: 1,
  title: "미스터 션샤인",
  type: "드라마",
  genre: "시대극",
  platform: "Netflix",
  poster: "/images/mr-sunshine.jpg",
};

/* API 연결 전 임시 추천 목록 */
const recommendations: Recommendation[] = [
  {
    workId: 1,
    title: "토지",
    author: "박경리",
    literaryType: "장편소설",
    publicationYear: 1969,
    poster: "/images/toji.jpg",
    similarityScore: 0.74,

    categoryScores: {
      ERA_SETTING: 0.82,
      GENRE: 0.55,
      SUBJECT: 0.78,
      EMOTIONAL: 0.68,
      RELATIONSHIP: 0.62,
      CULTURAL_CONTEXT: 0.81,
    },

    tags: ["일제강점기", "공동체", "역사", "가족"],

    description:
      "격변하는 시대 속에서 개인과 공동체가 살아가는 모습을 함께 담고 있어요.",
  },

  {
    workId: 2,
    title: "태백산맥",
    author: "조정래",
    literaryType: "장편소설",
    publicationYear: 1983,
    similarityScore: 0.68,

    categoryScores: {
      ERA_SETTING: 0.88,
      GENRE: 0.58,
      SUBJECT: 0.72,
      EMOTIONAL: 0.6,
      RELATIONSHIP: 0.54,
      CULTURAL_CONTEXT: 0.77,
    },

    tags: ["역사", "이념갈등", "공동체"],

    description:
      "한국 근현대사의 갈등을 중심으로 인물과 사회의 관계를 깊게 다뤄요.",
  },

  {
    workId: 3,
    title: "무정",
    author: "이광수",
    literaryType: "장편소설",
    publicationYear: 1917,
    similarityScore: 0.61,

    categoryScores: {
      ERA_SETTING: 0.72,
      GENRE: 0.42,
      SUBJECT: 0.58,
      EMOTIONAL: 0.64,
      RELATIONSHIP: 0.71,
      CULTURAL_CONTEXT: 0.52,
    },

    tags: ["근대", "사랑", "갈등"],

    description:
      "근대 사회의 변화 속에서 사랑과 가치관의 충돌을 그린 작품이에요.",
  },
];

export default function RecommendationPage() {
  const router = useRouter();

  const [selectedTheme, setSelectedTheme] =
    useState<Theme>("ALL");

  const [sortOrder, setSortOrder] =
    useState<"similarity" | "title">("similarity");

  const filteredRecommendations = useMemo(() => {
    let result = [...recommendations];

    /*
      전체가 아니라 테마 선택 시
      해당 테마 점수가 있는 추천만 보여줌

      추후 백엔드에서 테마별 추천 목록을
      따로 받아오면 이 부분은 API 호출로 교체 가능
    */
    if (selectedTheme !== "ALL") {
      result = result.filter(
        (item) =>
          (item.categoryScores[selectedTheme] ?? 0) > 0
      );

      result.sort(
        (a, b) =>
          (b.categoryScores[selectedTheme] ?? 0) -
          (a.categoryScores[selectedTheme] ?? 0)
      );
    }

    if (
      selectedTheme === "ALL" &&
      sortOrder === "similarity"
    ) {
      result.sort(
        (a, b) =>
          b.similarityScore -
          a.similarityScore
      );
    }

    if (sortOrder === "title") {
      result.sort((a, b) =>
        a.title.localeCompare(b.title, "ko")
      );
    }

    return result;
  }, [selectedTheme, sortOrder]);

  const selectedThemeLabel =
    themes.find(
      (theme) => theme.key === selectedTheme
    )?.label ?? "전체";

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
            {selectedContent.poster ? (
              <img
                src={selectedContent.poster}
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
              {selectedContent.type}
              <span>·</span>
              {selectedContent.genre}

              {selectedContent.platform && (
                <>
                  <span>·</span>
                  {selectedContent.platform}
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
        {filteredRecommendations.length > 0 ? (
          <section className="recommendation-list">
            {filteredRecommendations.map(
              (item) => {
                const score =
                  selectedTheme === "ALL"
                    ? item.similarityScore
                    : item.categoryScores[
                        selectedTheme
                      ] ?? 0;

                return (
                  <article
                    key={item.workId}
                    className="recommendation-card"
                    onClick={() =>
                      router.push(
                        `/literatures/${item.workId}`
                      )
                    }
                  >
                    <div className="literature-poster">
                      {item.poster ? (
                        <img
                          src={item.poster}
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
                            <span>·</span>
                            {item.literaryType}

                            {item.publicationYear && (
                              <>
                                <span>·</span>
                                {item.publicationYear}
                              </>
                            )}
                          </p>
                        </div>

                        <span className="similarity-badge">
                          {Math.round(score * 100)}%
                          유사
                        </span>
                      </div>

                      {item.description && (
                        <p className="recommendation-reason">
                          {item.description}
                        </p>
                      )}

                      <div className="literature-tags">
                        {item.tags.map((tag) => (
                          <span key={tag}>
                            # {tag}
                          </span>
                        ))}
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
                          item.workId
                        );
                      }}
                    >
                      ♡
                    </button>
                  </article>
                );
              }
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