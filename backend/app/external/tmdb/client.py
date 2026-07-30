### TMDb API 호출

import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")

class TMDbClient:
    def __init__(self) -> None:
        if not ACCESS_TOKEN:
            raise RuntimeError(
                "TMDB_ACCESS_TOKEN이 .env에 설정되어 있지 않습니다."
            )
        
        self.headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "accept": "application/json",
        }

    def _get(
            self, 
            endpoint: str, 
            params: dict | None = None
        ) -> dict:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=self.headers,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()
    
    # DISCOVER/MOVIE
    def get_korean_movies(
        self, 
        page: int = 1,
        genre_id: int | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {
            "language": "ko-KR",
            "with_origin_country": "KR",
            "with_original_language": "ko",
            "primary_release_date.gte": "2010-01-01",
            "sort_by": "popularity.desc",
            "include_adult": False,
            "vote_count.gte": 100,
            "page": page,
        }

        if genre_id is not None:
            params["with_genres"] = str(genre_id)

        data = self._get(
            "/discover/movie",
            params=params
        )

        return data.get("results", [])
    
    # DISCOVER/TV
    def get_korean_tv_contents(self, page: int = 1) -> list[dict]:
        data = self._get(
            "/discover/tv",
            params={
                "language": "ko-KR",
                "with_origin_country": "KR",
                "sort_by": "popularity.desc",
                "include_adult": False,
                "page": page,
            }
        )

        return data.get("results", [])
    
    # MOVIES/Details
    def get_movie_details(self, tmdb_id: int) -> dict:
        return self._get(
            f"/movie/{tmdb_id}",
            params={
                "language": "ko-KR",
            },
        )

    # TV_SERIES/Details
    def get_tv_details(self, tmdb_id: int) -> dict:
        return self._get(
            f"/tv/{tmdb_id}",
            params={
                "language": "ko-KR",
            },
        )
    
    # WATCH_PROVIDERS/Movie Provider
    def get_movie_watch_providers(self, tmdb_id: int) -> dict:
        return self._get(
            f"/movie/{tmdb_id}/watch/providers"
        )

    # WATCH_PROVIDERS/TV Provider
    def get_tv_watch_providers(self, tmdb_id: int) -> dict:
        return self._get(
            f"/tv/{tmdb_id}/watch/providers"
        )
    
    # SEARCH/MOVIE
    def search_movie(
        self,
        title: str,
        year: int | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {
            "language": "ko-KR",
            "query": title,
            "include_adult": False,
        }

        if year is not None:
            params["year"] = year

        data = self._get(
            "/search/movie",
            params=params,
        )

        return data.get("results", [])