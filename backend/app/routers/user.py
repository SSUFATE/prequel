### 회원가입, 로그인, 로그아웃 API
### 회원 조회, 회원정보 수정, 회원 탈퇴 API
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import crud.user as user_crud
from database import get_db
from schemas.user import UserCreate, UserResponse, TokenResponse, UserUpdate, MessageResponse
from core.security import verify_password, create_access_token, get_authenticated_user, hash_password
import models
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["Users"]
)

# 회원가입
@router.post(
    "/auth/signup", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 로그인 아이디 중복 검사
    existing_login_id_user = user_crud.get_user_by_login_id(
        login_id=user.login_id,
        db=db
    )

    if existing_login_id_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 로그인 아이디입니다."
        )
    
    # 이메일 이름 중복 검사
    existing_email_user = user_crud.get_user_by_email(
        email=str(user.email),
        db=db
    )

    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다."
        )
    
    hashed_password = hash_password(plain_password=user.password)

    try:
        created_user = user_crud.create_user(
            user=user,
            hashed_password=hashed_password,
            db=db
        )

        return created_user
    
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 사용자 정보입니다."
        )


# 로그인
@router.post("/auth/login", response_model=TokenResponse)
def login(
    login_form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm의 username 필드에 login_id가 전달됨
    login_id = login_form.username

    login_user = user_crud.get_user_by_login_id(
        login_id=login_id, 
        db=db
    )

    if login_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    password_is_verified = verify_password(
        plain_password=login_form.password,
        hashed_password=login_user.password_hash
    )

    if not password_is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate":"Bearer"}
        )
    
    if not login_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다."
        )
    
    access_token = create_access_token(
        user_id=login_user.user_id
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


# 현재 로그인한 사용자 정보 조회
@router.get("/users/me", response_model=UserResponse)
def read_my_user_info(
    current_user: models.User = Depends(get_authenticated_user)
):
    return current_user


# 회원정보 수정
@router.patch("/users/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: models.User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    update_data = user_update.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 정보를 입력해주세요."
        )
    
    # 이메일이 수정 요청이 포함되면 중복 확인
    if update_data.get("email") is not None:
        existing_user = user_crud.get_user_by_email(
            db=db, 
            email=user_update.email
        )

        if (existing_user is not None and existing_user.user_id != current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용 중인 이메일입니다."
            )
        
    try: 
        return user_crud.update_user(
            db=db,
            db_user=current_user,
            user_update=user_update
        )
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            stauts_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 회원정보입니다."
        )

# 회원 탈퇴
@router.delete("/users/me", response_model=MessageResponse)
def delete_current_user(
    current_user: models.User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    user_crud.delete_user(
        db=db,
        db_user=current_user
    )
    return {
        "message": "회원 탈퇴가 완료되었습니다."
    }

# 로그아웃
@router.post("/auth/logout", response_model=MessageResponse)
def logout(
    current_user: models.User = Depends(get_authenticated_user)
):
    return {
        "message": "로그아웃되었습니다."
    }