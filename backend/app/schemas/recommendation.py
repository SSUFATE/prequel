### Pydantic 모델: API 요청/응답 데이터 정의
from pydantic import BaseModel, Field

# 매칭 태그 응답
class MatchedTagResponse(BaseModel):
    tag_id: int
    name: str
    content_weight: int
    work_weight: int

# 추천 문학작품 하나 응답
class RecommendedWorkResponse(BaseModel):
    work_id: int
    title: str
    author: str
    summary: str | None = None
    genre: str | None = None
    era: str | None = None
    published_year: int | None = None
    cover_url: str | None = None

    similarity_score: float = Field(
        ge=0,
        le=1
    )

    matched_tags: list[MatchedTagResponse]
