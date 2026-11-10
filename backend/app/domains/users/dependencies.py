### 쿠키에서 JWT 추출 및 검증

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.domains.users import crud as user_crud
from app.domains.users.model import User


# HttpOnly Cookie에서 JWT를 가져오기 위한 쿠키 이름
COOKIE_NAME = "access_token"


def get_authenticated_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:

    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 올바르지 않거나 만료되었습니다.",
    )

    # HttpOnly Cookie에서 JWT 가져오기
    access_token = request.cookies.get(COOKIE_NAME)

    if not access_token:
        raise authentication_error

    # JWT 검증 및 사용자 ID 추출
    try:
        token_payload = decode_access_token(access_token)
        subject = token_payload.get("sub")

        if subject is None:
            raise authentication_error

        user_id = int(subject)

    except (JWTError, ValueError, TypeError):
        raise authentication_error

    # DB에서 사용자 확인
    authenticated_user = user_crud.get_user_by_id(
        user_id=user_id,
        db=db,
    )

    if authenticated_user is None:
        raise authentication_error

    if not authenticated_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다.",
        )

    return authenticated_user
