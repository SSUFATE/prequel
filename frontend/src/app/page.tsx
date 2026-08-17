import Link from "next/link";

const popularContents = Array.from({ length: 7 });

export default function Home() {
  return (
    <main className="home">
      <section className="hero">
        <p className="hero-label">Prequel</p>

        <h1 className="hero-title">
          좋아했던 K-콘텐츠와 닮은 한국 문학을 만나보세요.
          <br />
          재미있게 본 영화나 드라마를 검색해보세요.
        </h1>

        <form className="search-form">
          <input
            type="search"
            placeholder="당신이 재미있게 본 K-콘텐츠를 검색해보세요!"
            aria-label="K-콘텐츠 검색"
          />

          <button type="submit" aria-label="검색">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
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
      </section>

      <section className="popular-section">
        <div className="section-heading">
          <h2>지금 많이 찾는 K 콘텐츠</h2>

          <Link href="/search" className="more-link" aria-label="더 보기">
            ›
          </Link>
        </div>

        <div className="content-list">
          {popularContents.map((_, index) => (
            <div className="content-card" key={index}>
              <div className="poster-placeholder" />
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}