### 태그 기반 추천 계산 로직
from collections import defaultdict

from app.domains.tags.model import KContentTag
from app.domains.tags.model import LiteraryWorkTag
from app.domains.literatures.model import LiteraryWork
from app.domains.tags.model import Tag
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from app.domains.recommendations.crud import (
    get_content_tags, 
    get_scored_literatures,
    get_matched_tags
)

MAX_TAG_WEIGHT = 5

def get_recommendations_by_content_id(
    db: Session,
    content_id: int,
    limit: int = 5
): 
    # 1. 선택한 K콘텐츠의 태그 조회
    content_tags = get_content_tags(db, content_id)

    # 연결된 태그가 없으면 추천 결과 없음
    if not content_tags:
        return []
    
    # 유사도 계산 시 사용할 최대 가능 점수
    max_possible_score = (
        sum(tag.weight for tag in content_tags)
        * MAX_TAG_WEIGHT
    )

    if max_possible_score == 0:
        return []

    # 2. 작품별 추천 점수 계산
    scored_works = get_scored_literatures(db, content_id, limit=5)

    if not scored_works:
        return []
    
    selected_work_ids = [
        work.work_id
        for work, raw_score in scored_works
    ]

    # 3. 각 추천 작품과 콘텐츠가 공유한 태그 조회
    matched_tag_rows = get_matched_tags(db, content_id, selected_work_ids)

    # 작품별 공통 태그 정리
    matched_tags_by_work = defaultdict(list)

    for row in matched_tag_rows:
        matched_tags_by_work[row.work_id].append(
            {
                "tag_id": row.tag_id,
                "name": row.name,
                "content_weight": row.content_weight,
                "work_weight": row.work_weight
            }
        )

    # 4. 최종 추천 결과 형식 만들기
    recommendations = []

    for work, raw_score in scored_works:
        similarity_score = (
            float(raw_score) / max_possible_score
        )

        recommendations.append(
            {
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
                    3,
                ),
                "matched_tags": matched_tags_by_work[
                    work.work_id
                ],
            }
        )

    return recommendations
