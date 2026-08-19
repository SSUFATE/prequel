import Link from "next/link";
import SearchBar from "@/components/SearchBar";
import ContentCard from "@/components/ContentCard";
import { popularContents } from "@/data/mockContents";

export default function Home() {
  return (
    <main className="home">
      <section className="hero-section">
        <div className="hero-content">
          <p className="hero-label">Prequel</p>

          <h1>
            좋아했던 K-콘텐츠와 닮은
            <br className="mobile-hide" />
            한국 문학을 만나보세요.
          </h1>

          <p className="hero-description">
            재미있게 본 영화나 드라마를 검색하면
            <br className="mobile-hide" />
            비슷한 분위기와 주제를 가진 한국 문학을 추천해드려요.
          </p>

          <SearchBar />
        </div>
      </section>

      <section className="popular-section">
        <div className="section-heading">
          <h2>지금 많이 찾는 K 콘텐츠</h2>

          <Link href="/search" className="more-link">
            더 보기
            <span>›</span>
          </Link>
        </div>

        <div className="content-grid">
          {popularContents.map((content) => (
            <ContentCard
              key={content.id}
              title={content.title}
            />
          ))}
        </div>
      </section>
    </main>
  );
}