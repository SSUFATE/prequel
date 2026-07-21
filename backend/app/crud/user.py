### DB 작업 함수

from sqlalchemy.orm import Session
import models
from schemas.user import UserCreate, UserUpdate
from core.security import hash_password
from collections import defaultdict
from sqlalchemy import and_, func

# 새로운 사용자를 DB에 저장
def create_user(user: UserCreate, hashed_password: str, db: Session):
    db_user = models.User(
        login_id=user.login_id,
        password_hash=hashed_password,
        username=user.username,
        email=str(user.email),
        language=user.language.value
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# user_id로 사용자 조회: JWT 인증 후 현재 사용자 찾을 때 사용
def get_user_by_id(user_id: int, db: Session) -> models.User | None:
    return (
        db.query(models.User)
        .filter(models.User.user_id == user_id)
        .first()
    ) 

# login_id로 사용자 조회: 로그인 및 회원가입 중복 검사
def get_user_by_login_id(login_id: str, db: Session) -> models.User | None:
    return (
        db.query(models.User)
        .filter(models.User.login_id == login_id)
        .first()
    )

# email로 사용자 조회: 회원가입 중복 검사
def get_user_by_email(email: str, db: Session) -> models.User | None:
    return (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )

# 회원 정보 수정
def update_user(db: Session, db_user: models.User, user_update: UserUpdate):
    # 수정 정보만 반영
    update_data = user_update.model_dump(
        exclude_unset=True
    )

    # 수정 정보에 비밀번호가 있다면 비밀번호 해싱
    if "password" in update_data:
        update_data["password"] = hash_password(
            update_data["password"]
        )

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)

    return db_user

# 회원 삭제
def delete_user(db: Session, db_user: models.User):
    db.delete(db_user)
    db.commit()
    return db_user

# K콘텐츠 하나 조회
def get_kcontent_by_id(db: Session, content_id: int):
    return (
        db.query(models.KContent)
        .filter(
            models.KContent.content_id == content_id
        ).first()
    )

# 작품별 추천 점수 계산
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
            models.KContetnTag,
            and_(
                models.KContentTag.tag_id
                == models.LiteraryWorkTag.tag_id,

                models.KContentTag.tag_id
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
