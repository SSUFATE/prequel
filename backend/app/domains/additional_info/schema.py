from pydantic import BaseModel
from typing import Optional


class TranslationResponse(BaseModel):
    translation_id: int
    work_id: int
    language: str
    translated_title: Optional[str] = None
    translator: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    purchase_url: Optional[str] = None
    cover_url: Optional[str] = None
    published_year: Optional[int] = None

    class Config:
        from_attributes = True