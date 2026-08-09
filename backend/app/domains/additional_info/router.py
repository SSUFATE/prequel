from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.additional_info.service import TranslationService
from app.domains.additional_info.schema import TranslationResponse

router = APIRouter(prefix="/translations", tags=["translations"])


@router.post("/{work_id}/sync", response_model=list[TranslationResponse])
def sync_translations(work_id: int, db: Session = Depends(get_db)):
    service = TranslationService(db)
    try:
        saved = service.sync_translations_for_work(work_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return saved


@router.get("/{work_id}", response_model=list[TranslationResponse])
def get_translations(
    work_id: int,
    language: str | None = Query(None),
    db: Session = Depends(get_db),
):
    service = TranslationService(db)
    return service.get_translations(work_id, language)