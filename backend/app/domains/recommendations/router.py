### 콘텐츠 선택 후 추천 문학작품 목록 조회 API

from app.domains.kcontents import crud as kcontent_crud
from app.domains.recommendations import service
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.domains.recommendations.schema import RecommendationListResponse
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/v1/k-contents",
    tags=["Recommendations"]
)


@router.get(
    "/{content_id}/recommendations",
    response_model=RecommendationListResponse,
    status_code=status.HTTP_200_OK
)
def get_kcontent_recommendations(
    content_id: int,
    limit: int = Query(
        default=5,
        ge=1,
        le=20
    ),
    db: Session = Depends(get_db)
):
    # 1. 요청한 K-콘텐츠가 존재하는지 확인
    kcontent = kcontent_crud.get_kcontent_by_id(
        db=db,
        content_id=content_id
    )

    if kcontent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="K-콘텐츠를 찾을 수 없습니다."
        )

    # 2. 추천 결과 생성
    recommendations = service.get_recommendations_by_content_id(
        db=db,
        content_id=content_id,
        limit=limit
    )

    # 콘텐츠는 존재하지만 태그가 없다면
    # recommendations에 빈 배열이 들어감
    return {
        "content_id": kcontent.content_id,
        "content_title": kcontent.title,
        "recommendations": recommendations
    }