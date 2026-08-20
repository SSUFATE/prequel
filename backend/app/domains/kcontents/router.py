### K콘텐츠 목록 조회 API

from app.domains.kcontents.crud import (
    get_kcontents,
    get_kcontent_by_id
)
from app.database import get_db
from fastapi import APIRouter, Depends, Query, status, HTTPException
from app.domains.kcontents.schema import (
    ContentType,
    KContentResponse,
    KContentListResponse
)
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/k-contents",
    tags=["K-Contents"]
)

# K콘텐츠 목록 조회
@router.get(
    "", 
    response_model=KContentListResponse,
    status_code=status.HTTP_200_OK
)
def read_kcontents(
    search: str | None = Query(
        default=None,
        description="검색할 K-콘텐츠 제목"
    ),
    content_type: ContentType | None = Query(
        default=None,
        description="콘텐츠 종류"
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
    return get_kcontents(
        db=db,
        search=search,
        content_type=content_type,
        page=page,
        size=size
    )


# content_id로 K콘텐츠 조회
@router.get(
    "/{content_id}",
    response_model=KContentResponse,
    status_code=status.HTTP_200_OK
)
def read_kcontent(
    content_id: int,
    db: Session = Depends(get_db)
):
    kcontent = get_kcontent_by_id(
        db=db,
        content_id=content_id
    )

    if kcontent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="K-콘텐츠를 찾을 수 없습니다."
        )

    return kcontent