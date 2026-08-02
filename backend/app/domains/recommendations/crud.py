from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.domains.literatures.model import LiteraryWork
from app.domains.tags.model import Tag, KContentTag, LiteraryWorkTag


# content_id로 해당 k콘텐츠 태그 조회
def get_content_tags(
    db: Session,
    content_id: int
) -> list[KContentTag]:
    content_tags = (
        db.query(KContentTag)
        .filter(
            KContentTag.content_id == content_id
        ).all()
    )

    return content_tags


# 문학작품별 추천 점수 계산
def get_scored_literatures(
    db: Session,
    content_id: int,
    limit: int
):
    # 같은 tag_id의 가중치를 곱한 뒤, 작품별로 태그 점수식 환산
    score_expressions = (
        KContentTag.weight * LiteraryWorkTag.weight
    )

    scored_works = (
        db.query(
            LiteraryWork,
            score_expressions.label("raw_score")
        )
        # LiteraryWork와 LiteraryWorkTag 연결
        .join(
            LiteraryWorkTag,
            LiteraryWork.work_id 
            == LiteraryWorkTag.work_id,
        )
        # LiteraryWorkTag와 KContentTag 연결
        .join(
            KContentTag,
            and_(
                LiteraryWorkTag.tag_id 
                == KContentTag.tag_id,

                KContentTag.content_id 
                == content_id,
            )     
        )
        # 작품별로 점수 합산
        .group_by(
            LiteraryWork.work_id
        )
        # 점수가 높은 작품부터
        .order_by(
            score_expressions.desc()
        )
        # 상위 작품만 조회
        .limit(limit)
        .all()
    )

    return scored_works


# 콘텐츠와 추천 문학작품별 공통 태그 조회
def get_matched_tags(
    db: Session,
    content_id: int,
    work_ids: list[int]
):
    if not work_ids:
        return []
    
    matched_tag_rows = (
        db.query(
            LiteraryWorkTag.work_id,
            Tag.tag_id,
            Tag.name,
            LiteraryWorkTag.weight.label("content_weight"),
            KContentTag.weight.label("literature_weight"),
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
        .all()
    )

    return matched_tag_rows