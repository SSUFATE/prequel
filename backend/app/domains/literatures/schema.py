from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LiteraryWorkResponse(BaseModel):
    work_id: int
    title: str
    author: str | None
    summary: str | None
    genre: str | None
    era: str | None
    published_year: int | None
    cover_url: str | None
    literature_type: str | None
    source: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LiteraryWorkListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[LiteraryWorkResponse]