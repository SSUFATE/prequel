from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.domains.literatures.model import LiteraryWork


class LiteraryWorkRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_title_author(self, title: str, author: str) -> LiteraryWork | None:
        return (
            self.db.query(LiteraryWork)
            .filter(LiteraryWork.title == title, LiteraryWork.author == author)
            .first()
        )

    def find_by_isbn13(self, isbn13: str) -> LiteraryWork | None:
        return (
            self.db.query(LiteraryWork)
            .filter(LiteraryWork.isbn13 == isbn13)
            .first()
        )

    def find_by_id(self, work_id: int) -> LiteraryWork | None:
        return (
            self.db.query(LiteraryWork)
            .filter(LiteraryWork.work_id == work_id)
            .first()
        )

    def find_all(self, skip: int = 0, limit: int = 20) -> list[LiteraryWork]:
        return (
            self.db.query(LiteraryWork)
            .order_by(LiteraryWork.work_id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(LiteraryWork).count()

    def search(self, keyword: str, skip: int = 0, limit: int = 20) -> list[LiteraryWork]:
        pattern = f"%{keyword}%"
        return (
            self.db.query(LiteraryWork)
            .filter(
                or_(
                    LiteraryWork.title.ilike(pattern),
                    LiteraryWork.author.ilike(pattern),
                )
            )
            .order_by(LiteraryWork.work_id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_search(self, keyword: str) -> int:
        pattern = f"%{keyword}%"
        return (
            self.db.query(LiteraryWork)
            .filter(
                or_(
                    LiteraryWork.title.ilike(pattern),
                    LiteraryWork.author.ilike(pattern),
                )
            )
            .count()
        )

    def find_missing_summary(self, limit: int = 50):
        return (
            self.db.query(LiteraryWork)
            .filter(
                LiteraryWork.isbn13.isnot(None),  
                (LiteraryWork.summary.is_(None))
                | (LiteraryWork.summary == ""),  
            )
            .order_by(LiteraryWork.work_id.asc())  
            .limit(limit)
            .all()
        )

    def update_summary(self, work: LiteraryWork, summary: str) -> LiteraryWork:
        work.summary = summary
        self.db.commit()
        self.db.refresh(work)
        return work

    def save(self, work: LiteraryWork) -> LiteraryWork:
        self.db.add(work)
        self.db.commit()
        self.db.refresh(work)
        return work