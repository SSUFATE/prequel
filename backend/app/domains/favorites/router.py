from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.domains.favorites.service import FavoriteService
from app.domains.favorites.schema import FavoriteWorkResponse
from app.domains.users.model import User
from fastapi import status
from app.domains.favorites.schema import FavoriteResponse

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteWorkResponse])
def get_my_favorite_works(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """로그인한 사용자가 찜한 문학작품 목록 조회"""
    service = FavoriteService(db)
    return service.get_my_favorite_works(current_user.user_id)

from fastapi import status
from app.domains.favorites.schema import FavoriteResponse

@router.post("/{work_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """작품 찜하기"""
    service = FavoriteService(db)
    try:
        favorite = service.add_favorite(current_user.user_id, work_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return favorite


@router.delete("/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """찜 해제"""
    service = FavoriteService(db)
    deleted = service.remove_favorite(current_user.user_id, work_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="찜한 작품이 아닙니다.")