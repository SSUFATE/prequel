from pydantic import BaseModel
from typing import Optional


class BookDetailRaw(BaseModel):
    bookname: str
    authors: str
    publisher: str
    publication_year: Optional[str] = None
    isbn13: str
    class_nm: Optional[str] = None
    bookImageURL: Optional[str] = None
    description: Optional[str] = None