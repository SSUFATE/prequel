"use client";

import "./search.css";
import {
  FormEvent,
  useEffect,
  useState,
} from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getKContents } from "@/api/kcontents";
import type { KContent } from "@/types/kcontent";

const STORAGE_KEY = "prequel_recent_searches";

// 검색어 색칠 함수
const highlightMatch = (
  title: string,
  keyword: string
) => {
  const normalizedKeyword = keyword.trim();

  if (!normalizedKeyword) {
    return title;
  }

  const index = title
    .toLowerCase()
    .indexOf(normalizedKeyword.toLowerCase());

  if (index === -1) {
    return title;
  }

  return (
    <>
      {title.slice(0, index)}

      <span className="suggestion-highlight">
        {title.slice(
          index,
          index + normalizedKeyword.length
        )}
      </span>

      {title.slice(
        index + normalizedKeyword.length
      )}
    </>
  )
}

export default function SearchPage() {
  const router = useRouter();

  const [keyword, setKeyword] = useState("");
  const [searchedKeyword, setSearchedKeyword] =
    useState("");

  const [recentSearches, setRecentSearches] =
    useState<string[]>([]);

  const [searchResults, setSearchResults] = useState<KContent[]>([]);
  const [suggestions, setSuggestions] = useState<KContent[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 자동완성 조회
  useEffect(() => {
    const value = keyword.trim();

    if (!value) {
      setSuggestions([]);
      return;
    }

    let cancelled = false;

    const timer = setTimeout(async () => {
      try {
        const data = await getKContents({
          search: value,
          page: 1,
          size: 5,
        });

        if (!cancelled) {
          setSuggestions(data.items);
        }
      } catch (error) {
        console.error("자동완성 검색 실패:", error);

        if (!cancelled) {
          setSuggestions([]);
        }
      }
    }, 250);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [keyword]);

  // 자동완성 목록이 바뀔 때 선택값 초기화
  useEffect(() => {
    setSelectedIndex(-1);
  }, [suggestions]);

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

  const searchContents = async (
    value: string
  ) => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await getKContents({
        search: value,
        page: 1,
        size: 20,
      });

      setSearchResults(data.items);
      setTotal(data.total);
      setSearchedKeyword(value);
    } catch (error) {
      console.error("K-콘텐츠 검색 실패:", error);

      setSearchResults([]);
      setTotal(0);
      setError("검색 중 오류가 발생했어요.");
    } finally{
      setIsLoading(false);
    }
  }

  const handleSearch = async(
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    const value = keyword.trim();

    if (!value) return;

    addRecentSearch(value);
    setSuggestions([]);

    await searchContents(value);
  };

  const handleRecentSearch = async (
    value: string
  ) => {
    setKeyword(value);

    addRecentSearch(value);

    await searchContents(value);
  };

  // 자동완성 클릭 함수
  const handleSuggestionClick = (
    content: KContent
  ) => {
    addRecentSearch(content.title);
    setSuggestions([]);
    setSelectedIndex(-1);

    router.push(
      `/k-contents/${content.content_id}/recommendations`
    );
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
    setSearchResults([]);
    setSuggestions([]);
    setTotal(0);
    setError(null);
  };

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

        <div className="search-input-area">
          <form
            className="search-page-form"
            onSubmit={handleSearch}
          >
            <input
              type="search"
              value={keyword}
              onChange={(event) => {
                setKeyword(event.target.value);

                setSearchedKeyword("");
                setSearchResults([]);
                setTotal(0);
                setError(null);
              }}
              onKeyDown={(event) => {
                if (suggestions.length === 0) return;

                if (event.key === "ArrowDown") {
                  event.preventDefault();

                  setSelectedIndex((prev) => 
                    prev < suggestions.length -1 
                      ? prev + 1
                      : 0
                  ); 
                }

                if (event.key === "ArrowUp") {
                  event.preventDefault();

                  setSelectedIndex((prev) =>
                    prev > 0
                      ? prev - 1
                      : suggestions.length - 1
                  );
                }

                if (
                  event.key === "Enter" &&
                  selectedIndex >= 0
                ) {
                  event.preventDefault();

                  handleSuggestionClick(
                    suggestions[selectedIndex]
                  );
                }

                if (event.key === "Escape") {
                  setSuggestions([]);
                  setSelectedIndex(-1);
                }
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

        {/* 자동완성 검색어 제안 */}
        {keyword.trim() &&
          !hasSearched &&
          suggestions.length > 0 && (
            <div className="search-suggestions">
              {suggestions.map((content, index) => (
                <button
                  key={content.content_id}
                  type="button"
                  className={`search-suggestion-item ${
                    selectedIndex === index ? "selected" : ""
                  }`}
                  onMouseEnter={() => 
                    setSelectedIndex(index)
                  }
                  onClick={() =>
                    handleSuggestionClick(content)
                  }
                >
                  <span className="suggestion-title">
                    {highlightMatch(content.title, keyword)}
                  </span>

                  <span className="suggestion-meta">
                    {content.content_type === "MOVIE"
                      ? "영화"
                      : content.content_type === "DRAMA"
                      ? "드라마"
                      : "웹툰"}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>  

        {!hasSearched && !keyword.trim() && (
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
        )}

        {hasSearched && searchResults.length > 0 && (
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
                  key={content.content_id}
                  href={`/k-contents/${content.content_id}/recommendations`}
                  className="search-result-card"
                >
                  <div className="search-result-poster">
                    {content.poster_url ? (
                      <img
                        src={content.poster_url}
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
                      <span>{content.content_type === 
                      "MOVIE"
                        ? "영화"
                        : "드라마"}
                      </span>
                      
                      {content.release_date && (
                        <>
                          <span className="separator">·</span>
                          <span>
                            {new Date(
                              content.release_date
                            ).getFullYear()}
                          </span>
                        </>
                      )}

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
        )}

        {hasSearched &&
          !isLoading &&
          searchResults.length === 0 && (
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