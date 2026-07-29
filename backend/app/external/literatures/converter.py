from app.domains.literatures.model import LiteraryWork
from app.external.literatures.schema import BookDetailRaw


def convert_to_literary_work(raw: dict) -> LiteraryWork:
    detail = raw["response"]["detail"][0]["book"]
    parsed = BookDetailRaw(**detail)

    return LiteraryWork(
        title=parsed.bookname,
        literature_type=None,
        author=parsed.authors,
        summary=parsed.description,
        genre=parsed.class_nm,
        era=None,
        published_year=_parse_year(parsed.publication_year),
        cover_url=parsed.bookImageURL,
        source="data4library",
    )


def _parse_year(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value[:4])
    except ValueError:
        return None