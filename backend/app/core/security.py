### 비밀번호 해싱, JWT 생성, JWT 인증

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
import crud.user as user_crud
from database import get_db
import models

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
def verify_password(plain_password: str, hashed_password: str) -> str:
    return password_hasher.verify(plain_password, hashed_password)

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

# Swagger Authorization와 Bearer Token 인증에 사용
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT 검사, 현재 로그인 사용자 반환
def get_authenticated_user(
        access_token: str = Depends(oauth2_bearer),
        db: Session = Depends(get_db)
) -> models.User: 
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 올바르지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        token_payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=ALGORITHM
        )

        subject = token_payload.get("sub")

        if subject is None:
            raise authentication_error
        
        user_id = int(subject)
    
    except (JWTError, ValueError, TypeError):
        raise authentication_error
    
    authenticated_user = user_crud.get_user_by_id(
        user_id=user_id,
        db=db
    )

    if authenticated_user is None:
        raise authenticated_user
    
    return authenticated_user