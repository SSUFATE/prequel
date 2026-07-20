### Pydantic 모델: API 요청/응답 데이터 정의
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    KO = "ko"
    EN = "en"
    JA = "ja"

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


# 회원가입 요청 데이터
class UserCreate(BaseModel):
    login_id: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    language: Language = Language.KO

# 사용자 정보 응답
class UserResponse(BaseModel):
    user_id: int
    login_id: str
    username: str
    email: EmailStr
    language: Language
    role: UserRole
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 로그인 성공 응답
class TokenResponse(BaseModel):
    access_token: str
    token_type: str