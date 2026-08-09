import app.models 

import httpx
from app.database import SessionLocal
from app.domains.additional_info.model import LtiBibliographyCache

BASE_URL = "https://library.ltikorea.or.kr/api/open/bibliography"


def fetch_all_and_cache():
    db = SessionLocal()
    page = 1
    total_saved = 0

    try:
        while True:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(BASE_URL, params={"page": page, "items_per_page": 100})
                res.raise_for_status()
                data = res.json()

            items = data.get("list", [])
            if not items:
                break

            for item in items:
                nid = item.get("nid")
                if not nid:
                    continue

                existing = db.query(LtiBibliographyCache).filter(
                    LtiBibliographyCache.nid == nid
                ).first()
                if existing:
                    continue

                db.add(LtiBibliographyCache(
                    nid=nid,
                    original_title=item.get("originalTitle"),
                    author_kor=item.get("authorKor"),
                    author=item.get("author"),
                    language=item.get("language"),
                    translator=item.get("translator"),
                    publisher=item.get("publisher"),
                    isbn=item.get("isbn"),
                    published_year=item.get("publishedYear"),
                    image=item.get("image"),
                    url=item.get("url"),
                ))
                total_saved += 1

            db.commit()
            print(f"{page}페이지 완료 ({total_saved}건 누적)")

            if page * 100 >= data.get("count", 0):
                break
            page += 1

    finally:
        db.close()

    print(f"전체 동기화 완료: 총 {total_saved}건")


if __name__ == "__main__":
    fetch_all_and_cache()