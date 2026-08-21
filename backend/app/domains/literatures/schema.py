from datetime import datetime

from pydantic import BaseModel, ConfigDict


def split_genre(genre: str | None) -> tuple[str | None, str | None]:
    if not genre:
        return None, None

    parts = [p.strip() for p in genre.split(">")]
    main_genre = parts[0] if parts else None
    sub_genre = " > ".join(parts[1:]) if len(parts) > 1 else None
    return main_genre, sub_genre


class LiteraryWorkResponse(BaseModel):
    work_id: int
    title: str
    author: str | None
    summary: str | None
    genre: str | None  
    main_genre: str | None  
    sub_genre: str | None  
    era: str | None
    published_year: int | None
    isbn13: str | None
    cover_url: str | None
    literature_type: str | None
    source: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_work(cls, work) -> "LiteraryWorkResponse":
        main_genre, sub_genre = split_genre(work.genre)
        return cls(
            work_id=work.work_id,
            title=work.title,
            author=work.author,
            summary=work.summary,
            genre=work.genre,
            main_genre=main_genre,
            sub_genre=sub_genre,
            era=work.era,
            published_year=work.published_year,
            isbn13=work.isbn13,
            cover_url=work.cover_url,
            literature_type=work.literature_type,
            source=work.source,
            created_at=work.created_at,
        )


class LiteraryWorkListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[LiteraryWorkResponse]