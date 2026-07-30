### kcontent.csv 생성 스크립트

import csv
import json
from pathlib import Path

from app.external.tmdb.client import TMDbClient
from app.external.tmdb.converter import (
    movie_to_dto,
    tv_to_dto,
    dto_to_csv_row,
)

OUTPUT_PATH = Path("app/data/kcontents.csv")

FIELDNAMES = [
    "tmdb_id",
    "title",
    "content_type",
    "overview",
    "tmdb_genres",
    "runtime",
    "platform",
    "release_date",
    "poster_url",
    "source",
]

# 장르별로 후보 영화를 수집하기 위한 TMDb 영화 장르 ID
MOVIE_GENRES = {
    "드라마": 18,
    "코미디": 35,
    "로맨스": 10749,
    "역사": 36,
    "판타지": 14,
    "SF": 878,
    "공포": 27,
    "미스터리": 9648,
}

# 장르별 수집 작품 수
MOVIES_PER_GENRE = 7

# 직접 검색해서 수집할 작품
ADDITIONAL_MOVIES = [
    {
        "title": "살인의 추억",
        "year": 2003,
    },
    {
        "title": "괴물",
        "year": 2006,
    },
    {
        "title": "극한직업",
        "year": 2019,
    },
    {
        "title": "1987",
        "year": 2017,
    },
    {
        "title": "리틀 포레스트",
        "year": 2018,
    },
    {
        "title": "아이 캔 스피크",
        "year": 2017,
    },
    {
        "title": "변호인",
        "year": 2013,
    },
    {
        "title": "극한직업",
        "year": 2019,
    },
    {
        "title": "동주",
        "year": 2016,
    },
    {
        "title": "7번방의 선물",
        "year": 2013,
    },
    {
        "title": "수상한 그녀",
        "year": 2014,
    }, 
    {
        "title": "건축학개론",
        "year": 2012,
    }
]

# page_count: 1이면 최대 20개 작품 반환
def collect_movies(
    client: TMDbClient,
    genre_id: int,
    limit: int = MOVIES_PER_GENRE,
    page_count: int = 1,
) -> list[dict]:
    rows = []

    for page in range(1, page_count + 1):
        movies = client.get_korean_movies(
            page=page,
            genre_id=genre_id,
        )

        for movie in movies:
            if len(rows) >= limit:
                return rows
            
            tmdb_id = movie.get("id")

            if tmdb_id is None:
                continue
            
            try: 
                details = client.get_movie_details(tmdb_id)
                providers = client.get_movie_watch_providers(tmdb_id)

                dto = movie_to_dto(
                    details, 
                    providers,
                )

                rows.append(dto_to_csv_row(dto))
            
            except Exception as error:
                title = movie.get(
                    "title",
                    "제목 없음",
                )

                print(
                    f"[수집 실패] "
                    f"{title}({tmdb_id}): {error}"
                )

    return rows


def collect_tv_contents(
    client: TMDbClient,
    page_count: int = 1,
) -> list[dict]:
    rows = []

    for page in range(1, page_count + 1):
        tv_contents = client.get_korean_tv_contents(page)

        for tv_content in tv_contents:
            tmdb_id = tv_content["id"]

            details = client.get_tv_details(tmdb_id)
            providers = client.get_tv_watch_providers(tmdb_id)

            dto = tv_to_dto(details, providers)
            rows.append(dto_to_csv_row(dto))

    return rows

# 검색한 작품을 csv 행으로 변환
def collect_movie_by_title(
    client: TMDbClient,
    title: str,
    year: int | None = None,
) -> dict | None:
    search_results = client.search_movie(
        title=title,
        year=year,
    )

    if not search_results:
        print(f"[검색 실패] {title}")
        return None

    movie = search_results[0]
    tmdb_id = movie["id"]

    details = client.get_movie_details(tmdb_id)
    providers = client.get_movie_watch_providers(tmdb_id)

    dto = movie_to_dto(
        details,
        providers,
    )

    return dto_to_csv_row(dto)


def remove_duplicates(
    rows: list[dict],
) -> list[dict]:
    unique_rows = {}

    for row in rows:
        key = (
            row["tmdb_id"],
            row["content_type"],
        )

        unique_rows[key] = row

    return list(unique_rows.values())


def save_csv(
    rows: list[dict],
) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=FIELDNAMES,
        )

        writer.writeheader()

        for row in rows:
            csv_row = row.copy()

            csv_row["tmdb_genres"] = json.dumps(
                csv_row["tmdb_genres"],
                ensure_ascii=False,
            )

            writer.writerow(csv_row)


def main():
    client = TMDbClient()
    movie_rows = []

    # 장르별 자동 수집
    for genre_name, genre_id in MOVIE_GENRES.items():
        print(f"\n[{genre_name}] 수집 시작")

        genre_rows = collect_movies(
            client=client,
            genre_id=genre_id,
            limit=MOVIES_PER_GENRE,
            page_count=1,
        )

        movie_rows.extend(genre_rows)

        print(
            f"[{genre_name}] "
            f"{len(genre_rows)}개 수집 완료"
        )

    # tv_rows = collect_tv_contents(client)

    # rows = remove_duplicates(
    #     movie_rows + tv_rows
    # )

    # 특정 영화 제목으로 추가 수집
    for movie_info in ADDITIONAL_MOVIES:
        row = collect_movie_by_title(
            client=client,
            title=movie_info["title"],
            year=movie_info["year"],
        )

        if row is not None:
            movie_rows.append(row)
            print(f"[직접 추가] {movie_info['title']}")
    rows = remove_duplicates(movie_rows)

    save_csv(rows)

    print("\n===== 수집 결과 =====")
    print(f"(영화 수집) 중복 제거 전: {len(movie_rows)}개")
    # print(f"TV 콘텐츠 {len(tv_rows)}개")
    print(f"중복 제거 후: {len(rows)}개")
    print(f"저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()