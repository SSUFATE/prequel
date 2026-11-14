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
    EXACT 매칭용 정규화.
    - 앞뒤 공백 제거
    - 소문자 변환
    - 모든 공백 제거
    """
    if not value:
        return ""

    value = value.strip().lower()
    value = re.sub(r"\s+", "", value)

    return value


def split_authors(value: str | None) -> list[str]:
    """
    LTI author_kor에 여러 작가가 들어있는 경우 분리.

    예:
    '공선옥,김소진,황순원'
    -> ['공선옥', '김소진', '황순원']
    """
    if not value:
        return []

    return [
        normalize_text(author)
        for author in value.split(",")
        if normalize_text(author)
    ]


def parse_year(value: str | None) -> int | None:
    """
    published_year에서 4자리 연도만 추출.
    """
    if not value:
        return None

    match = re.search(r"\d{4}", value)

    if not match:
        return None

    return int(match.group())


def contains_title_as_unit(
    literature_title: str,
    lti_title: str,
) -> bool:
    """
    작품명이 LTI 원제 안에서 독립적인 제목 단위로
    존재하는지 검사한다.

    허용:
        가난한 사랑 노래
        -> 가난한 사랑노래: 신경림 시선집

        학
        -> 학: 황순원 단편선

        소
        -> 소, 토막, 당나귀

        별
        -> 단편소설선 <별>

    제외:
        학
        -> 한국문학 단편선

        꽃
        -> 꽃을 위한 서시

        아버지
        -> 아버지의 눈물
    """
    if not literature_title or not lti_title:
        return False

    # 제목 내부 공백은 무시
    lit = re.sub(
        r"\s+",
        "",
        literature_title.strip().lower(),
    )

    lti = re.sub(
        r"\s+",
        "",
        lti_title.strip().lower(),
    )

    if not lit or not lti:
        return False

    if lit == lti:
        return True

    # 작품명이 등장하는 모든 위치 검사
    start = 0

    while True:
        index = lti.find(lit, start)

        if index == -1:
            return False

        before_index = index - 1
        after_index = index + len(lit)

        before_char = (
            lti[before_index]
            if before_index >= 0
            else None
        )

        after_char = (
            lti[after_index]
            if after_index < len(lti)
            else None
        )

        # 앞 문자가 한글/영문/숫자가 아니어야 함
        before_ok = (
            before_char is None
            or not re.match(
                r"[가-힣a-zA-Z0-9]",
                before_char,
            )
        )

        # 뒤 문자도 한글/영문/숫자가 아니어야 함
        after_ok = (
            after_char is None
            or not re.match(
                r"[가-힣a-zA-Z0-9]",
                after_char,
            )
        )

        if before_ok and after_ok:
            return True

        start = index + 1


def is_safe_title_match(
    literature_title: str,
    lti_title: str,
) -> bool:
    """
    EXACT가 실패했을 때 사용하는 SAFE 제목 매칭.
    """
    lit_normalized = normalize_text(
        literature_title
    )

    lti_normalized = normalize_text(
        lti_title
    )

    if not lit_normalized or not lti_normalized:
        return False

    # 1. 정규화 후 동일
    if lit_normalized == lti_normalized:
        return True

    # 2. 작품명 뒤에 권수/서지 정보가 붙은 경우
    #
    # 태백산맥 -> 태백산맥 1
    # 송곳 -> 송곳. 1
    # 지리산 -> 지리산 (상)
    # 우상의 눈물 -> 우상의 눈물 (가제)
    # 미생 -> 미생 시리즈 (가제)
    # 황토기 -> 황토기 외

    if lti_normalized.startswith(
        lit_normalized
    ):
        suffix = lti_normalized[
            len(lit_normalized):
        ]

        safe_suffix_patterns = [
            r"^\d+$",
            r"^\.\d+$",
            r"^\((상|하|가제)\)$",
            r"^(상|하)\.?$",
            r"^시리즈.*$",
            r"^외$",
        ]

        for pattern in safe_suffix_patterns:
            if re.match(pattern, suffix):
                return True

    # 3. 작품명이 선집/합본 등에 독립적으로 포함
    if contains_title_as_unit(
        literature_title,
        lti_title,
    ):
        return True

    return False


def find_literature_match(
    item: LtiBibliographyCache,
    literatures: list[LiteraryWork],
    literature_map: dict,
):
    """
    LTI 한 건에 대해 문학 작품을 찾는다.

    반환:
        (literature, "EXACT")
        (literature, "SAFE")
        (None, None)
    """
    original_title = normalize_text(
        item.original_title
    )

    authors = split_authors(
        item.author_kor
    )

    if not original_title or not authors:
        return None, None

    # ------------------------------------------
    # 1순위: EXACT
    # ------------------------------------------
    for author in authors:
        key = (
            original_title,
            author,
        )

        literature = literature_map.get(key)

        if literature:
            return literature, "EXACT"

    # ------------------------------------------
    # 2순위: SAFE
    # ------------------------------------------
    for candidate in literatures:

        candidate_author = normalize_text(
            candidate.author
        )

        # 작가 일치는 필수
        if candidate_author not in authors:
            continue

        if is_safe_title_match(
            candidate.title,
            item.original_title,
        ):
            return candidate, "SAFE"

    return None, None


def sync_lti_translations():
    db = SessionLocal()

    created = 0
    exact_created = 0
    safe_created = 0

    already_exists = 0
    unmatched = 0
    invalid = 0

    try:
        # ------------------------------------------
        # 문학 작품 로드
        # ------------------------------------------
        literatures = (
            db.query(LiteraryWork)
            .all()
        )

        print(
            f"문학 작품: "
            f"{len(literatures)}건"
        )

        # ------------------------------------------
        # EXACT 검색용 map
        # ------------------------------------------
        literature_map = {}

        for literature in literatures:

            title = normalize_text(
                literature.title
            )

            author = normalize_text(
                literature.author
            )

            if not title or not author:
                continue

            key = (
                title,
                author,
            )

            if key in literature_map:
                print(
                    "[주의] 동일 제목 + 작가 작품 존재: "
                    f"{literature.title} / "
                    f"{literature.author}"
                )
                continue

            literature_map[key] = literature

        # ------------------------------------------
        # LTI 캐시 로드
        # ------------------------------------------
        lti_items = (
            db.query(LtiBibliographyCache)
            .all()
        )

        print(
            f"LTI 번역서지: "
            f"{len(lti_items)}건"
        )

        print("=" * 100)

        # ------------------------------------------
        # 이미 저장된 LTI nid
        # ------------------------------------------
        existing_nids = {
            row[0]
            for row in (
                db.query(Translation.lti_nid)
                .filter(
                    Translation.lti_nid.isnot(None)
                )
                .all()
            )
        }

        # ------------------------------------------
        # LTI 전체 처리
        # ------------------------------------------
        for index, item in enumerate(
            lti_items,
            start=1,
        ):

            # nid 없음
            if not item.nid:
                invalid += 1
                continue

            # 이미 Translation에 존재
            if item.nid in existing_nids:
                already_exists += 1
                continue

            # 필수 매칭 정보 확인
            if (
                not normalize_text(item.original_title)
                or not split_authors(item.author_kor)
            ):
                invalid += 1
                continue

            # --------------------------------------
            # 문학 작품 매칭
            # --------------------------------------
            literature, match_type = (
                find_literature_match(
                    item=item,
                    literatures=literatures,
                    literature_map=literature_map,
                )
            )

            if literature is None:
                unmatched += 1
                continue

            # --------------------------------------
            # Translation 생성
            # --------------------------------------
            translation = Translation(
                work_id=literature.work_id,
                lti_nid=item.nid,

                translated_title=item.title,

                author=item.author,

                language=(
                    item.language
                    or "Unknown"
                ),

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

            existing_nids.add(
                item.nid
            )

            created += 1

            if match_type == "EXACT":
                exact_created += 1

            elif match_type == "SAFE":
                safe_created += 1

            print(
                f"[{index}/{len(lti_items)}] "
                f"{match_type} | "
                f"{literature.title} / "
                f"{literature.author}"
                f" <- "
                f"{item.original_title} / "
                f"{item.author_kor}"
                f" -> "
                f"{item.title} "
                f"({item.language})"
            )

            # --------------------------------------
            # 100건마다 commit
            # --------------------------------------
            if created % 100 == 0:
                db.commit()

        # 남은 데이터 commit
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    # ------------------------------------------
    # 결과 출력
    # ------------------------------------------
    print()
    print("=" * 100)
    print(
        "LTI -> Translation 동기화 완료"
    )
    print("=" * 100)

    print(
        f"새로 생성:       "
        f"{created}건"
    )

    print(
        f"  - EXACT:       "
        f"{exact_created}건"
    )

    print(
        f"  - SAFE:        "
        f"{safe_created}건"
    )

    print(
        f"이미 존재:       "
        f"{already_exists}건"
    )

    print(
        f"매칭 실패:       "
        f"{unmatched}건"
    )

    print(
        f"정보 부족:       "
        f"{invalid}건"
    )


if __name__ == "__main__":
    sync_lti_translations()