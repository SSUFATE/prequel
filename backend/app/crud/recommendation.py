### 작품별 추천 점수 계산

from sqlalchemy.orm import Session
import models
from collections import defaultdict
from sqlalchemy import and_, func

def get_recommendations_by_content_id(
    db: Session,
    content_id: int,
    limit: int = 5
): 
    # 1. 선택한 K콘텐츠의 태그 조회
    content_tags = (
        db.query(models.KContentTag)
        .filter(
            models.KContentTag.content_id == content_id
        ).all()
    )

    # 연결된 태그가 없으면 추천 결과 없음
    if not content_tags:
        return []
    
    # 콘텐츠 태그가 받을 수 있는 최대 점수
    max_possible_score = (
        sum(tag.weight for tag in content_tags) * 5 
    )

    # 같은 tag_id의 가중치를 곱한 뒤, 작품별로 태그 점수식 환산
    score_expression = func.sum(
        models.KContentTag.weight 
        * models.LiteraryWorkTag.weight
    )

    # 2. 작품별 추천 점수 계산
    scored_works = (
        db.query(
            models.LiteraryWork,
            score_expression.label("raw_score")
        )
        # LiteraryWork와 LiteraryWorkTag 연결
        .join(
            models.LiteraryWorkTag,
            models.LiteraryWorkTag.work_id
            == models.LiteraryWork.work_id
        )
        # LiteraryWorkTag와 KContentTag 연결
        .join(
            models.KContentTag,
            and_(
                models.KContentTag.tag_id
                == models.LiteraryWorkTag.tag_id,

                models.KContentTag.content_id
                == content_id
            )
        )
        # 작품별로 점수 합산
        .group_by(
            models.LiteraryWork.work_id
        )
        # 점수가 높은 작품부터
        .order_by(
            score_expression.desc()
        )
        # 상위 작품만 조회
        .limit(limit)
        .all()
    )

    if not scored_works:
        return []
    
    selected_work_ids = [
        work.work_id
        for work, raw_score in scored_works
    ]

    # 3. 각 추천 작품과 콘텐츠가 공유한 태그 조회
    matched_tag_rows = (
        db.query(
            models.LiteraryWorkTag.work_id,
            models.Tag.tag_id,
            models.Tag.name,
            models.KContentTag.weight.label(
                "content_weight"
            ),
            models.LiteraryWorkTag.weight.label(
                "work_weight"
            )
        )
        .join(
            models.Tag,
            models.Tag.tag_id
            == models.LiteraryWorkTag.tag_id
        )
        .join(
            models.KContentTag,
            and_(
                models.KContentTag.tag_id
                == models.LiteraryWorkTag.tag_id,

                models.KContentTag.content_id
                == content_id
            )
        )
        .filter(
            models.LiteraryWorkTag.work_id.in_(
                selected_work_ids
            )
        )
        .all()
    )

    # 작품별 공통 태그 정리
    matched_tags_by_work = defaultdict(list)

    for row in matched_tag_rows:
        matched_tags_by_work[row.work_id].append({
            "tag_id": row.tag_id,
            "name": row.name,
            "content_weight": row.content_weight,
            "work_weight": row.work_weight
        })

    # 4. API 응답 형식 만들기
    recommendations = []

    for work, raw_score in scored_works:
        similarity_score = (
            float(raw_score) / max_possible_score
        )

        recommendations.append({
            "work_id": work.work_id,
            "title": work.title,
            "author": work.author,
            "summary": work.summary,
            "genre": work.genre,
            "era": work.era,
            "published_year": work.published_year,
            "cover_url": work.cover_url,
            "similarity_score": round(
                min(similarity_score, 1.0),
                3
            ),
            "matched_tags": matched_tags_by_work[
                work.work_id
            ]
        })

    return recommendations
