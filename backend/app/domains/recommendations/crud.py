from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.domains.literatures.model import LiteraryWork
from app.domains.tags.model import Tag, KContentTag, LiteraryWorkTag
from app.domains.tags.constants import TagCategory

# content_id로 해당 k콘텐츠 태그 조회
def get_content_tags(
    db: Session,
    content_id: int,
    category: TagCategory | None = None
) -> list[KContentTag]:
    
    query = (
        db.query(KContentTag)
        .join(
            Tag,
            Tag.tag_id == KContentTag.tag_id,
        )
        .filter(
            KContentTag.content_id == content_id
        )
    )

    if category is not None:
        query = query.filter(
            Tag.category == category.value
        )
    
    return query.all()


# 전체/테마별 문학 작품 순위
def get_tag_scored_literatures(
    db: Session,
    content_id: int,
    limit: int = 5,
    category: TagCategory | None = None,
    work_ids: list[int] | None = None,
):
    score_expression = func.sum(
        KContentTag.weight * LiteraryWorkTag.weight
    )

    query = (
        db.query(
            LiteraryWork,
            score_expression.label("raw_score")
        )
        .join(
            LiteraryWorkTag,
            LiteraryWork.work_id == LiteraryWorkTag.work_id,
        )
        .join(
            KContentTag,
            and_(
                LiteraryWorkTag.tag_id == KContentTag.tag_id,
                KContentTag.content_id == content_id,
            )
        )
        .join(
            Tag,
            Tag.tag_id == LiteraryWorkTag.tag_id
        )
    )

    if category is not None:
        query = query.filter(
            Tag.category == category.value
        )

    if work_ids is not None:
        if not work_ids:
            return []

        query = query.filter(
            LiteraryWork.work_id.in_(work_ids)
        )

    query = (
        query
        .group_by(LiteraryWork.work_id)
        .order_by(
            score_expression.desc(),
            LiteraryWork.work_id.asc(),
        )
    )

    # 후보 ID가 주어지면 해당 후보의 점수를 모두 조회
    if work_ids is None:
        query = query.limit(limit)

    return query.all()


# 콘텐츠와 추천 문학작품의 공통 태그 조회
def get_matched_tags(
    db: Session,
    content_id: int,
    work_ids: list[int],
    category: TagCategory | None = None
):
    if not work_ids:
        return []
    
    query = (
        db.query(
            LiteraryWorkTag.work_id,
            Tag.tag_id,
            Tag.name,
            Tag.category,
            KContentTag.weight.label("content_weight"),
            LiteraryWorkTag.weight.label("literature_weight"),
        ).
        join(
            Tag,
            Tag.tag_id 
            == LiteraryWorkTag.tag_id,
        )
        .join(
            KContentTag,
            and_(
                KContentTag.tag_id 
                == Tag.tag_id,

                KContentTag.content_id 
                == content_id,
            )
        )
        .filter(
            LiteraryWorkTag.work_id.in_(work_ids),
        )
    )

    if category is not None:
        query = query.filter(
            Tag.category == category.value
        )

    matched_tag_rows = query.all()

    return matched_tag_rows

# 특정 작품의 6대 테마별 점수 계산
def get_category_scores(
    db: Session,
    content_id: int,
    work_id: int
):
    score_expression = func.sum(
        KContentTag.weight * LiteraryWorkTag.weight
    )

    category_scores = (
        db
        .query(
            Tag.category,
            score_expression.label("raw_score")
        )
        .join(
            LiteraryWorkTag,
            LiteraryWorkTag.tag_id == Tag.tag_id
        )
        .join(
            KContentTag,
            and_(
                KContentTag.tag_id == Tag.tag_id,
                KContentTag.content_id == content_id
            )
        )
        .filter(
            LiteraryWorkTag.work_id == work_id
        )
        .group_by(
            Tag.category
        )
        .all()
    )

    return category_scores

# 문학작품 자체 태그 조회
def get_literature_tags(
    db: Session,
    work_id: int
):
    literature_tags = (
        db
        .query(
            Tag.tag_id,
            Tag.name,
            Tag.category,
            LiteraryWorkTag.weight.label("literature_weight"),
        )
        .join(
            LiteraryWorkTag,
            LiteraryWorkTag.tag_id == Tag.tag_id
        )
        .filter(
            LiteraryWorkTag.work_id == work_id
        )
        .all()
    )

    return literature_tags


# work_id로 문학작품 조회
# literatures 폴더로 옮기는 것 고려
def get_literature_by_id(
    db: Session,
    work_id: int
): 
    return (
        db.query(LiteraryWork)
        .filter(
            LiteraryWork.work_id == work_id
        )
        .first()
    )


# 임베딩 점수 기반 문학 추천
def get_embedding_scored_literatures(
    db: Session,
    content_embedding,
    limit: int = 5,
    work_ids: list[int] | None = None,
):
    distance = LiteraryWork.embedding.cosine_distance(
        content_embedding
    )

    query = (
        db.query(
            LiteraryWork,
            (1 - distance).label("embedding_score"),
        )
        .filter(LiteraryWork.embedding.is_not(None))
    )

    if work_ids is not None:
        if not work_ids:
            return []

        query = query.filter(
            LiteraryWork.work_id.in_(work_ids)
        )

    query = query.order_by(
        distance,
        LiteraryWork.work_id.asc(),
    )

    if work_ids is None:
        query = query.limit(limit)

    return query.all()