"""literatures 테이블의 title/author로 카카오 책 검색 API를 호출해
isbn13, cover_url 만 채워 넣는 스크립트.

환경변수:
  KAKAO_REST_API_KEY  카카오 REST API 키
  DATABASE_URL        postgresql://user:pass@host:5432/dbname

사용:
  pip install requests psycopg2-binary
  python fill_isbn_cover.py --dry-run --limit 20   # DB는 건드리지 않고 매칭 결과만 확인
  python fill_isbn_cover.py                        # isbn13 또는 cover_url이 빈 행만 채움

동작 원칙:
  - 이미 값이 있는 isbn13 / cover_url 은 덮어쓰지 않는다.
  - title, author 외의 컬럼(embedding 등)은 읽지도 쓰지도 않는다.
  - 매칭에 실패한 작품은 not_found.csv 에 저장한다 (수동 확인용).
"""
import argparse
import csv
import os
import re
import sys
import time

import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 읽기

KAKAO_URL = "https://dapi.kakao.com/v3/search/book"


def norm(s):
    """공백/특수문자 제거 + 소문자화 (비교용)."""
    return re.sub(r"[\s\W_]+", "", s or "").lower()


def isbn10_to_13(isbn10):
    core = "978" + isbn10[:9]
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(core))
    return core + str((10 - total % 10) % 10)


def extract_isbn13(isbn_field):
    """카카오 isbn 필드('ISBN10 ISBN13' 또는 하나만)에서 ISBN13을 뽑는다."""
    parts = (isbn_field or "").split()
    for p in parts:
        if len(p) == 13 and p.isdigit():
            return p
    for p in parts:
        if len(p) == 10 and p[:9].isdigit():
            return isbn10_to_13(p)
    return ""


def search(session, key, title, author):
    params = {"query": f"{title} {author}".strip(), "size": 10}
    headers = {"Authorization": f"KakaoAK {key}"}
    for attempt in range(3):
        r = session.get(KAKAO_URL, params=params, headers=headers, timeout=10)
        if r.status_code == 429:  # 호출 제한 -> 잠깐 쉬고 재시도
            time.sleep(1 + attempt)
            continue
        r.raise_for_status()
        return r.json().get("documents", [])
    return []


def pick(docs, title, author):
    """제목이 같고 저자가 겹치며, ISBN13과 표지가 모두 있는 첫 후보를 고른다."""
    t, a = norm(title), norm(author)
    best, best_score = None, 0
    for d in docs:
        isbn13 = extract_isbn13(d.get("isbn"))
        thumb = d.get("thumbnail") or ""
        if not isbn13 or not thumb:
            continue

        dt = norm(d.get("title"))
        if dt == t:
            score = 3
        elif dt.startswith(t):  # "소나기 (개정판)" 같은 경우
            score = 1
        else:
            continue

        if a:
            authors = d.get("authors") or []
            if any(norm(x) and (norm(x) in a or a in norm(x)) for x in authors):
                score += 2
            else:
                continue

        if score > best_score:  # 동점이면 카카오 정확도 순서상 먼저 나온 것 유지
            best, best_score = {"isbn13": isbn13, "cover_url": thumb}, score
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="DB를 수정하지 않고 결과만 출력")
    ap.add_argument("--limit", type=int, default=0, help="처리할 최대 행 수 (0이면 전체)")
    args = ap.parse_args()

    key = os.environ.get("KAKAO_REST_API_KEY")
    dsn = os.environ.get("POSTGRESQL_URL")

    if dsn:
        dsn = dsn.replace("postgresql+psycopg2://", "postgresql://", 1)

    if not key or not dsn:
        sys.exit("KAKAO_REST_API_KEY 와 POSTGRESQL_URL 환경변수를 설정하세요.")

    conn = psycopg2.connect(dsn)
    session = requests.Session()

    sql = """
        SELECT work_id, title, author
        FROM literatures
        WHERE isbn13 IS NULL OR isbn13 = '' OR cover_url IS NULL OR cover_url = ''
        ORDER BY work_id
    """
    if args.limit:
        sql += f" LIMIT {int(args.limit)}"

    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    print(f"대상 {len(rows)}건")

    found = missed = 0
    with open("not_found.csv", "w", encoding="utf-8", newline="") as nf:
        nw = csv.writer(nf)
        nw.writerow(["work_id", "title", "author"])

        for i, (work_id, title, author) in enumerate(rows, 1):
            try:
                hit = pick(search(session, key, title, author), title, author)
            except requests.RequestException as e:
                print(f"[{i}] ERR {title}: {e}")
                hit = None

            if not hit:
                missed += 1
                nw.writerow([work_id, title, author])
                print(f"[{i}] NOT FOUND  {title} / {author}")
            else:
                found += 1
                print(f"[{i}] OK  {title} / {author} -> {hit['isbn13']}  {hit['cover_url']}")
                if not args.dry_run:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE literatures
                            SET isbn13    = COALESCE(NULLIF(isbn13, ''), %s),
                                cover_url = COALESCE(NULLIF(cover_url, ''), %s)
                            WHERE work_id = %s
                            """,
                            (hit["isbn13"], hit["cover_url"], work_id),
                        )
                    if i % 50 == 0:
                        conn.commit()
            time.sleep(0.05)

    if not args.dry_run:
        conn.commit()
    conn.close()
    print(f"완료: 성공 {found} / 실패 {missed}  (실패 목록: not_found.csv)")


if __name__ == "__main__":
    main()