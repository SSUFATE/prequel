from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.literatures.service import LiteraryWorkService
from app.domains.literatures.schema import LiteraryWorkResponse, LiteraryWorkListResponse
from fastapi import Query, HTTPException

router = APIRouter(prefix="/literatures", tags=["literatures"])


@router.get("/{isbn13}")
def get_literary_work(isbn13: str, db: Session = Depends(get_db)):
    service = LiteraryWorkService(db)
    work = service.get_or_fetch(isbn13)
    return {"data": work}

@router.post("")
def bulk_fetch_books(total_pages: int = 5, start_dt: str = "2024-01-01", end_dt: str = "2024-12-31", db: Session = Depends(get_db)):
    service = LiteraryWorkService(db)
    count = service.bulk_fetch_and_save(total_pages, start_dt, end_dt)
    return {"saved": count} 

 
@router.get("", response_model=LiteraryWorkListResponse)
def get_literary_works(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    size: int = Query(20, ge=1, le=100, description="페이지당 개수"),
    keyword: str | None = Query(None, description="제목 또는 저자로 검색"),
    db: Session = Depends(get_db),
):
    service = LiteraryWorkService(db)
    items, total = service.get_list(page=page, size=size, keyword=keyword)
    return LiteraryWorkListResponse(total=total, page=page, size=size, items=items)
 
 
@router.get("/{work_id}", response_model=LiteraryWorkResponse)
def get_literary_work_detail(work_id: int, db: Session = Depends(get_db)):
    service = LiteraryWorkService(db)
    work = service.get_detail(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="해당 작품을 찾을 수 없습니다.")
    return work
 