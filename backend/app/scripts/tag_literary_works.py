# """
# 아직 태그가 없는 LiteraryWork들을 순회하면서 OpenAI(gpt-4o-mini)로
# 6개 카테고리(ERA_SETTING, GENRE, SUBJECT, MOOD, RELATIONSHIP, CULTURAL_CONTEXT)
# 태그를 붙이는 스크립트.

# 규칙: 카테고리마다 최소 1개, 전체 합쳐서 최대 8개.

# 사용법:
#     python -m scripts.tag_literary_works              # 전체 대상 처리
#     python -m scripts.tag_literary_works --limit 20    # 20건만
#     python -m scripts.tag_literary_works --work-id 5   # 특정 작품 하나만 (재태깅)
# """
# import app.models 
# import argparse
# import json
# import time
# from collections import defaultdict

# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.domains.literatures.model import LiteraryWork
# from app.domains.tags.model import Tag, LiteraryWorkTag
# from app.domains.tags.constants import TagCategory
# from app.external.openai.openai_client import get_openai_client

# MODEL = "gpt-4o-mini"
# MIN_PER_CATEGORY = 1
# MAX_TOTAL_TAGS = 8
# CREATED_BY = f"openai:{MODEL}"

# CATEGORY_LABELS = {
#     TagCategory.ERA_SETTING: "시대·배경",
#     TagCategory.GENRE: "장르",
#     TagCategory.SUBJECT: "소재·주제",
#     TagCategory.MOOD: "정서·분위기",
#     TagCategory.RELATIONSHIP: "인물 관계",
#     TagCategory.CULTURAL_CONTEXT: "한국 사회·문화적 맥락",
# }


# def load_tags_by_category(db: Session) -> dict[TagCategory, list[Tag]]:
#     """DB의 category는 plain string(예: 'GENRE')이라 TagCategory enum으로 변환해서 그룹핑"""
#     tags = db.query(Tag).order_by(Tag.category, Tag.tag_id).all()
#     grouped: dict[TagCategory, list[Tag]] = defaultdict(list)
#     for tag in tags:
#         try:
#             category = TagCategory(tag.category)
#         except ValueError:
#             print(f"  [경고] 알 수 없는 category 무시: tag_id={tag.tag_id}, category={tag.category}")
#             continue
#         grouped[category].append(tag)
#     return grouped


# def build_tag_catalog_text(tags_by_category: dict[TagCategory, list[Tag]]) -> str:
#     lines = []
#     for category in TagCategory:
#         lines.append(f"\n[{CATEGORY_LABELS[category]} / {category.value}]")
#         for tag in tags_by_category[category]:
#             guide = (tag.selection_guide or "").strip()
#             lines.append(f"  - id={tag.tag_id} {tag.name}: {guide}")
#     return "\n".join(lines)


# def build_json_schema() -> dict:
#     category_array_schema = {
#         "type": "array",
#         "items": {"type": "integer"},
#         "description": "선택한 태그의 tag_id 목록 (최소 1개)",
#     }
#     return {
#         "type": "object",
#         "properties": {category.value: category_array_schema for category in TagCategory},
#         "required": [category.value for category in TagCategory],
#         "additionalProperties": False,
#     }


# def build_prompt(work: LiteraryWork, tags_by_category: dict[TagCategory, list[Tag]]) -> list[dict]:
#     catalog = build_tag_catalog_text(tags_by_category)

#     system_prompt = (
#         "너는 한국 문학작품에 구조화된 태그를 붙이는 전문가야. "
#         "주어진 작품 정보와 태그 카탈로그를 보고, 각 카테고리(6개)에서 "
#         f"최소 {MIN_PER_CATEGORY}개, 전체 태그 개수는 합쳐서 최대 {MAX_TOTAL_TAGS}개가 되도록 "
#         "가장 적합한 태그의 id만 골라줘. "
#         "각 태그의 selection_guide 기준을 충실히 따르고, 애매하면 그 카테고리에서 "
#         "가장 대표성이 높은 태그 1개만 선택해."
#     )

#     work_info = (
#         f"제목: {work.title}\n"
#         f"저자: {work.author or '알 수 없음'}\n"
#         f"장르(원본): {work.genre or '알 수 없음'}\n"
#         f"발행년도: {work.published_year or '알 수 없음'}\n"
#         f"줄거리/소개: {work.summary or '(소개 정보 없음)'}"
#     )

#     user_prompt = f"[작품 정보]\n{work_info}\n\n[태그 카탈로그]{catalog}"

#     return [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_prompt},
#     ]


