### TMDb 응답 데이터 정의

from dataclasses import dataclass
from datetime import date


@dataclass
class TMDbContentDTO:
    tmdb_id: int
    title: str
    content_type: str
    overview: str | None
    tmdb_genres: list[dict]
    runtime: int | None
    platform: str | None
    release_date: date | None
    poster_url: str | None
    source: str = "TMDB"