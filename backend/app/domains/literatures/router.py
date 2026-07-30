from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.literatures.service import LiteraryWorkService

router = APIRouter(prefix="/literatures", tags=["literatures"])


@router.get("/{isbn13}")
def get_literary_work(isbn13: str, db: Session = Depends(get_db)):
    service = LiteraryWorkService(db)
    work = service.get_or_fetch(isbn13)  # try/except 제거하고 원래 에러 보기
    return {"data": work}

@router.post("")
def bulk_fetch_books(total_pages: int = 5, start_dt: str = "2024-01-01", end_dt: str = "2024-12-31", db: Session = Depends(get_db)):
    service = LiteraryWorkService(db)
    count = service.bulk_fetch_and_save(total_pages, start_dt, end_dt)
    return {"saved": count}