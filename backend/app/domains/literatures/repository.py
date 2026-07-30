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

    def save(self, work: LiteraryWork) -> LiteraryWork:
        self.db.add(work)
        self.db.commit()
        self.db.refresh(work)
        return work