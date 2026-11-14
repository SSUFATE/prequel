from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FavoriteWorkResponse(BaseModel):
    favorite_id: int
    work_id: int
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    era: Optional[str] = None
    cover_url: Optional[str] = None
    favorited_at: datetime

    class Config:
        from_attributes = True
        

class FavoriteResponse(BaseModel):
    favorite_id: int
    work_id: int
    created_at: datetime

    class Config:
        from_attributes = True