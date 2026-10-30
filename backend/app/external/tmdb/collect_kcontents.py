import time
from datetime import date

import app.models

from app.database import SessionLocal
from app.domains.kcontents.model import KContent
from app.external.tmdb.client import TMDbClient
from app.external.tmdb.converter import movie_to_dto
from app.external.tmdb.service import save_kcontent


MOVIE_GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "로맨스": 10749,
    "범죄": 80,
    "스릴러": 53,
    "미스터리": 9648,
    "공포": 27,
    "SF": 878,
    "판타지": 14,
    "역사": 36,
    "가족": 10751,
    "애니메이션": 16,
}

MAX_MOVIES = 1200

START_YEAR = 2000
END_YEAR = date.today().year

PAGES_PER_YEAR = 10
PAGES_PER_GENRE = 10

SORT_OPTIONS = [
    "popularity.desc",
    "primary_release_date.desc",
]

REQUEST_DELAY = 0.2


def collect_movies():
    client = TMDbClient()
    db = SessionLocal()

    created_count = 0
    skipped_count = 0
    failed_count = 0

    current_count = (
        db.query(KContent)
        .filter(KContent.content_type == "MOVIE")
        .count()
    )

    remaining = max(0, MAX_MOVIES - current_count)

    print(f"현재 영화: {current_count}편")
    print(f"추가 수집 목표: {remaining}편")

    if remaining == 0:
        db.close()
        print("이미 최대 영화 수에 도달했습니다.")
        return

    # 기존 DB에 저장된 TMDb ID
    existing_ids = {
        tmdb_id
        for (tmdb_id,) in db.query(KContent.tmdb_id).all()
        if tmdb_id is not None
    }

    # 동일 실행 중 중복 조회 방지
    processed_ids = set(existing_ids)

    def collect_page(
        page: int,
        year: int | None = None,
        genre_id: int | None = None,
        sort_by: str = "popularity.desc",
    ) -> bool:
        nonlocal created_count, skipped_count, failed_count

        if created_count >= remaining:
            return False

        try:
            data = client.get_korean_movies(
                page=page,
                genre_id=genre_id,
                year=year,
                sort_by=sort_by,
            )

        except Exception as e:
            failed_count += 1
            print(f"[목록 조회 실패] page={page}: {e}")
            return False

        movies = data.get("results", [])

        if not movies:
            return False

        for movie in movies:
            if created_count >= remaining:
                return False

            tmdb_id = movie.get("id")

            if tmdb_id is None:
                skipped_count += 1
                continue

            if tmdb_id in processed_ids:
                skipped_count += 1
                continue

            processed_ids.add(tmdb_id)

            try:
                details = client.get_movie_details(tmdb_id)

                release_date = details.get("release_date")

                # 개봉일이 없거나 아직 개봉하지 않은 영화 제외
                if not release_date:
                    skipped_count += 1
                    continue

                if release_date > date.today().isoformat():
                    skipped_count += 1
                    continue

                # 성인물 및 미개봉 영화 제외
                if details.get("adult", False):
                    skipped_count += 1
                    continue

                if details.get("status") != "Released":
                    skipped_count += 1
                    continue

                # 한국 영화 여부 확인
                production_countries = {
                    country.get("iso_3166_1")
                    for country in details.get(
                        "production_countries", []
                    )
                }

                if (
                    "KR" not in production_countries
                    and details.get("original_language") != "ko"
                ):
                    skipped_count += 1
                    continue

                providers = client.get_movie_watch_providers(
                    tmdb_id
                )

                dto = movie_to_dto(details, providers)

                kcontent, created = save_kcontent(db, dto)

                if created:
                    created_count += 1

                    print(
                        f"[{current_count + created_count}/{MAX_MOVIES}] "
                        f"{kcontent.content_id} / {kcontent.title}"
                    )
                else:
                    skipped_count += 1

            except Exception as e:
                db.rollback()
                failed_count += 1
                print(f"[저장 실패] {tmdb_id}: {e}")

            time.sleep(REQUEST_DELAY)

        return page < data.get("total_pages", page)

    try:
        # 1. 연도별 수집
        # 여러 연도에서 1페이지씩 먼저 수집하여 연도 편중 완화
        for page in range(1, PAGES_PER_YEAR + 1):
            if created_count >= remaining:
                break

            for year in range(END_YEAR, START_YEAR - 1, -1):
                if created_count >= remaining:
                    break

                for sort_by in SORT_OPTIONS:
                    if created_count >= remaining:
                        break

                    print(
                        f"[연도별] {year}년 / "
                        f"{sort_by} / {page}페이지"
                    )

                    collect_page(
                        page=page,
                        year=year,
                        sort_by=sort_by,
                    )

                    time.sleep(REQUEST_DELAY)

        # 2. 장르별 수집
        if created_count < remaining:
            for genre_name, genre_id in MOVIE_GENRES.items():
                if created_count >= remaining:
                    break

                print(f"\n===== {genre_name} 장르 수집 =====")

                for page in range(1, PAGES_PER_GENRE + 1):
                    if created_count >= remaining:
                        break

                    has_next = collect_page(
                        page=page,
                        genre_id=genre_id,
                    )

                    if not has_next:
                        break

                    time.sleep(REQUEST_DELAY)

    finally:
        db.close()

    print("\n===== 영화 수집 완료 =====")
    print(f"기존 영화: {current_count}편")
    print(f"신규 저장: {created_count}편")
    print(f"최종 영화: {current_count + created_count}편")
    print(f"중복 및 제외: {skipped_count}건")
    print(f"실패: {failed_count}건")


if __name__ == "__main__":
    collect_movies()