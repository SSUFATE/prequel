from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.literatures.service import LiteraryWorkService
from app.domains.literatures.schema import LiteraryWorkResponse, LiteraryWorkListResponse

router = APIRouter(prefix="/literatures", tags=["literatures"])


@router.post("")
def bulk_fetch_books(
    start_page: int = Query(1, ge=1, description="수집 시작 페이지 번호"),
    total_pages: int = Query(5, ge=1, description="수집할 총 페이지 수"),
    start_dt: str = "2024-01-01",
    end_dt: str = "2024-12-31",
    db: Session = Depends(get_db),
):
    service = LiteraryWorkService(db)
    count = service.bulk_fetch_and_save(start_page, total_pages, start_dt, end_dt)
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
    return LiteraryWorkListResponse(
        total=total,
        page=page,
        size=size,
        items=[LiteraryWorkResponse.from_work(w) for w in items],
    )


@router.post("/backfill-summaries")
def backfill_summaries(
    limit: int = Query(50, ge=1, le=500, description="한 번에 처리할 최대 건수"),
    db: Session = Depends(get_db),
):
   
    service = LiteraryWorkService(db)
    updated = service.backfill_summaries(limit=limit)
    return {"updated": updated}



@router.get("/{work_id}", response_model=LiteraryWorkResponse)
def get_literary_work_detail(work_id: int, db: Session = Depends(get_db)):
    service = LiteraryWorkService(db)
    work = service.get_detail(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="해당 작품을 찾을 수 없습니다.")
    return LiteraryWorkResponse.from_work(work)