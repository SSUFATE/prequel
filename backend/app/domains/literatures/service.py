from sqlalchemy.orm import Session
from app.external.literatures.client import LibraryApiClient
from app.external.literatures.converter import convert_to_literary_work
from app.domains.literatures.repository import LiteraryWorkRepository
from app.domains.literatures.model import LiteraryWork
import time


class LiteraryWorkService:
    def __init__(self, db: Session):
        self.client = LibraryApiClient()
        self.repository = LiteraryWorkRepository(db)

    def get_or_fetch(self, isbn13: str) -> LiteraryWork:
        raw = self.client.fetch_book_detail(isbn13)
        work = convert_to_literary_work(raw)

        existing = self.repository.find_by_title_author(work.title, work.author)
        if existing:
            return existing

        return self.repository.save(work)


class LiteraryWorkService:
    def __init__(self, db: Session):
        self.client = LibraryApiClient()
        self.repository = LiteraryWorkRepository(db)

    def bulk_fetch_and_save(self, total_pages: int, start_dt: str, end_dt: str):
        saved_count = 0

        for page in range(1, total_pages + 1):
            raw = self.client.fetch_books_page(page_no=page, start_dt=start_dt, end_dt=end_dt)
            books = raw.get("response", {}).get("docs", [])

            if not books:
                break  # 더 이상 데이터 없으면 중단

            for item in books:
                book = item.get("doc")
                if not book:
                    continue

                work = self._convert_search_result(book)

                existing = self.repository.find_by_title_author(work.title, work.author)
                if not existing:
                    self.repository.save(work)
                    saved_count += 1

            time.sleep(0.2)  # API 과호출 방지

        return saved_count

    def _convert_search_result(self, book: dict) -> LiteraryWork:
        return LiteraryWork(
            title=book.get("bookname"),
            author=book.get("authors"),
            summary=None,  # srchBooks는 책소개 안 줌 → 상세조회 별도 필요
            genre=book.get("class_nm"),
            published_year=self._parse_year(book.get("publication_year")),
            cover_url=book.get("bookImageURL"),
            source="data4library",
        )

    def _parse_year(self, value):
        if not value:
            return None
        try:
            return int(value[:4])
        except (ValueError, TypeError):
            return None
        
    def get_or_fetch(self, isbn13: str) -> LiteraryWork:
        raw = self.client.fetch_book_detail(isbn13)
        work = convert_to_literary_work(raw)

        existing = self.repository.find_by_title_author(work.title, work.author)
        if existing:
            return existing

        return self.repository.save(work)