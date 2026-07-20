### K콘텐츠 목록 조회 API

from fastapi import APIRouter, Depends, Query
from schemas import KContentListResponse
import crud.user as user_crud
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/k-contents",
    tags=["K-Contents"]
)

@router.get("", response_model=KContentListResponse)
def read_kcontents(
    search: str | None = Query(
        default=None,
        description="검색할 K-콘텐츠 제목"
    ),
    content_type: str | None = Query(
        default=None,
        description="콘텐츠 종류: movie, drama, webtoon"
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    size: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db)
):
    return user_crud.get_kcontents(
        db=db,
        search=search,
        content_type=content_type,
        page=page,
        size=size
    )