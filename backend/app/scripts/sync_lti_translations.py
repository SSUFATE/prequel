import re

import app.models

from app.database import SessionLocal
from app.domains.literatures.model import LiteraryWork
from app.domains.additional_info.model import (
    LtiBibliographyCache,
    Translation,
)


def normalize_text(value: str | None) -> str:
    """
    작품명/작가명 매칭을 위한 정규화.

    예:
    ' 채식주의자 ' -> '채식주의자'
    '한 강'        -> '한강'
    """

    if not value:
        return ""

    value = value.strip().lower()

    # 일반 공백 / 탭 / 줄바꿈 등 제거
    value = re.sub(r"\s+", "", value)

    return value


def parse_year(value: str | None) -> int | None:
    """
    LTI published_year는 문자열이므로
    Translation의 Integer 컬럼에 맞게 변환한다.
    """

    if not value:
        return None

    match = re.search(r"\d{4}", value)

    if not match:
        return None

    return int(match.group())


def sync_lti_translations():
    db = SessionLocal()

    created = 0
    already_exists = 0
    unmatched = 0
    invalid = 0

    try:
        # ---------------------------------------
        # 1. 우리 서비스의 문학 작품 가져오기
        # ---------------------------------------
        literatures = db.query(LiteraryWork).all()

        print(f"문학 작품: {len(literatures)}건")

        # ---------------------------------------
        # 2. 제목 + 작가명을 key로 lookup 생성
        # ---------------------------------------
        literature_map = {}

        for literature in literatures:
            title = normalize_text(literature.title)
            author = normalize_text(literature.author)

            if not title or not author:
                continue

            key = (title, author)

            # 같은 제목 + 같은 작가가 여러 개 존재하는지 확인
            if key in literature_map:
                print(
                    "[주의] 동일한 제목 + 작가 작품 존재: "
                    f"{literature.title} / {literature.author}"
                )
                continue

            literature_map[key] = literature

        # ---------------------------------------
        # 3. LTI 데이터 전체 조회
        # ---------------------------------------
        lti_items = db.query(LtiBibliographyCache).all()

        print(f"LTI 번역서지: {len(lti_items)}건")
        print("=" * 80)

        # ---------------------------------------
        # 4. 기존 Translation의 lti_nid 조회
        # ---------------------------------------
        existing_nids = {
            row[0]
            for row in (
                db.query(Translation.lti_nid)
                .filter(Translation.lti_nid.isnot(None))
                .all()
            )
        }

        # ---------------------------------------
        # 5. LTI ↔ literature 매칭
        # ---------------------------------------
        for index, item in enumerate(lti_items, start=1):

            if not item.nid:
                invalid += 1
                continue

            # 이미 translations에 저장되어 있으면 건너뜀
            if item.nid in existing_nids:
                already_exists += 1
                continue

            original_title = normalize_text(
                item.original_title
            )

            author_kor = normalize_text(
                item.author_kor
            )

            if not original_title or not author_kor:
                invalid += 1
                continue

            key = (
                original_title,
                author_kor,
            )

            literature = literature_map.get(key)

            # -----------------------------------
            # 매칭 실패
            # -----------------------------------
            if literature is None:
                unmatched += 1

                continue

            # -----------------------------------
            # 6. Translation 생성
            # -----------------------------------
            translation = Translation(
                work_id=literature.work_id,

                lti_nid=item.nid,

                translated_title=item.title,

                author=item.author,

                language=item.language or "Unknown",

                country=item.country,

                translator=item.translator,

                publisher=item.publisher,

                isbn=item.isbn,

                published_year=parse_year(
                    item.published_year
                ),

                description=item.description,

                cover_url=item.image,

                source_url=item.url,
            )

            db.add(translation)

            existing_nids.add(item.nid)
            created += 1

            print(
                f"[{index}/{len(lti_items)}] "
                f"매칭: "
                f"{literature.title} / "
                f"{literature.author}"
                f" -> "
                f"{item.title} "
                f"({item.language})"
            )

            # 100건마다 commit
            if created % 100 == 0:
                db.commit()

        # 남은 데이터 저장
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    print()
    print("=" * 80)
    print("LTI -> Translation 동기화 완료")
    print("=" * 80)

    print(f"새로 생성:       {created}건")
    print(f"이미 존재:       {already_exists}건")
    print(f"매칭 실패:       {unmatched}건")
    print(f"정보 부족:       {invalid}건")


if __name__ == "__main__":
    sync_lti_translations()