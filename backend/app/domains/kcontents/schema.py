### Pydantic 모델: API 요청/응답 데이터 정의

from datetime import date
from enum import Enum
from pydantic import BaseModel, ConfigDict

class ContentType(str, Enum):
    MOVIE = "MOVIE"
    DRAMA = "DRAMA"

# K-콘텐츠 응답
class KContentResponse(BaseModel):
    content_id: int
    title: str
    content_type: ContentType
    overview: str | None = None
    platform: str | None = None
    release_date: date | None = None
    poster_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


# K-콘텐츠 목록 응답
class KContentListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[KContentResponse]
