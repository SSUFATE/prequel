import app.models

from app.database import SessionLocal
from app.external.tmdb.client import TMDbClient
from app.external.tmdb.converter import movie_to_dto, tv_to_dto
from app.external.tmdb.service import save_kcontent

# 장르별 수집
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
}

# 영화 수집
# 11개 장르 x page 당 최대 20개 = page 당 220건
def collect_movies_by_genre(
    pages_per_genre: int = 5,
):
    client = TMDbClient()
    db = SessionLocal()

    try:
        for genre_name, genre_id in MOVIE_GENRES.items():

            print(f"\n===== {genre_name} 수집 시작 =====")

            for page in range(1, pages_per_genre + 1):

                movies = client.get_korean_movies(
                    page=page,
                    genre_id=genre_id,
                )

                if not movies:
                    break

                print(
                    f"[{genre_name}] page {page}"
                )

                for movie in movies:
                    tmdb_id = movie["id"]

                    try:
                        details = client.get_movie_details(
                            tmdb_id
                        )

                        providers = (
                            client.get_movie_watch_providers(
                                tmdb_id
                            )
                        )

                        dto = movie_to_dto(
                            details,
                            providers,
                        )

                        result = save_kcontent(
                            db,
                            dto,
                        )

                        print(
                            f"저장/확인: {result.title}"
                        )

                    except Exception as e:
                        db.rollback()

                        print(
                            f"실패: {tmdb_id} / {e}"
                        )

    finally:
        db.close()


# 전체 영화 수집
def collect_movies(
    start_page: int = 1,
    end_page: int = 100,
):
    client = TMDbClient()
    db = SessionLocal()

    try:
        for page in range(start_page, end_page + 1):

            movies = client.get_korean_movies(page=page)

            if not movies:
                break

            print(f"[MOVIE] page {page}")

            for movie in movies:
                tmdb_id = movie["id"]

                try:
                    details = client.get_movie_details(tmdb_id)

                    providers = (
                        client.get_movie_watch_providers(tmdb_id)
                    )

                    dto = movie_to_dto(
                        details,
                        providers,
                    )

                    result, created = save_kcontent(
                        db,
                        dto,
                    )

                    if created:
                        print(f"신규 저장: {result.title}")
                    else:
                        print(f"중복 건너뜀: {result.title}")

                except Exception as e:
                    db.rollback()
                    print(f"실패: {tmdb_id} / {e}")

    finally:
        db.close()


# 드라마 수집
def collect_dramas(
    start_page: int = 1,
    end_page: int = 50,
):
    client = TMDbClient()
    db = SessionLocal()

    try:
        for page in range(start_page, end_page + 1):

            contents = client.get_korean_tv_contents(
                page=page
            )

            if not contents:
                break

            print(f"[DRAMA] page {page}")

            for content in contents:
                tmdb_id = content["id"]

                try:
                    details = client.get_tv_details(
                        tmdb_id
                    )

                    providers = (
                        client.get_tv_watch_providers(
                            tmdb_id
                        )
                    )

                    dto = tv_to_dto(
                        details,
                        providers,
                    )

                    result = save_kcontent(
                        db,
                        dto,
                    )

                    print(
                        f"저장: {result.title}"
                    )

                except Exception as e:
                    print(
                        f"실패: {tmdb_id} / {e}"
                    )

    finally:
        db.close()

# 영화만 수집
if __name__ == "__main__":
    collect_movies(
        start_page=1,
        end_page=100,
    )