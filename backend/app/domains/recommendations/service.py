from collections import defaultdict

from sqlalchemy.orm import Session

from app.domains.kcontents.crud import get_kcontent_by_id
from app.domains.recommendations.crud import (
    get_content_tags,
    get_matched_tags,
    get_category_scores,
    get_literature_tags,
    get_tag_scored_literatures,
    get_embedding_scored_literatures,
)
from app.domains.recommendations.constants import MAX_TAG_WEIGHT
from app.domains.tags.constants import TagCategory


# 하이브리드 추천 가중치
TAG_WEIGHT = 0.4
EMBEDDING_WEIGHT = 0.6

# 태그/임베딩 각각 추출할 후보 수
CANDIDATE_LIMIT = 100


# 전체/테마별 content_id로 추천 문학 목록 반환
def get_recommendations_by_content_id(
    db: Session,
    content_id: int,
    limit: int = 5,
    category: TagCategory | None = None,
):
    # 1. 콘텐츠 태그 조회
    # category가 있으면 해당 테마의 태그만 조회
    content_tags = get_content_tags(
        db=db,
        content_id=content_id,
        category=category,
    )

    if not content_tags:
        return []

    # 2. 최대 가능 점수 계산
    max_possible_score = (
        sum(tag.weight for tag in content_tags)
        * MAX_TAG_WEIGHT
    )

    if max_possible_score == 0:
        return []

    # 3. 문학작품별 태그 점수 계산
    scored_works = get_tag_scored_literatures(
        db=db,
        content_id=content_id,
        limit=limit,
        category=category,
    )

    if not scored_works:
        return []

    selected_work_ids = [
        work.work_id
        for work, raw_score in scored_works
    ]

    # 4. 콘텐츠와 추천 작품의 공통 태그 조회
    matched_tag_rows = get_matched_tags(
        db=db,
        content_id=content_id,
        work_ids=selected_work_ids,
        category=category,
    )

    matched_tags_by_work = defaultdict(list)

    for row in matched_tag_rows:
        matched_tags_by_work[row.work_id].append(
            {
                "tag_id": row.tag_id,
                "name": row.name,
                "category": row.category,
                "content_weight": row.content_weight,
                "literature_weight": row.literature_weight,
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


# 문학 상세 화면: 전체 유사도 + 6대 테마 점수 + 문학 태그 반환
def get_recommendation_detail(
    db: Session,
    content_id: int,
    work_id: int,
):
    # 1. 콘텐츠 전체 태그 조회
    content_tags = get_content_tags(
        db=db,
        content_id=content_id,
    )

    if not content_tags:
        return None

    # 2. 카테고리별 실제 매칭 점수 조회
    raw_category_scores = get_category_scores(
        db=db,
        content_id=content_id,
        work_id=work_id,
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
            0,
        )

        max_score = max_score_by_category.get(
            category_value,
            0,
        )

        if max_score == 0:
            similarity_score = 0
        else:
            similarity_score = raw_score / max_score

        category_scores[category_value] = round(
            min(similarity_score, 1.0),
            3,
        )

    # 5. 전체 태그 유사도 계산
    total_raw_score = sum(
        raw_score_by_category.values()
    )

    total_max_score = (
        sum(tag.weight for tag in content_tags)
        * MAX_TAG_WEIGHT
    )

    tag_similarity_score = (
        total_raw_score / total_max_score
        if total_max_score > 0
        else 0
    )

    # 6. 하이브리드 유사도 계산
    content = get_kcontent_by_id(
        db=db,
        content_id=content_id,
    )

    # 임베딩이 없으면 기존 태그 유사도 사용
    total_similarity_score = tag_similarity_score

    if content is not None and content.embedding is not None:
        embedding_results = get_embedding_scored_literatures(
            db=db,
            content_embedding=content.embedding,
            work_ids=[work_id],
        )

        if embedding_results:
            embedding_score = max(
                0.0,
                min(float(embedding_results[0][1]), 1.0),
            )

            total_similarity_score = (
                TAG_WEIGHT * tag_similarity_score
                + EMBEDDING_WEIGHT * embedding_score
            )

    # 7. 문학작품 전체 태그 조회
    literature_tag_rows = get_literature_tags(
        db=db,
        work_id=work_id,
    )

    # 8. 콘텐츠와 문학작품의 공통 태그 조회
    matched_tag_rows = get_matched_tags(
        db=db,
        content_id=content_id,
        work_ids=[work_id],
    )

    matched_tag_ids = {
        row.tag_id
        for row in matched_tag_rows
    }

    # 9. 문학 태그에 공통 태그 여부 표시
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
            max(0.0, min(total_similarity_score, 1.0)),
            3,
        ),
        "category_scores": category_scores,
        "literature_tags": literature_tags,
    }


