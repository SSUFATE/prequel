import re
from sqlalchemy.orm import Session
from app.domains.additional_info.model import Translation, LtiBibliographyCache
from app.domains.additional_info.repository import TranslationRepository
from app.domains.literatures.model import LiteraryWork


class TranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TranslationRepository(db)

    def get_translations(self, work_id: int, language: str | None = None) -> list:
        return self.repository.find_all_by_work(work_id, language)
    
    def sync_translations_for_work(self, work_id: int) -> list:
        work = self.db.query(LiteraryWork).filter(LiteraryWork.work_id == work_id).first()
        if not work:
            raise ValueError("존재하지 않는 작품입니다.")

        
        clean_title = re.sub(r"\(.*?\)|\[.*?\]", "", work.title)
        clean_title = re.split(r"[:：;]", clean_title)[0]
        clean_title = re.sub(r"[0-9]", "", clean_title).strip()

        
        first_word = clean_title.split()[0] if clean_title.split() else clean_title
        search_keyword = first_word[:3] if len(first_word) >= 3 else first_word

        
        candidates = (
            self.db.query(LtiBibliographyCache)
            .filter(LtiBibliographyCache.original_title.ilike(f"%{search_keyword}%"))
            .all()
        )

        
        if not candidates:
            no_space_title = clean_title.replace(" ", "")
            short_keyword = no_space_title[:2] if len(no_space_title) >= 2 else no_space_title
            candidates = (
                self.db.query(LtiBibliographyCache)
                .filter(LtiBibliographyCache.original_title.ilike(f"%{short_keyword}%"))
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