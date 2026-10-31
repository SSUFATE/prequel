import Link from "next/link";
import SearchBar from "@/components/SearchBar";
import ContentCard from "@/components/ContentCard";
import { getHomeSections } from "@/api/kcontents";
import ContentSlider from "@/components/ContentSlider";

export default async function Home() {
  const { sections } = await getHomeSections();

  return (
    <main className="home">
      <section className="hero-section">
        <div className="hero-content">
          <h1>
            좋아하는 K-콘텐츠와 닮은
            <br className="mobile-hide" />
            한국 문학을 만나보세요
          </h1>

          <p className="hero-description">
            재미있게 본 영화를 검색하면
            <br className="mobile-hide" />
            비슷한 분위기와 주제를 가진 한국 문학을 추천해드려요.
          </p>

          <SearchBar />
        </div>
      </section>

      {/* 장르·개봉 연도별 콘텐츠 섹션 */}
      {sections.map((section) => (
        <section
          key={section.key}
          className="popular-section"
        >
          <div className="section-heading">
            <h2>{section.title}</h2>
          </div>

          <ContentSlider contents={section.contents} />
        </section>
      ))}
    </main>
  );
}