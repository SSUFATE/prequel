### TMDb 데이터를 프로젝트 DB 형식으로 변환

from datetime import date

from app.external.tmdb.dto import TMDbContentDTO

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
    

def build_poster_url(poster_path: str | None) -> str | None:
    if not poster_path:
        return None
    
    return f"{IMAGE_BASE_URL}{poster_path}"


def extract_platform(provider_data: dict) -> str | None:
    korean_data = provider_data.get("results", {}).get("KR")

    if not korean_data:
        return None
    
    provider_names: list[str] = []

    for provider_type in ("flatrate", "rent", "buy", "free", "ads"):
        providers = korean_data.get(provider_type, [])

        for provider in providers:
            provider_name = provider.get("provider_name")

            if (provider_name and provider_name not in provider_names):
                provider_names.append(provider_name)
            
    if not provider_names:
        return None
    
    return ", ".join(provider_names)


def movie_to_dto(
    details: dict,
    provider_data: dict,
) -> TMDbContentDTO:
    return TMDbContentDTO(
        tmdb_id=details["id"],
        title=details.get("title", ""),
        content_type="MOVIE",
        overview=details.get("overview") or None,
        tmdb_genres=details.get("genres", []),
        runtime=details.get("runtime"),
        platform=extract_platform(provider_data),
        release_date=parse_date(
            details.get("release_date")
        ),
        poster_url=build_poster_url(
            details.get("poster_path")
        ),
    )


def tv_to_dto(
    details: dict,
    provider_data: dict,
) -> TMDbContentDTO:
    episode_runtimes = details.get("episode_run_time", [])

    runtime = (
        episode_runtimes[0]
        if episode_runtimes
        else None
    )

    return TMDbContentDTO(
        tmdb_id=details["id"],
        title=details.get("name", ""),
        content_type="DRAMA",
        overview=details.get("overview") or None,
        tmdb_genres=details.get("genres", []),
        runtime=runtime,
        platform=extract_platform(provider_data),
        release_date=parse_date(
            details.get("first_air_date")
        ),
        poster_url=build_poster_url(
            details.get("poster_path")
        ),
    )

# csv에 저장
def dto_to_csv_row(dto: TMDbContentDTO) -> dict:
    return {
        "tmdb_id": dto.tmdb_id,
        "title": dto.title,
        "content_type": dto.content_type,
        "overview": dto.overview,
        "tmdb_genres": dto.tmdb_genres,
        "runtime": dto.runtime,
        "platform": dto.platform,
        "release_date": dto.release_date,
        "poster_url": dto.poster_url,
        "source": dto.source,
    }