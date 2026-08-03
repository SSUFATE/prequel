from sqlalchemy.orm import Session, joinedload
from app.domains.favorites.model import Favorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all_by_user(self, user_id: int) -> list[Favorite]:
        return (
            self.db.query(Favorite)
            .options(joinedload(Favorite.literary_work))  # N+1 방지 — 문학작품 정보 한 번에 로드
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .all()
        )

    def find_by_user_and_work(self, user_id: int, work_id: int) -> Favorite | None:
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.work_id == work_id)
            .first()
        )

    def save(self, favorite: Favorite) -> Favorite:
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def delete(self, favorite: Favorite) -> None:
        self.db.delete(favorite)
        self.db.commit()