# def call_openai_for_tags(work: LiteraryWork, tags_by_category: dict[TagCategory, list[Tag]]) -> dict[str, list[int]]:
#     client = get_openai_client()
#     messages = build_prompt(work, tags_by_category)

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=messages,
#         response_format={
#             "type": "json_schema",
#             "json_schema": {
#                 "name": "literary_work_tags",
#                 "schema": build_json_schema(),
#                 "strict": True,
#             },
#         },
#     )

#     content = response.choices[0].message.content
#     return json.loads(content)


# def validate_and_normalize(
#     result: dict[str, list[int]],
#     tags_by_category: dict[TagCategory, list[Tag]],
# ) -> list[int] | None:
#     """
#     규칙 검증: 카테고리당 최소 1개, 전체 최대 8개.
#     유효한 tag_id인지도 확인. 위반하면 None 반환(해당 작품 스킵).
#     """
#     valid_ids_by_category = {
#         category: {tag.tag_id for tag in tags} for category, tags in tags_by_category.items()
#     }

#     all_ids: list[int] = []

#     for category in TagCategory:
#         selected = result.get(category.value, [])
#         selected = [tid for tid in selected if tid in valid_ids_by_category[category]]

#         if len(selected) < MIN_PER_CATEGORY:
#             print(f"  [경고] {category.value} 카테고리에 태그가 없어서 스킵함")
#             return None

#         all_ids.extend(selected)

#     if len(all_ids) > MAX_TOTAL_TAGS:
#         per_category: dict[TagCategory, list[int]] = {}
#         for category in TagCategory:
#             selected = [tid for tid in result.get(category.value, []) if tid in valid_ids_by_category[category]]
#             per_category[category] = selected

#         trimmed: list[int] = [ids[0] for ids in per_category.values()]
#         extras = [tid for ids in per_category.values() for tid in ids[1:]]
#         remaining_slots = MAX_TOTAL_TAGS - len(trimmed)
#         trimmed.extend(extras[:remaining_slots])
#         all_ids = trimmed

#     return all_ids


# def tag_work(db: Session, work: LiteraryWork, tags_by_category: dict[TagCategory, list[Tag]]) -> bool:
#     try:
#         result = call_openai_for_tags(work, tags_by_category)
#     except Exception as e:
#         print(f"  [실패] OpenAI 호출 오류: {e}")
#         return False

#     tag_ids = validate_and_normalize(result, tags_by_category)
#     if tag_ids is None:
#         return False

#     # 기존 태그 있으면 지우고 새로 저장 (재태깅 지원)
#     db.query(LiteraryWorkTag).filter(LiteraryWorkTag.work_id == work.work_id).delete()

#     for tag_id in tag_ids:
#         db.add(LiteraryWorkTag(work_id=work.work_id, tag_id=tag_id, created_by=CREATED_BY))

#     db.commit()
#     print(f"  [완료] {len(tag_ids)}개 태그 저장: {tag_ids}")
#     return True


# def run(limit: int | None = None, work_id: int | None = None) -> None:
#     db = SessionLocal()

#     try:
#         tags_by_category = load_tags_by_category(db)
#         if len(tags_by_category) != len(TagCategory):
#             missing = set(TagCategory) - set(tags_by_category.keys())
#             print(f"[중단] tags 테이블에 없는 카테고리가 있습니다: {missing}. 먼저 seed_tags를 실행하세요.")
#             return

#         if work_id is not None:
#             works = db.query(LiteraryWork).filter(LiteraryWork.work_id == work_id).all()
#         else:
#             tagged_work_ids = {row[0] for row in db.query(LiteraryWorkTag.work_id).distinct()}
#             query = db.query(LiteraryWork).filter(~LiteraryWork.work_id.in_(tagged_work_ids))
#             if limit:
#                 query = query.limit(limit)
#             works = query.all()

#         print(f"대상 작품 수: {len(works)}")

#         success_count = 0
#         for i, work in enumerate(works, start=1):
#             print(f"[{i}/{len(works)}] {work.title} (work_id={work.work_id})")
#             if tag_work(db, work, tags_by_category):
#                 success_count += 1
#             time.sleep(0.3)

#         print(f"\n완료: {success_count}/{len(works)}건 성공")

#     finally:
#         db.close()


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--limit", type=int, default=None, help="처리할 최대 작품 수")
#     parser.add_argument("--work-id", type=int, default=None, help="특정 작품 하나만 재태깅")
#     args = parser.parse_args()

#     run(limit=args.limit, work_id=args.work_id)