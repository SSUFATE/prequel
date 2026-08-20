### 태그 기반 추천 계산 로직
from collections import defaultdict


from sqlalchemy.orm import Session
from app.domains.recommendations.crud import (
    get_content_tags, 
    get_scored_literatures,
    get_matched_tags,
    get_category_scores,
    get_literature_tags
)
from app.domains.recommendations.constants import MAX_TAG_WEIGHT
from app.domains.tags.constants import TagCategory


# 전체/테마별 content_id로 추천 문학 목록 반환
def get_recommendations_by_content_id(
    db: Session,
    content_id: int,
    limit: int = 5,
    category: TagCategory | None = None
): 
    # 1. 콘텐츠 태그 조회
    # category가 있으면 해당 테마의 태그만 조회
    content_tags = get_content_tags(
        db=db, 
        content_id=content_id,
        category=category
    )

    # 연결된 태그가 없으면 추천 결과 없음
    if not content_tags:
        return []
    
    
    # 2. 최대 가능 점수 계산
    max_possible_score = (
        sum(tag.weight for tag in content_tags)
        * MAX_TAG_WEIGHT
    )

    if max_possible_score == 0:
        return []

    # 3. 문학작품별 추천 점수 계산
    scored_works = get_scored_literatures(
        db=db, 
        content_id=content_id, 
        limit=limit,
        category=category
    )

    if not scored_works:
        return []
    
    selected_work_ids = [
        work.work_id
        for work, raw_score in scored_works
    ]

    # 4. 콘텐츠와 추천 작품의 공통 태그 조회
    matched_tag_rows = get_matched_tags(
        db, 
        content_id, 
        selected_work_ids,
        category=category
    )

    # 작품별 공통 태그 정리
    matched_tags_by_work = defaultdict(list)

    for row in matched_tag_rows:
        matched_tags_by_work[row.work_id].append(
            {
                "tag_id": row.tag_id,
                "name": row.name,
                "category": row.category,
                "content_weight": row.content_weight,
                "literature_weight": row.literature_weight
            }
        )

    # 5. 최종 추천 결과 생성
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

# 문학 상세 화면: 전체 유사도 + 6대 테마 점수 + 공통 태그 반환
def get_recommendation_detail(
    db: Session,
    content_id: int,
    work_id: int
):
    # 1. 콘텐츠 전체 태그 조회
    content_tags = get_content_tags(
        db = db,
        content_id=content_id
    )

    if not content_tags:
        return None
    
    # 2. 카테고리별 실제 매칭 점수 조회
    raw_category_scores = get_category_scores(
        db=db,
        content_id=content_id,
        work_id=work_id
    )

    raw_score_by_category = {
        row.category: float(row.raw_score)
        for row in raw_category_scores
    }

    # 3. 카테고리별 최대 가능 점수 계산
    max_score_by_category = defaultdict(float)

    for tag in content_tags:
        max_score_by_category[tag.tag.category] += (
            tag.weight * MAX_TAG_WEIGHT
        )

    # 4. 6대 테마별 유사도 계산
    category_scores = {}

    for category in TagCategory:
        category_value = category.value

        raw_score = raw_score_by_category.get(
            category_value,
            0
        )

        max_score = max_score_by_category.get(
            category_value,
            0
        )

        if max_score == 0:
            similarity_score = 0
        else:
            similarity_score = raw_score / max_score

        category_scores[category_value] = round(
            min(similarity_score, 1.0),
            3
        )

    # 5. 전체 유사도 계산
    total_raw_score = sum(
        raw_score_by_category.values()
    )

    total_max_score = (
        sum(tag.weight for tag in content_tags)
        * MAX_TAG_WEIGHT
    )

    total_similarity_score = (
        total_raw_score / total_max_score
        if total_max_score > 0
        else 0
    )

    # 6. 문학작품 전체 태그 조회
    literature_tag_rows = get_literature_tags(
        db=db,
        work_id=work_id
    )

    # 7. 콘텐츠와 문학작품의 공통 태그 조회
    matched_tag_rows = get_matched_tags(
        db=db,
        content_id=content_id,
        work_ids=[work_id]
    )

    matched_tag_ids = {
        row.tag_id
        for row in matched_tag_rows
    }

    # 8. 문학 태그에 공통 태그 여부 표시
    literature_tags = [
        {
            "tag_id": row.tag_id,
            "name": row.name,
            "category": row.category,
            "literature_weight": row.literature_weight,
            "is_matched": row.tag_id in matched_tag_ids,
        }
        for row in literature_tag_rows
    ]

    return {
        "content_id": content_id,
        "work_id": work_id,
        "similarity_score": round(
            min(total_similarity_score, 1.0),
            3
        ),
        "category_scores": category_scores,
        "literature_tags": literature_tags,
    }