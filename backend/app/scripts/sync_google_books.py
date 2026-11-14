import os
import time

import httpx
from dotenv import load_dotenv

import app.models
from app.database import SessionLocal
from app.domains.additional_info.model import Translation


load_dotenv()

BASE_URL = "https://www.googleapis.com/books/v1/volumes"
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


def fetch_google_book(client: httpx.Client, isbn: str):
    response = client.get(
        BASE_URL,
        params={
            "q": f"isbn:{isbn}",
            "maxResults": 1,
            "key": API_KEY,
        },
    )

    # 요청 제한은 검색 결과 없음과 구분
    if response.status_code == 429:
        raise RuntimeError("GOOGLE_BOOKS_RATE_LIMIT")

    response.raise_for_status()

    data = response.json()
    items = data.get("items", [])

    if not items:
        return None

    return items[0]


def sync_google_books():
    if not API_KEY:
        raise RuntimeError(
            "GOOGLE_BOOKS_API_KEY가 .env에 설정되어 있지 않습니다."
        )

    db = SessionLocal()

    found = 0
    not_found = 0
    skipped = 0
    error = 0
    rate_limited = 0

    try:
        translations = (
            db.query(Translation)
            .filter(Translation.isbn.isnot(None))
            .filter(Translation.google_books_id.is_(None))
            .all()
        )

        total = len(translations)

        print(f"Google Books 조회 대상: {total}건")
        print("=" * 80)

        with httpx.Client(timeout=15.0) as client:
            for index, translation in enumerate(
                translations,
                start=1,
            ):
                isbn = (
                    translation.isbn.strip()
                    if translation.isbn
                    else None
                )

                if not isbn:
                    skipped += 1
                    continue

                try:
                    item = fetch_google_book(
                        client,
                        isbn,
                    )

                    # Google Books에 해당 ISBN 없음
                    if item is None:
                        not_found += 1

                        print(
                            f"[{index}/{total}] "
                            f"검색 결과 없음: {isbn}"
                        )

                        time.sleep(0.2)
                        continue

                    volume_info = item.get(
                        "volumeInfo",
                        {},
                    )

                    sale_info = item.get(
                        "saleInfo",
                        {},
                    )

                    # Google Books ID
                    translation.google_books_id = (
                        item.get("id")
                    )

                    # 미리보기
                    translation.preview_url = (
                        volume_info.get("previewLink")
                    )

                    # 구매 링크가 있을 때만 저장
                    translation.purchase_url = (
                        sale_info.get("buyLink")
                    )

                    found += 1

                    print(
                        f"[{index}/{total}] "
                        f"검색 성공: {isbn} "
                        f"→ {item.get('id')}"
                    )

                    # 50건 단위 저장
                    if found % 50 == 0:
                        db.commit()

                except RuntimeError as e:
                    if str(e) == "GOOGLE_BOOKS_RATE_LIMIT":
                        rate_limited += 1

                        print(
                            f"[{index}/{total}] "
                            f"429 요청 제한: {isbn}"
                        )

                        # 제한 발생 시 조금 길게 대기
                        time.sleep(5)

                    else:
                        error += 1
                        print(
                            f"[{index}/{total}] "
                            f"오류: {isbn} / {e}"
                        )

                except httpx.HTTPStatusError as e:
                    error += 1

                    print(
                        f"[{index}/{total}] "
                        f"HTTP 오류: {isbn} / {e}"
                    )

                except Exception as e:
                    error += 1

                    print(
                        f"[{index}/{total}] "
                        f"오류: {isbn} / {e}"
                    )

                # API 요청 간격
                time.sleep(0.2)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    print()
    print("=" * 80)
    print("Google Books 동기화 완료")
    print("=" * 80)
    print(f"검색 성공:       {found}건")
    print(f"검색 결과 없음: {not_found}건")
    print(f"요청 제한:       {rate_limited}건")
    print(f"건너뜀:          {skipped}건")
    print(f"오류:            {error}건")


if __name__ == "__main__":
    sync_google_books()