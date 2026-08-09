from sqlalchemy.orm import Session
from app.domains.favorites.repository import FavoriteRepository
from app.domains.favorites.schema import FavoriteWorkResponse
from app.domains.favorites.model import Favorite
from app.domains.literatures.model import LiteraryWork


class FavoriteService:
    def __init__(self, db: Session):
        self.db = db    
        self.repository = FavoriteRepository(db)

    def get_my_favorite_works(self, user_id: int) -> list[FavoriteWorkResponse]:
        favorites = self.repository.find_all_by_user(user_id)

        return [
            FavoriteWorkResponse(
                favorite_id=fav.favorite_id,
                work_id=fav.literary_work.work_id,
                title=fav.literary_work.title,
                author=fav.literary_work.author,
                genre=fav.literary_work.genre,
                era=fav.literary_work.era,
                cover_url=fav.literary_work.cover_url,
                favorited_at=fav.created_at,
            )
            for fav in favorites
        ]
    
    def add_favorite(self, user_id: int, work_id: int) -> Favorite:
        work = self.db.query(LiteraryWork).filter(LiteraryWork.work_id == work_id).first()
        if not work:
            raise ValueError("존재하지 않는 작품입니다.")

        existing = self.repository.find_by_user_and_work(user_id, work_id)
        if existing:
            return existing  # 이미 찜한 경우 중복 생성하지 않고 그대로 반환

        favorite = Favorite(user_id=user_id, work_id=work_id)
        return self.repository.save(favorite)

    def remove_favorite(self, user_id: int, work_id: int) -> bool:
        favorite = self.repository.find_by_user_and_work(user_id, work_id)
        if not favorite:
            return False
        self.repository.delete(favorite)
        return True
    