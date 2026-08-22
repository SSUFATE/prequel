"use client";

import { use, useEffect, useState } from "react";
import "./literature-detail.css";
import { addFavorite, removeFavorite } from "@/api/favorites";

type TagCategory =
  | "ERA_SETTING"
  | "GENRE"
  | "SUBJECT"
  | "MOOD"
  | "RELATIONSHIP"
  | "CULTURAL_CONTEXT";

type LiteratureTag = {
  tag_id: number;
  name: string;
  category: TagCategory;
  literature_weight: number;
  is_matched: boolean;
};

type RecommendationDetail = {
  content_id: number;
  work_id: number;
  similarity_score: number;
  category_scores: Partial<Record<TagCategory, number>>;
  literature_tags: LiteratureTag[];
};

type LiteraryWork = {
  work_id: number;
  title: string;
  author: string | null;
  summary: string | null;
  genre: string | null;
  main_genre: string | null;
  sub_genre: string | null;
  era: string | null;
  published_year: number | null;
  isbn13: string | null;
  cover_url: string | null;
  literature_type: string | null;
  source: string | null;
  is_favorite?: boolean;
  created_at: string;
};

type Translation = {
  translation_id?: number;
  work_id?: number;
  language?: string | null;
  translated_title?: string | null;
  title?: string | null;
  translator?: string | null;
  publisher?: string | null;
  isbn?: string | null;
  isbn13?: string | null;
  purchase_url?: string | null;
  cover_url?: string | null;
  cover_image?: string | null;
  published_year?: number | null;
  publication_year?: number | null;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const CATEGORY_LABELS: Record<TagCategory, string> = {
  ERA_SETTING: "시대·배경",
  GENRE: "장르",
  SUBJECT: "소재·주제",
  MOOD: "정서",
  RELATIONSHIP: "관계",
  CULTURAL_CONTEXT: "문화 맥락",
};

const CATEGORY_ORDER: TagCategory[] = [
  "ERA_SETTING",
  "GENRE",
  "SUBJECT",
  "MOOD",
  "RELATIONSHIP",
  "CULTURAL_CONTEXT",
];

const tabs = [
  { id: "intro", label: "책 소개" },
  { id: "translation", label: "번역본 정보" },
  { id: "timeline", label: "시대연표 및 인물관계도" },
] as const;

type TabId = (typeof tabs)[number]["id"];

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API 요청 실패 (${res.status}): ${path}`);
  }
  return res.json();
}

function buildRecommendationCopy(
  categoryScores: Partial<Record<TagCategory, number>> = {},
  literatureTags: LiteratureTag[] = []
) {
  const topCategories = CATEGORY_ORDER.filter((c) => categoryScores[c] !== undefined)
    .sort((a, b) => (categoryScores[b] ?? 0) - (categoryScores[a] ?? 0))
    .slice(0, 2)
    .map((c) => CATEGORY_LABELS[c]);

  const sharedTagNames = literatureTags
    .filter((t) => t.is_matched)
    .slice(0, 4)
    .map((t) => t.name);

  const line1 =
    topCategories.length > 0
      ? `${topCategories.join(", ")}에서 특히 닮아 있어요.`
      : "여러 테마에서 닮은 점이 있어요.";
  const line2 =
    sharedTagNames.length > 0
      ? `두 작품은 ${sharedTagNames.join(", ")} 등의 키워드를 공통으로 가지고 있어요.`
      : "";

  return {
    heading: "추천 포인트",
    description: [line1, line2].filter(Boolean).join("\n"),
  };
}

export default function LiteratureDetailPage({
  params,
}: {
  params: Promise<{ contentId: string; workId: string }>;
}) {
  const resolvedParams = use(params);
  const { contentId, workId } = resolvedParams;

  const [activeTab, setActiveTab] = useState<TabId>("intro");
  const [liked, setLiked] = useState(false);
  const [isLikingLoading, setIsLikingLoading] = useState(false);

  const [work, setWork] = useState<LiteraryWork | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationDetail | null>(null);
  const [translations, setTranslations] = useState<Translation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [workData, recommendationData, translationData] = await Promise.all([
          fetchJSON<LiteraryWork>(`/literatures/${workId}`),
          fetchJSON<RecommendationDetail>(
            `/k-contents/${contentId}/recommendations/${workId}`
          ),
          fetchJSON<Translation[]>(`/translations/${workId}`).catch(() => [] as Translation[]),
        ]);

        if (cancelled) return;
        setWork(workData);
        setLiked(workData.is_favorite ?? false);
        setRecommendation(recommendationData);
        setTranslations(Array.isArray(translationData) ? translationData : []);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "데이터를 불러오지 못했어요.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [contentId, workId]);

  const handleTabClick = (id: TabId) => {
    setActiveTab(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleToggleLike = async () => {
    if (isLikingLoading || !work) return;

    const previousLiked = liked;
    const nextLiked = !liked;

    setLiked(nextLiked);
    setIsLikingLoading(true);

    try {
      if (nextLiked) {
        await addFavorite(work.work_id);
      } else {
        await removeFavorite(work.work_id);
      }
    } catch (err) {
      setLiked(previousLiked);
      alert(err instanceof Error ? err.message : "처리에 실패했습니다.");
    } finally {
      setIsLikingLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="detail-page">
        <div className="detail-body">
          <p className="detail-body-text">불러오는 중이에요...</p>
        </div>
      </div>
    );
  }

  if (error || !work || !recommendation) {
    return (
      <div className="detail-page">
        <div className="detail-body">
          <button
            type="button"
            className="detail-back-button"
            aria-label="뒤로 가기"
            onClick={() => window.history.back()}
          >
            <BackIcon />
          </button>
          <p className="detail-body-text">{error ?? "작품 정보를 찾을 수 없어요."}</p>
        </div>
      </div>
    );
  }

  const matchPercent = Math.round((recommendation.similarity_score ?? 0) * 100);
  const { heading: matchHeading, description: matchDescription } = buildRecommendationCopy(
    recommendation.category_scores ?? {},
    recommendation.literature_tags ?? []
  );

  const themeSimilarities = CATEGORY_ORDER.map((c) => ({
    label: CATEGORY_LABELS[c],
    value: Math.round(((recommendation.category_scores ?? {})[c] ?? 0) * 100),
  }));

  const keywordTags = [...(recommendation.literature_tags ?? [])]
    .sort((a, b) => Number(b.is_matched) - Number(a.is_matched))
    .map((tag) => ({
      label: tag.name,
      type: tag.is_matched ? ("shared" as const) : ("unique" as const),
    }));

  const primaryTranslation =
    translations.find((t) => t.language?.toLowerCase() === "en" || t.language?.toLowerCase() === "english") ??
    translations[0] ??
    null;

  const translationTitle = primaryTranslation?.translated_title ?? primaryTranslation?.title ?? "-";
  const translationCover = primaryTranslation?.cover_url ?? primaryTranslation?.cover_image ?? null;
  const translationYear = primaryTranslation?.published_year ?? primaryTranslation?.publication_year ?? "-";
  const translationIsbn = primaryTranslation?.isbn ?? primaryTranslation?.isbn13 ?? "-";

  return (
    <div className="detail-page">
      <div className="detail-body">
        <button
          type="button"
          className="detail-back-button"
          aria-label="뒤로 가기"
          onClick={() => window.history.back()}
        >
          <BackIcon />
        </button>

        <div className="detail-content">
          {/* Overview card */}
          <section className="detail-card">
            <div className="detail-overview">
              <div
                className="detail-cover"
                style={
                  work.cover_url
                    ? {
                        backgroundImage: `url(${work.cover_url})`,
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                      }
                    : undefined
                }
              >
                {!work.cover_url && (
                  <>
                    <span className="detail-cover-eyebrow">
                      {work.literature_type ?? work.main_genre ?? ""}
                    </span>
                    <span className="detail-cover-title">{work.title}</span>
                    {work.summary && (
                      <p className="detail-cover-tagline">{work.summary}</p>
                    )}
                  </>
                )}
              </div>

              <div className="detail-info">
                <div className="detail-info-header">
                  <div>
                    <h1 className="detail-title">{work.title}</h1>
                    <p className="detail-subtitle">
                      {[work.author, work.literature_type ?? work.main_genre, work.published_year]
                        .filter(Boolean)
                        .join(" · ")}
                    </p>
                  </div>
                  <button
                    type="button"
                    className={`heart-button-lg ${liked ? "heart-button-lg--active" : ""}`}
                    aria-label={liked ? "찜 해제" : "찜하기"}
                    onClick={handleToggleLike}
                    disabled={isLikingLoading}
                    style={{ color: liked ? "#E5484D" : "inherit" }}
                  >
                    <HeartIcon filled={liked} />
                  </button>
                </div>

                <section className="similarity-section">
                  <h2 className="section-label">K-콘텐츠와의 유사도</h2>
                  <div className="similarity-box">
                    <DonutChart percent={matchPercent} />
                    <div className="similarity-text">
                      <p className="similarity-heading">{matchHeading}</p>
                      <p className="similarity-desc">
                        {matchDescription.split("\n").map((line, i) => (
                          <span key={i}>
                            {line}
                            <br />
                          </span>
                        ))}
                      </p>
                    </div>
                  </div>
                </section>
              </div>
            </div>

            <hr className="detail-divider" />

            <section className="reason-section">
              <h2 className="section-label">추천 이유</h2>
              <div className="reason-grid">
                <div>
                  <h3 className="reason-subtitle">6대 테마별 유사도</h3>
                  <ul className="theme-bar-list">
                    {themeSimilarities.map((theme) => (
                      <li key={theme.label} className="theme-bar-row">
                        <span className="theme-bar-label">{theme.label}</span>
                        <div className="theme-bar-track">
                          <div
                            className="theme-bar-fill"
                            style={{ width: `${theme.value}%` }}
                          />
                        </div>
                        <span className="theme-bar-value">{theme.value}%</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="reason-subtitle">키워드로 보는 연결점</h3>
                  <div className="keyword-tags">
                    {keywordTags.map((keyword, i) => (
                      <span
                        key={`${keyword.label}-${i}`}
                        className={`keyword-tag keyword-tag--${keyword.type}`}
                      >
                        # {keyword.label}
                      </span>
                    ))}
                  </div>
                  <ul className="keyword-legend">
                    <li>
                      <span className="legend-dot legend-dot--shared" />K-콘텐츠와 공통 키워드
                    </li>
                    <li>
                      <span className="legend-dot legend-dot--unique" />
                      문학 작품 고유 키워드
                    </li>
                  </ul>
                </div>
              </div>
            </section>
          </section>

          {/* Tabbed detail card */}
          <section className="detail-card">
            <nav className="detail-tabs" role="tablist">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  className={`detail-tab ${activeTab === tab.id ? "detail-tab--active" : ""}`}
                  onClick={() => handleTabClick(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </nav>

            <section id="intro" className="detail-section">
              <h2 className="section-label">책 소개</h2>
              <p className="detail-body-text">
                {work.summary
                  ? work.summary.split("\n").map((line, i) => (
                      <span key={i}>
                        {line}
                        <br />
                      </span>
                    ))
                  : "아직 등록된 줄거리가 없어요."}
              </p>

              <div className="ai-grid">
                <div className="ai-box">
                  <h3 className="ai-box-title">AI 3줄 요약</h3>
                  <div className="ai-box-placeholder">아직 준비 중인 기능이에요.</div>
                </div>
                <div className="ai-box">
                  <h3 className="ai-box-title">AI 작품 이해 포인트</h3>
                  <div className="ai-box-placeholder">아직 준비 중인 기능이에요.</div>
                </div>
              </div>
            </section>

            <hr className="detail-divider" />

            <section id="translation" className="detail-section">
              <h2 className="section-label">번역본 정보</h2>
              {primaryTranslation ? (
                <div className="translation-row" style={{ display: "flex", alignItems: "center", gap: "24px" }}>
                  <div
                    className="translation-thumb"
                    style={{
                      width: "140px",
                      height: "200px",
                      flexShrink: 0,
                      borderRadius: "8px",
                      backgroundColor: "#f5f5f5",
                      ...(translationCover
                        ? {
                            backgroundImage: `url(${translationCover})`,
                            backgroundSize: "contain",
                            backgroundRepeat: "no-repeat",
                            backgroundPosition: "center",
                          }
                        : {}),
                    }}
                  />
                  <dl className="translation-list">
                    <div className="translation-item">
                      <dt>번역본 제목</dt>
                      <dd>{translationTitle}</dd>
                    </div>
                    <div className="translation-item">
                      <dt>언어</dt>
                      <dd>{primaryTranslation.language ?? "-"}</dd>
                    </div>
                    <div className="translation-item">
                      <dt>번역가</dt>
                      <dd>{primaryTranslation.translator ?? "-"}</dd>
                    </div>
                    <div className="translation-item">
                      <dt>출판사</dt>
                      <dd>{primaryTranslation.publisher ?? "-"}</dd>
                    </div>
                    <div className="translation-item">
                      <dt>출판 연도</dt>
                      <dd>{translationYear}</dd>
                    </div>
                    <div className="translation-item">
                      <dt>ISBN</dt>
                      <dd>{translationIsbn}</dd>
                    </div>
                    <div className="translation-item">
                      <dt>구매 링크</dt>
                      <dd>
                        {primaryTranslation.purchase_url ? (
                          <a
                            href={primaryTranslation.purchase_url}
                            className="translation-link"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            바로 가기
                          </a>
                        ) : (
                          "-"
                        )}
                      </dd>
                    </div>
                  </dl>
                </div>
              ) : (
                <div className="ai-box-placeholder">등록된 번역본 정보가 없어요.</div>
              )}
            </section>

            <hr className="detail-divider" />

            <section id="timeline" className="detail-section">
              <h2 className="section-label">시대연표 및 인물관계도</h2>
              <div className="timeline-grid">
                <div>
                  <h3 className="reason-subtitle">시대 연표</h3>
                  <div className="ai-box-placeholder">아직 준비 중인 기능이에요.</div>
                </div>
                <div>
                  <h3 className="reason-subtitle">인물 관계도</h3>
                  <div className="ai-box-placeholder">아직 준비 중인 기능이에요.</div>
                </div>
              </div>
            </section>
          </section>
        </div>
      </div>
    </div>
  );
}

function DonutChart({ percent }: { percent: number }) {
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;

  return (
    <div className="donut-chart">
      <svg width="104" height="104" viewBox="0 0 104 104">
        <circle cx="52" cy="52" r={radius} fill="none" stroke="#FBDACB" strokeWidth="10" />
        <circle
          cx="52"
          cy="52"
          r={radius}
          fill="none"
          stroke="#FF6A3D"
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 52 52)"
        />
      </svg>
      <span className="donut-chart-label">{percent}%</span>
    </div>
  );
}

function BackIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M15 5l-7 7 7 7"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
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