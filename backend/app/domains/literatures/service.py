from sqlalchemy.orm import Session
from app.external.literatures.client import LibraryApiClient
from app.external.literatures.converter import convert_to_literary_work
from app.external.literatures.schema import BookDetailRaw
from app.domains.literatures.repository import LiteraryWorkRepository
from app.domains.literatures.model import LiteraryWork
import time


class LiteraryWorkService:
    def __init__(self, db: Session):
        self.client = LibraryApiClient()
        self.repository = LiteraryWorkRepository(db)

    def bulk_fetch_and_save(
        self, start_page: int, total_pages: int, start_dt: str, end_dt: str
    ):
        saved_count = 0

        # range(1, ...) 대신 range(start_page, start_page + total_pages) 사용
        for page in range(start_page, start_page + total_pages):
            raw = self.client.fetch_books_page(
                page_no=page, start_dt=start_dt, end_dt=end_dt, kdc="81"
            )
            books = raw.get("response", {}).get("docs", [])

            print(f"[{page}페이지] 가져온 도서 수: {len(books)}개") 
            if not books:
                break  

            for item in books:
                book = item.get("doc")
                if not book:
                    continue

                class_nm = book.get("class_nm", "") or ""

                if "한국문학" not in class_nm:
                    continue
              

                work = self._convert_search_result(book)

                existing = None
                if work.isbn13:
                    existing = self.repository.find_by_isbn13(work.isbn13)
                if not existing:
                    existing = self.repository.find_by_title_author(
                        work.title, work.author
                    )

                if not existing:
                    self.repository.save(work)
                    saved_count += 1

            time.sleep(0.2) 

        return saved_count

    def _convert_search_result(self, book: dict) -> LiteraryWork:
        return LiteraryWork(
            title=book.get("bookname"),
            author=book.get("authors"),
            isbn13=book.get("isbn13"),
            summary=None,  
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
        existing = self.repository.find_by_isbn13(isbn13)
        if existing:
            return existing

        raw = self.client.fetch_book_detail(isbn13)
        work = convert_to_literary_work(raw)
        return self.repository.save(work)

    def get_list(
        self, page: int = 1, size: int = 20, keyword: str | None = None
    ) -> tuple[list[LiteraryWork], int]:
        skip = (page - 1) * size

        if keyword:
            items = self.repository.search(keyword, skip=skip, limit=size)
            total = self.repository.count_search(keyword)
        else:
            items = self.repository.find_all(skip=skip, limit=size)
            total = self.repository.count_all()

        return items, total

    def get_detail(self, work_id: int) -> LiteraryWork | None:
        return self.repository.find_by_id(work_id)

    def backfill_summaries(self, limit: int = 50) -> int:
        updated = 0
        targets = self.repository.find_missing_summary(limit=limit)

        for work in targets:
            try:
                raw = self.client.fetch_book_detail(work.isbn13)
                detail = raw["response"]["detail"][0]["book"]
                parsed = BookDetailRaw(**detail)

                if parsed.description:
                    self.repository.update_summary(work, parsed.description)
                    updated += 1
            except Exception:
                continue

            time.sleep(0.2)

        return updated