"use client";

import "./search.css";
import {
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const STORAGE_KEY = "prequel_recent_searches";

type Content = {
  id: number;
  title: string;
  type: "영화" | "드라마";
  genre: string;
  platform?: string;
  poster?: string;
};

const mockContents: Content[] = [
  {
    id: 1,
    title: "미스터 션샤인",
    type: "드라마",
    genre: "시대극",
    platform: "Netflix",
    poster: "/images/mr-sunshine.jpg",
  },
  {
    id: 2,
    title: "미스터 고",
    type: "영화",
    genre: "코미디",
  },
  {
    id: 3,
    title: "미스터 주",
    type: "영화",
    genre: "코미디",
  },
  {
    id: 4,
    title: "미스터 기간제",
    type: "드라마",
    genre: "스릴러",
  },
  {
    id: 5,
    title: "1987",
    type: "영화",
    genre: "드라마",
  },
  {
    id: 6,
    title: "극한직업",
    type: "영화",
    genre: "코미디",
  },
];

export default function SearchPage() {
  const router = useRouter();

  const [keyword, setKeyword] = useState("");
  const [searchedKeyword, setSearchedKeyword] =
    useState("");

  const [recentSearches, setRecentSearches] =
    useState<string[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (!saved) return;

    try {
      setRecentSearches(JSON.parse(saved));
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const updateRecentSearches = (items: string[]) => {
    setRecentSearches(items);

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(items)
    );
  };

  const addRecentSearch = (value: string) => {
    const updated = [
      value,
      ...recentSearches.filter(
        (item) => item !== value
      ),
    ].slice(0, 10);

    updateRecentSearches(updated);
  };

  const handleSearch = (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    const value = keyword.trim();

    if (!value) return;

    addRecentSearch(value);

    setSearchedKeyword(value);
  };

  const handleRecentSearch = (value: string) => {
    setKeyword(value);

    addRecentSearch(value);

    setSearchedKeyword(value);
  };

  const handleDelete = (target: string) => {
    updateRecentSearches(
      recentSearches.filter(
        (item) => item !== target
      )
    );
  };

  const handleClearKeyword = () => {
    setKeyword("");
    setSearchedKeyword("");
  };

  const searchResults = useMemo(() => {
    if (!searchedKeyword) {
      return [];
    }

    const normalizedKeyword =
      searchedKeyword.toLowerCase();

    return mockContents.filter((content) =>
      content.title
        .toLowerCase()
        .includes(normalizedKeyword)
    );
  }, [searchedKeyword]);

  const hasSearched = searchedKeyword !== "";

  return (
    <main className="search-page">
      <div className="search-page-inner">
        <div className="search-page-top">
          <button
            type="button"
            className="close-button"
            onClick={() => router.push("/")}
            aria-label="검색 닫기"
          >
            ×
          </button>
        </div>

        <form
          className="search-page-form"
          onSubmit={handleSearch}
        >
          <input
            type="search"
            value={keyword}
            onChange={(event) => {
              setKeyword(event.target.value);
            }}
            placeholder="당신이 재미있게 본 K-콘텐츠를 검색해보세요!"
            autoFocus
          />

          {keyword && (
            <button
              type="button"
              className="search-clear-button"
              onClick={handleClearKeyword}
              aria-label="검색어 지우기"
            >
              ×
            </button>
          )}

          <button
            type="submit"
            className="search-submit-button"
            aria-label="검색"
          >
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
        </form>

        {!hasSearched ? (
          <section className="recent-search-section">
            <div className="recent-search-heading">
              <h2>최근 검색어</h2>

              {recentSearches.length > 0 && (
                <button
                  type="button"
                  onClick={() =>
                    updateRecentSearches([])
                  }
                >
                  전체 삭제
                </button>
              )}
            </div>

            {recentSearches.length === 0 ? (
              <p className="empty-recent">
                최근 검색어가 없습니다.
              </p>
            ) : (
              <ul className="recent-search-list">
                {recentSearches.map((item) => (
                  <li key={item}>
                    <button
                      type="button"
                      className="recent-keyword"
                      onClick={() =>
                        handleRecentSearch(item)
                      }
                    >
                      {item}
                    </button>

                    <button
                      type="button"
                      className="recent-delete"
                      onClick={() =>
                        handleDelete(item)
                      }
                      aria-label={`${item} 삭제`}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : searchResults.length > 0 ? (
          <section className="search-results">
            <div className="search-results-heading">
              <h2>검색 결과</h2>

              <span>
                {searchResults.length}개
              </span>
            </div>

            <div className="search-result-grid">
              {searchResults.map((content) => (
                <Link
                  key={content.id}
                  href={`/k-contents/${content.id}/recommendations`}
                  className="search-result-card"
                >
                  <div className="search-result-poster">
                    {content.poster ? (
                      <img
                        src={content.poster}
                        alt={`${content.title} 포스터`}
                      />
                    ) : (
                      <div className="poster-placeholder">
                        {content.title}
                      </div>
                    )}
                  </div>

                  <div className="search-result-info">
                    <h3>{content.title}</h3>

                    <p>
                      <span>{content.type}</span>
                      <span className="separator">·</span>
                      <span>{content.genre}</span>

                      {content.platform && (
                        <>
                          <span className="separator">·</span>
                          <span>{content.platform}</span>
                        </>
                      )}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        ) : (
          <section className="search-empty">
            <div className="search-empty-content">
              <svg
                width="42"
                height="42"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M11 19A8 8 0 1 0 11 3a8 8 0 0 0 0 16ZM21 21l-4.35-4.35"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>

              <h2>검색 결과가 없어요.</h2>

              <p>
                다른 제목으로 다시 검색해보세요.
              </p>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}