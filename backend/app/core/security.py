### 비밀번호 해싱, JWT 생성, JWT 인증

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY가 .env에 설정되어 있지 않습니다."
    )

# Argon2 사용
password_hasher = PasswordHash.recommended()

# 비밀번호 암호화
def hash_password(plain_password: str) -> str:
    return password_hasher.hash(plain_password)

# 비밀번호 확인
def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
    return password_hasher.verify(
        plain_password,
        hashed_password
    )

# 로그인 성공 시, JWT Access Token 발급
def create_access_token(user_id: int) -> str:
    expiration_time = (
        datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    token_payload = {
        "sub": str(user_id),
        "exp": expiration_time
    }

    access_token = jwt.encode(
        token_payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token

# JWT 토큰 복호화
def decode_access_token(access_token: str) -> dict:
    return jwt.decode(
        access_token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )


# 요청 헤더에서 Bearer 토큰을 꺼내는 스킴
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# 현재 로그인한 사용자를 조회하는 의존성 함수
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    from app.domains.users.model import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user