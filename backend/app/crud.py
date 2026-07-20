### DB 작업 함수

from sqlalchemy.orm import Session
import models
from schemas import UserCreate

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