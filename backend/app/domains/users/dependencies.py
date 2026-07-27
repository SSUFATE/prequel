### 로그인 사용자 인증 의존성

from app.core.security import decode_access_token
from app.database import get_db
from app.domains.users import crud as user_crud
from app.domains.users.model import User
from app.database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

# Swagger Authorization와 Bearer Token 인증에 사용
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT 검사, 현재 로그인 사용자 반환
def get_authenticated_user(
        access_token: str = Depends(oauth2_bearer),
        db: Session = Depends(get_db)
) -> User: 
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 올바르지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        token_payload = decode_access_token(access_token)
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
        raise authentication_error
    
    return authenticated_user