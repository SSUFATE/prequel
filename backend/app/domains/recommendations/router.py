### 콘텐츠 선택 후 추천 문학작품 목록 조회 API

from app.domains.kcontents.crud import get_kcontent_by_id
from app.domains.recommendations.crud import get_literature_by_id 
from app.domains.recommendations import service
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.domains.recommendations.schema import RecommendationListResponse, RecommendationDetailResponse
from sqlalchemy.orm import Session
from app.domains.tags.constants import TagCategory

router = APIRouter(
    prefix="/k-contents",
    tags=["Recommendations"]
)

# 콘텐츠로 추천 문학 목록 조회
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
    category: TagCategory | None = Query(
        default=None
    ),
    db: Session = Depends(get_db)
):
    # 1. 콘텐츠 존재 여부 확인
    kcontent = get_kcontent_by_id(
        db=db,
        content_id=content_id
    )

    if kcontent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="K-콘텐츠를 찾을 수 없습니다."
        )

    # 2. 전체/테마별 추천 결과 생성
    recommendations = service.get_recommendations_by_content_id(
        db=db,
        content_id=content_id,
        limit=limit,
        category=category
    )

    return {
        "content_id": kcontent.content_id,
        "content_title": kcontent.title,
        "recommendations": recommendations
    }


# 특정 콘텐츠 + 문학작품 상세 조회
@router.get(
    "/{contend_id}/recommendations/{work_id}",
    response_model=RecommendationDetailResponse,
    status_code=status.HTTP_200_OK
)
def get_recommendation_detail(
    content_id: int,
    work_id: int,
    db: Session = Depends(get_db)
):
    # 콘텐츠 존재 여부 확인
    kcontent = get_kcontent_by_id(
        db=db,
        content_id=content_id
    )

    if kcontent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="K-콘텐츠를 찾을 수 없습니다."
        )
    
    # 문학작품 존재 여부 확인
    literature = get_literature_by_id(
        db=db,
        work_id=work_id
    )

    if literature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문학작품을 찾을 수 없습니다."
        )
    
    # 추천 상세 정보 생성
    detail = service.get_recommendation_detail(
        db=db,
        content_id=content_id,
        work_id=work_id
    )

    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추천 정보를 찾을 수 없습니다."
        )
    
    return detail