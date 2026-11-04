import logging

import app.models

from sqlalchemy import select

from app.database import SessionLocal
from app.domains.kcontents.model import KContent
from app.domains.literatures.model import LiteraryWork
from app.services.embedding_service import embedding_service


BATCH_SIZE = 100

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


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


def generate_embeddings(db, model, id_column, build_text, name):
    success = 0
    failed = []
    last_id = None

    while True:
        # 1. 임베딩이 없는 작품 100개 조회
        stmt = (
            select(model)
            .where(model.embedding.is_(None))
            .order_by(id_column)
            .limit(BATCH_SIZE)
        )

        if last_id is not None:
            stmt = stmt.where(id_column > last_id)

        items = db.scalars(stmt).all()

        if not items:
            break

        # 2. 마지막 조회 ID 저장
        last_id = getattr(items[-1], id_column.key)

        # 3. 작품별 임베딩 생성
        for item in items:
            item_id = getattr(item, id_column.key)

            try:
                text = build_text(item)
                vector = embedding_service.encode(text)

                item.embedding = vector
                success += 1

                logger.info(
                    "[%s] %s (ID=%s)",
                    name,
                    item.title,
                    item_id,
                )

            except Exception:
                failed.append(item_id)

                logger.exception(
                    "[%s] 임베딩 생성 실패: ID=%s",
                    name,
                    item_id,
                )

                # 실패한 객체의 변경사항 초기화
                db.expire(item)

        # 4. 배치 단위 저장
        try:
            db.commit()
            logger.info(
                "%s 저장 완료: 누적 %s개",
                name,
                success,
            )

        except Exception:
            db.rollback()
            logger.exception(
                "%s 배치 저장 실패",
                name,
            )
            raise

    logger.info(
        "%s 완료: 성공 %s개 / 실패 %s개",
        name,
        success,
        len(failed),
    )

    if failed:
        logger.warning("%s 실패 ID: %s", name, failed)


def main():
    db = SessionLocal()

    try:
        generate_embeddings(
            db=db,
            model=KContent,
            id_column=KContent.content_id,
            build_text=build_kcontent_text,
            name="KContent",
        )

        generate_embeddings(
            db=db,
            model=LiteraryWork,
            id_column=LiteraryWork.work_id,
            build_text=build_literature_text,
            name="Literature",
        )

        logger.info("전체 임베딩 생성 완료")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()