# 임베딩 기반 추천
def get_embedding_recommendations_by_content_id(
    db: Session,
    content_id: int,
    limit: int = 5,
):
    # 1. K콘텐츠 조회
    content = get_kcontent_by_id(
        db=db,
        content_id=content_id,
    )

    if content is None:
        return []

    # 2. 임베딩이 생성되지 않은 콘텐츠
    if content.embedding is None:
        return []

    # 3. 임베딩 유사도 기준 문학 검색
    scored_works = get_embedding_scored_literatures(
        db=db,
        content_embedding=content.embedding,
        limit=limit,
    )

    # 4. 응답 생성
    recommendations = []

    for work, embedding_score in scored_works:
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
                    max(0.0, min(float(embedding_score), 1.0)),
                    3,
                ),
                "matched_tags": [],
            }
        )

    return recommendations


# 태그 + 임베딩 하이브리드 추천
def get_hybrid_recommendations_by_content_id(
    db: Session,
    content_id: int,
    limit: int = 5,
):
    # 1. K콘텐츠 조회
    content = get_kcontent_by_id(
        db=db,
        content_id=content_id,
    )

    if content is None:
        return []

    # 임베딩이 없으면 태그 기반 추천
    if content.embedding is None:
        return get_recommendations_by_content_id(
            db=db,
            content_id=content_id,
            limit=limit,
        )

    # 2. 태그 유사도 정규화에 필요한 최대 점수
    content_tags = get_content_tags(
        db=db,
        content_id=content_id,
    )

    max_possible_score = (
        sum(tag.weight for tag in content_tags)
        * MAX_TAG_WEIGHT
    )

    # 3. 태그 기반 상위 100개 후보
    tag_candidates = get_tag_scored_literatures(
        db=db,
        content_id=content_id,
        limit=CANDIDATE_LIMIT,
    )

    # 4. 임베딩 기반 상위 100개 후보
    embedding_candidates = get_embedding_scored_literatures(
        db=db,
        content_embedding=content.embedding,
        limit=CANDIDATE_LIMIT,
    )

    # 5. 후보 ID 합치기 (중복 제거)
    candidate_ids = {
        work.work_id
        for work, _ in tag_candidates
    } | {
        work.work_id
        for work, _ in embedding_candidates
    }

    if not candidate_ids:
        return []

    candidate_ids = sorted(candidate_ids)

    # 6. 모든 후보의 태그 점수 조회
    tag_scored_works = get_tag_scored_literatures(
        db=db,
        content_id=content_id,
        work_ids=candidate_ids,
    )

    tag_score_map = {
        work.work_id: float(raw_score)
        for work, raw_score in tag_scored_works
    }

    # 7. 모든 후보의 임베딩 점수 조회
    embedding_scored_works = get_embedding_scored_literatures(
        db=db,
        content_embedding=content.embedding,
        work_ids=candidate_ids,
    )

    # 8. 하이브리드 점수 계산
    hybrid_works = []

    for work, embedding_score in embedding_scored_works:
        raw_tag_score = tag_score_map.get(
            work.work_id,
            0.0,
        )

        tag_score = (
            raw_tag_score / max_possible_score
            if max_possible_score > 0
            else 0.0
        )

        # 코사인 유사도 범위 보정
        embedding_score = max(
            0.0,
            min(float(embedding_score), 1.0),
        )

        hybrid_score = (
            TAG_WEIGHT * tag_score
            + EMBEDDING_WEIGHT * embedding_score
        )

        hybrid_works.append(
            (
                work,
                hybrid_score,
            )
        )

    # 9. 최종 점수 내림차순 정렬
    hybrid_works.sort(
        key=lambda item: (-item[1], item[0].work_id)
    )

    selected_works = hybrid_works[:limit]

    # 10. 추천 작품의 공통 태그 조회
    selected_work_ids = [
        work.work_id
        for work, _ in selected_works
    ]

    matched_tag_rows = get_matched_tags(
        db=db,
        content_id=content_id,
        work_ids=selected_work_ids,
    )

    matched_tags_by_work = defaultdict(list)

    for row in matched_tag_rows:
        matched_tags_by_work[row.work_id].append(
            {
                "tag_id": row.tag_id,
                "name": row.name,
                "category": row.category,
                "content_weight": row.content_weight,
                "literature_weight": row.literature_weight,
            }
        )

    # 11. 최종 추천 결과 생성
    recommendations = []

    for work, hybrid_score in selected_works:
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
                    max(0.0, min(hybrid_score, 1.0)),
                    3,
                ),
                "matched_tags": matched_tags_by_work[
                    work.work_id
                ],
            }
        )

    return recommendations