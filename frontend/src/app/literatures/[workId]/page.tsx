"use client";

import Link from "next/link";
import { useState } from "react";
import "./literature-detail.css";

type ThemeSimilarity = {
  label: string;
  value: number;
};

type KeywordTag = {
  label: string;
  type: "shared" | "unique";
};

//API 연동 시 params.id로 실제 문학 상세 데이터를 받아오도록 교체.
const mockBook = {
  title: "토지",
  author: "박경리",
  type: "장편소설",
  publishedYear: "1994",
  matchPercent: 87,
  matchHeading: "추천 포인트",
  matchDescription:
    "시대적 배경과 장르에서 특히 닮아 있어요.\n두 작품은 일제강점기, 전쟁, 농촌 등의 키워드를 공통으로 가지고 있어요.",
};

const themeSimilarities: ThemeSimilarity[] = [
  { label: "시대·배경", value: 87 },
  { label: "장르", value: 76 },
  { label: "소재·주제", value: 58 },
  { label: "정서", value: 37 },
  { label: "관계", value: 22 },
  { label: "문화 맥락", value: 13 },
];

const keywordTags: KeywordTag[] = [
  { label: "농촌", type: "shared" },
  { label: "일제강점기", type: "shared" },
  { label: "전쟁", type: "shared" },
  { label: "이산가족", type: "shared" },
  { label: "사랑", type: "unique" },
  { label: "가족", type: "unique" },
  { label: "신분제", type: "unique" },
  { label: "지리산", type: "unique" },
  { label: "토지", type: "unique" },
];

const tabs = [
  { id: "intro", label: "책 소개" },
  { id: "translation", label: "번역본 정보" },
  { id: "timeline", label: "시대연표 및 인물관계도" },
] as const;

type TabId = (typeof tabs)[number]["id"];

export default function LiteratureDetailPage({
  params,
}: {
  params: { workId: string };
}) {
  // params.workId — 지금은 목데이터만 쓰지만, API 연동 시 이 값으로 상세 데이터를 fetch.
  const [activeTab, setActiveTab] = useState<TabId>("intro");
  const [liked, setLiked] = useState(true);

  const handleTabClick = (id: TabId) => {
    setActiveTab(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

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
          {/* ---------- Overview card ---------- */}
          <section className="detail-card">
            <div className="detail-overview">
              <div className="detail-cover">
                <span className="detail-cover-eyebrow">{mockBook.type}</span>
                <span className="detail-cover-title">{mockBook.title}</span>
                <p className="detail-cover-tagline">
                  한 집안 4세대 걸쳐 한국의 근현대사를 담아낸
                  <br />
                  우리 시대 최고의 고전
                </p>
                <div className="detail-cover-footer">
                  <span className="detail-cover-chip" />
                  <span className="detail-cover-chip" />
                </div>
              </div>

              <div className="detail-info">
                <div className="detail-info-header">
                  <div>
                    <h1 className="detail-title">{mockBook.title}</h1>
                    <p className="detail-subtitle">
                      {mockBook.author} · {mockBook.type} · {mockBook.publishedYear}
                    </p>
                  </div>
                  <button
                    type="button"
                    className={`heart-button-lg ${liked ? "heart-button-lg--active" : ""}`}
                    aria-label={liked ? "찜 해제" : "찜하기"}
                    onClick={() => setLiked((prev) => !prev)}
                  >
                    <HeartIcon filled={liked} />
                  </button>
                </div>

                <section className="similarity-section">
                  <h2 className="section-label">K-콘텐츠와의 유사도</h2>
                  <div className="similarity-box">
                    <DonutChart percent={mockBook.matchPercent} />
                    <div className="similarity-text">
                      <p className="similarity-heading">{mockBook.matchHeading}</p>
                      <p className="similarity-desc">
                        {mockBook.matchDescription.split("\n").map((line, i) => (
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
                    {keywordTags.map((keyword) => (
                      <span
                        key={keyword.label}
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

          {/* ---------- Tabbed detail card ---------- */}
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
                줄거리를 작성하세요.
                <br />
                줄거리 줄거리 줄거리 줄거리...............................
                <br />
                줄거리
                <br />
                줄거리
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
              <div className="translation-row">
                <div className="translation-thumb" />
                <dl className="translation-list">
                  <div className="translation-item">
                    <dt>번역본 제목</dt>
                    <dd>토지</dd>
                  </div>
                  <div className="translation-item">
                    <dt>언어</dt>
                    <dd>영어</dd>
                  </div>
                  <div className="translation-item">
                    <dt>번역가</dt>
                    <dd>번역가</dd>
                  </div>
                  <div className="translation-item">
                    <dt>출판사</dt>
                    <dd>출판사</dd>
                  </div>
                  <div className="translation-item">
                    <dt>출판 연도</dt>
                    <dd>출판 연도</dd>
                  </div>
                  <div className="translation-item">
                    <dt>ISBN</dt>
                    <dd>1236</dd>
                  </div>
                  <div className="translation-item">
                    <dt>구매 링크</dt>
                    <dd>
                      <a href="#" className="translation-link">
                        바로 가기
                      </a>
                    </dd>
                  </div>
                </dl>
              </div>
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