import app.models

from app.database import SessionLocal
from app.domains.kcontents.model import KContent
from app.domains.literatures.model import LiteraryWork
from app.services.embedding_service import embedding_service


def build_kcontent_text(content: KContent) -> str:
    return f"""
제목: {content.title}
내용: {content.overview or ""}
""".strip()


def build_literature_text(literature: LiteraryWork) -> str:
    return f"""
제목: {literature.title}
내용: {literature.summary or ""}
""".strip()


def generate_kcontent_embeddings(db):
    contents = (
        db.query(KContent)
        .filter(KContent.embedding.is_(None))
        .all()
    )
    # contents = (
    #     db.query(KContent)
    #     .filter(KContent.embedding.is_(None))
    #     .limit(3)
    #     .all()
    # )

    print(f"K콘텐츠 임베딩 생성 대상: {len(contents)}개")

    for index, content in enumerate(contents, start=1):
        text = build_kcontent_text(content)

        content.embedding = embedding_service.encode(text)

        print(
            f"[KContent {index}/{len(contents)}] "
            f"{content.title}"
        )

    db.commit()


def generate_literature_embeddings(db):
    literatures = (
        db.query(LiteraryWork)
        .filter(LiteraryWork.embedding.is_(None))
        .all()
    )
    # literatures = (
    #     db.query(LiteraryWork)
    #     .filter(LiteraryWork.embedding.is_(None))
    #     .limit(3)
    #     .all()
    # )

    print(f"문학 임베딩 생성 대상: {len(literatures)}개")

    for index, literature in enumerate(literatures, start=1):
        text = build_literature_text(literature)

        literature.embedding = embedding_service.encode(text)

        print(
            f"[Literature {index}/{len(literatures)}] "
            f"{literature.title}"
        )

    db.commit()


def main():
    db = SessionLocal()

    try:
        generate_kcontent_embeddings(db)
        generate_literature_embeddings(db)

        print("임베딩 생성 완료")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()