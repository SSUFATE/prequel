### DB 작업 함수

from sqlalchemy.orm import Session
import models

# KContent 목록 조회
def get_kcontents(
    db: Session,
    search: str | None = None,
    content_type: str | None = None,
    page: int = 1,
    size: int = 10
):
    query = db.query(models.KContent)

    # 제목 검색
    if search:
        query = query.filter(
            models.KContent.title.ilike(f"%{search}%")
        )

    # 콘텐츠 종류 필터
    if content_type:
        query = query.filter(
            models.KContent.content_type.ilike(f"%{content_type}%")
        )

    # 조건에 맞는 전체 콘텐츠 개수
    total = query.count()

    # 페이지네이션
    items = (
        query.order_by(models.KContent.content_id.asc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }