### DB 작업 함수

from datetime import date

from sqlalchemy.orm import Session
from app.domains.kcontents.model import KContent


# KContent 목록 조회
def get_kcontents(
    db: Session,
    search: str | None = None,
    content_type: str | None = None,
    page: int = 1,
    size: int = 10
):
    query = db.query(KContent)

    # 제목 검색
    if search:
        query = query.filter(
            KContent.title.ilike(f"%{search}%")
        )

    # 콘텐츠 종류 필터
    if content_type:
        query = query.filter(
            KContent.content_type == content_type.value
        )

    # 조건에 맞는 전체 콘텐츠 개수
    total = query.count()

    # 페이지네이션
    items = (
        query.order_by(KContent.content_id.asc())
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


# K콘텐츠 하나 조회
def get_kcontent_by_id(db: Session, content_id: int):
    return (
        db.query(KContent)
        .filter(
            KContent.content_id == content_id
        ).first()
    )


# 홈 화면 -> 섹션별 영화 조회
def get_home_section_contents(
    db: Session,
    section: dict,
):
    query = (
        db.query(KContent)
        .filter(KContent.content_type == "MOVIE")
        .filter(KContent.poster_url.is_not(None))
    )

    section_type = section["type"]

    # 장르별 조회
    if section_type == "GENRE":
        genre_id = section["genre_id"]

        query = query.filter(
            KContent.tmdb_genres.op("@>")(
                [{"id": genre_id}]
            )
        )

    # 개봉 연도별 조회
    elif section_type == "DECADE":
        query = query.filter(
            KContent.release_date >= date(
                section["start_year"], 1, 1
            ),
            KContent.release_date <= date(
                section["end_year"], 12, 31
            ),
        )

    # 최신 개봉순
    query = query.order_by(
        KContent.release_date.desc().nullslast(),
        KContent.content_id.desc(),
    )

    return query.limit(section["limit"]).all()