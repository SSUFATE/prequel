from sqlalchemy.orm import Session
from app.domains.additional_info.model import Translation


class TranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_work_and_language(self, work_id: int, language: str) -> Translation | None:
        return (
            self.db.query(Translation)
            .filter(Translation.work_id == work_id, Translation.language == language)
            .first()
        )

    def find_all_by_work(self, work_id: int, language: str | None = None) -> list[Translation]:
        query = self.db.query(Translation).filter(Translation.work_id == work_id)
        if language:
            query = query.filter(Translation.language == language)
        return query.all()

    def save_all(self, translations: list[Translation]) -> list[Translation]:
        saved = []
        for t in translations:
            existing = self.find_by_work_and_language(t.work_id, t.language)
            if existing:
                continue
            self.db.add(t)
            saved.append(t)
        self.db.commit()
        return saved