### Pydantic 모델: API 요청/응답 데이터 정의

from datetime import date
from pydantic import BaseModel, ConfigDict


# K-콘텐츠 응답
class KContentResponse(BaseModel):
    content_id: int
    title: str
    content_type: str
    release_date: date
    poster_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


# K-콘텐츠 목록 응답
class KContentListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[KContentResponse]
