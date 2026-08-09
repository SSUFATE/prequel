from sqlalchemy.orm import Session
from app.domains.additional_info.model import Translation, LtiBibliographyCache
from app.domains.additional_info.repository import TranslationRepository
from app.domains.literatures.model import LiteraryWork
import re


class TranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TranslationRepository(db)

    def sync_translations_for_work(self, work_id: int) -> list:
        work = self.db.query(LiteraryWork).filter(LiteraryWork.work_id == work_id).first()
        if not work:
            raise ValueError("존재하지 않는 작품입니다.")

        clean_title = self._clean_title(work.title)

        candidates = (
            self.db.query(LtiBibliographyCache)
            .filter(LtiBibliographyCache.original_title.ilike(f"%{clean_title}%"))
            .all()
        )

        translations = [
            Translation(
                work_id=work_id,
                language=c.language or "unknown",
                translated_title=c.original_title,
                translator=c.translator,
                publisher=c.publisher,
                isbn=c.isbn,
                cover_url=c.image,
                published_year=self._parse_year(c.published_year),
                purchase_url=None,
            )
            for c in candidates
        ]

        return self.repository.save_all(translations)

    def get_translations(self, work_id: int, language: str | None = None) -> list:
        return self.repository.find_all_by_work(work_id, language)

    def _parse_year(self, value: str | None) -> int | None:
        if not value:
            return None
        try:
            return int(value[:4])
        except (ValueError, TypeError):
            return None

    def _clean_title(self, title: str) -> str:
        # 콜론(: 또는 ：) 이후 부제 제거, 앞뒤 공백 정리
        return re.split(r"[:：]", title)[0].strip()