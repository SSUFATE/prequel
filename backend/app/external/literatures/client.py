import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://data4library.kr/api/srchDtlList"
AUTH_KEY = os.getenv("LIBRARY_API_KEY")


class LibraryApiClient:
    def fetch_book_detail(self, isbn13: str) -> dict:
        params = {
            "authKey": AUTH_KEY,
            "isbn13": isbn13,
            "loaninfoYN": "Y",
            "format": "json",
        }
        with httpx.Client(timeout=15.0) as client:
            res = client.get(BASE_URL, params=params)
            res.raise_for_status()
            return res.json()

    def fetch_books_page(self, page_no: int, page_size: int = 100, start_dt: str | None = None, end_dt: str | None = None, kdc: str = "81") -> dict:
        params = {
            "authKey": AUTH_KEY,
            "pageNo": page_no,
            "pageSize": page_size,
            "kdc": kdc,
            "format": "json",
        }
        if start_dt:
            params["startDt"] = start_dt
        if end_dt:
            params["endDt"] = end_dt

        with httpx.Client(timeout=60.0) as client:
            res = client.get("http://data4library.kr/api/srchBooks", params=params)
            res.raise_for_status()
            return res.json()