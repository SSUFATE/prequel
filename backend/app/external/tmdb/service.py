from sqlalchemy.orm import Session

from app.domains.kcontents.model import KContent
from app.external.tmdb.dto import TMDbContentDTO


def save_kcontent(
    db: Session,
    dto: TMDbContentDTO,
) -> tuple[KContent, bool]:

    existing = (
        db.query(KContent)
        .filter(
            KContent.tmdb_id == dto.tmdb_id,
            KContent.content_type == dto.content_type,
        )
        .first()
    )

    if existing:
        return existing, False

    kcontent = KContent(
        tmdb_id=dto.tmdb_id,
        title=dto.title,
        content_type=dto.content_type,
        overview=dto.overview,
        tmdb_genres=dto.tmdb_genres,
        runtime=dto.runtime,
        platform=dto.platform,
        release_date=dto.release_date,
        poster_url=dto.poster_url,
        source=dto.source,
    )

    db.add(kcontent)
    db.commit()
    db.refresh(kcontent)

    return kcontent, True