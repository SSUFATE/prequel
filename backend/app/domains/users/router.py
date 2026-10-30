### 회원가입, 로그인, 로그아웃 API
### 회원 조회, 회원정보 수정, 회원 탈퇴 API
### 프로필 이미지 업로드, 수정, 삭제 API

import uuid
import warnings

from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.domains.users.crud as user_crud

from app.domains.users.model import User
from app.domains.users.dependencies import get_authenticated_user

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.database import get_db

from app.domains.users.schema import (
    MessageResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserDeleteRequest,
)


router = APIRouter(
    tags=["Users"]
)


# =========================
# 회원가입
# =========================

@router.post(
    "/auth/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
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

    # 이메일 중복 검사
    existing_email_user = user_crud.get_user_by_email(
        email=str(user.email),
        db=db
    )

    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다."
        )

    hashed_password = hash_password(
        plain_password=user.password
    )

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


# =========================
# 로그인
# =========================

@router.post(
    "/auth/login",
    response_model=TokenResponse
)
def login(
    login_form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm의 username 필드에 login_id 전달
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
            headers={"WWW-Authenticate": "Bearer"}
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


# =========================
# 현재 로그인한 사용자 정보 조회
# =========================

@router.get(
    "/users/me",
    response_model=UserResponse
)
def read_my_user_info(
    current_user: User = Depends(get_authenticated_user)
):
    return current_user


# =========================
# 회원정보 수정
# =========================

@router.patch(
    "/users/me",
    response_model=UserResponse
)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_authenticated_user),
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

    # 이메일 중복 확인
    if update_data.get("email") is not None:
        existing_user = user_crud.get_user_by_email(
            db=db,
            email=str(user_update.email)
        )

        if (
            existing_user is not None
            and existing_user.user_id != current_user.user_id
        ):
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
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 회원정보입니다."
        )


# =========================
# 회원 탈퇴
# =========================

@router.delete(
    "/users/me",
    response_model=MessageResponse
)
def delete_current_user(
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    old_image_url = current_user.profile_image_url

    user_crud.delete_user(
        db=db,
        db_user=current_user
    )

    # DB 삭제 성공 후 프로필 이미지 파일 삭제
    remove_local_profile_image(old_image_url)

    return {
        "message": "회원 탈퇴가 완료되었습니다."
    }


# =========================
# 로그아웃
# =========================

@router.post(
    "/auth/logout",
    response_model=MessageResponse
)
def logout(
    current_user: User = Depends(get_authenticated_user)
):
    return {
        "message": "로그아웃되었습니다."
    }


# =========================
# Profile Image 설정
# =========================

PROFILE_IMAGE_DIR = Path("uploads/profiles")

PROFILE_IMAGE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# 업로드 파일 최대 크기: 5MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024

# 이미지 최대 가로·세로 길이
MAX_IMAGE_DIMENSION = 4096

# 이미지 최대 픽셀 수
MAX_IMAGE_PIXELS = 4096 * 4096

# Pillow 압축 폭탄 감지 기준
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

# 허용 이미지 형식
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}

# 파일 시그니처 검사
IMAGE_SIGNATURES = {
    "JPEG": lambda data: data.startswith(b"\xff\xd8\xff"),

    "PNG": lambda data: data.startswith(
        b"\x89PNG\r\n\x1a\n"
    ),

    "WEBP": lambda data: (
        len(data) >= 12
        and data.startswith(b"RIFF")
        and data[8:12] == b"WEBP"
    ),
}


# =========================
# 이미지 검증 및 재인코딩
# =========================

def validate_and_process_image(
    content: bytes,
    expected_format: str
) -> bytes:

    try:
        # Pillow 경고도 오류로 처리
        with warnings.catch_warnings():
            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning
            )

            # 1. 실제 이미지 파일인지 확인
            with Image.open(BytesIO(content)) as image:

                if image.format != expected_format:
                    raise HTTPException(
                        status_code=400,
                        detail="파일 형식과 실제 이미지 형식이 일치하지 않습니다."
                    )

                # 2. 이미지 크기 검사
                width, height = image.size

                if (
                    width > MAX_IMAGE_DIMENSION
                    or height > MAX_IMAGE_DIMENSION
                    or width * height > MAX_IMAGE_PIXELS
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="이미지 크기는 가로·세로 4096px 이하만 가능합니다."
                    )

                # 3. 이미지 구조 검증
                image.verify()

            # 4. 실제 이미지 디코딩
            with Image.open(BytesIO(content)) as image:

                image.load()

                # 5. 이미지 RGB 변환
                # 원본 메타데이터를 복사하지 않음
                processed_image = Image.new(
                    "RGB",
                    image.size,
                    (255, 255, 255)
                )

                # PNG/WEBP 투명 배경 처리
                if image.mode in ("RGBA", "LA") or (
                    "transparency" in image.info
                ):
                    rgba_image = image.convert("RGBA")

                    processed_image.paste(
                        rgba_image,
                        mask=rgba_image.getchannel("A")
                    )

                else:
                    processed_image.paste(
                        image.convert("RGB")
                    )

                # 6. WEBP로 재인코딩
                output = BytesIO()

                processed_image.save(
                    output,
                    format="WEBP",
                    quality=85,
                    method=4
                )

                return output.getvalue()

    except HTTPException:
        raise

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        SyntaxError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ):
        raise HTTPException(
            status_code=400,
            detail="올바르지 않거나 손상된 이미지 파일입니다."
        )


# =========================
# 기존 프로필 이미지 파일 삭제
# =========================

def remove_local_profile_image(
    image_url: str | None
):
    if not image_url:
        return

    prefix = "/uploads/profiles/"

    if not image_url.startswith(prefix):
        return

    filename = image_url.removeprefix(prefix)

    # 다른 경로의 파일 삭제 방지
    if Path(filename).name != filename:
        return

    # 허용된 파일명 패턴만 삭제
    import re

    if not re.fullmatch(
        r"\d+_[0-9a-f]{32}\.(jpg|png|webp)",
        filename
    ):
        return

    file_path = PROFILE_IMAGE_DIR / filename

    file_path.unlink(missing_ok=True)


# =========================
# 프로필 이미지 업로드 및 수정
# =========================

@router.post(
    "/users/me/profile-image",
    response_model=UserResponse
)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    try:
        # 1. MIME 타입 검사
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="JPG, PNG, WEBP 이미지만 업로드할 수 있습니다."
            )

        expected_format = ALLOWED_IMAGE_TYPES[
            file.content_type
        ]

        # 2. 파일 크기 제한
        content = await file.read(
            MAX_IMAGE_SIZE + 1
        )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="빈 파일은 업로드할 수 없습니다."
            )

        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="이미지는 5MB 이하만 업로드할 수 있습니다."
            )

        # 3. 파일 시그니처 검사
        if not IMAGE_SIGNATURES[expected_format](content):
            raise HTTPException(
                status_code=400,
                detail="올바른 이미지 파일이 아닙니다."
            )

        # 4. 실제 이미지 디코딩 및 보안 검증
        processed_image = validate_and_process_image(
            content=content,
            expected_format=expected_format
        )

        # 5. UUID 파일명 생성
        filename = (
            f"{current_user.user_id}_"
            f"{uuid.uuid4().hex}.webp"
        )

        file_path = PROFILE_IMAGE_DIR / filename

        # 6. WEBP 이미지 저장
        file_path.write_bytes(processed_image)

        image_url = f"/uploads/profiles/{filename}"

        old_image_url = current_user.profile_image_url

        # 7. DB에 이미지 URL 저장
        try:
            updated_user = user_crud.update_profile_image(
                db=db,
                db_user=current_user,
                image_url=image_url
            )

        except Exception:
            # DB 저장 실패 시 새 이미지 삭제
            file_path.unlink(missing_ok=True)
            raise

        # 8. 기존 이미지 삭제
        remove_local_profile_image(old_image_url)

        return updated_user

    finally:
        await file.close()


# =========================
# 프로필 이미지 삭제
# =========================

@router.delete(
    "/users/me/profile-image",
    response_model=UserResponse
)
def remove_profile_image(
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    old_image_url = current_user.profile_image_url

    # DB에서 이미지 URL 제거
    updated_user = user_crud.delete_profile_image(
        db=db,
        db_user=current_user
    )

    # 실제 이미지 파일 삭제
    remove_local_profile_image(old_image_url)

    return updated_user


# 회원탈퇴 시 비밀번호 확인
@router.delete("/users/me", response_model=MessageResponse)
def delete_current_user(
    request: UserDeleteRequest,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    # 비밀번호 확인
    if not verify_password(
        plain_password=request.password,
        hashed_password=current_user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="비밀번호가 일치하지 않습니다."
        )

    # 프로필 이미지 경로 저장
    old_image_url = current_user.profile_image_url

    # 회원 삭제
    user_crud.delete_user(
        db=db,
        db_user=current_user
    )

    remove_local_profile_image(old_image_url)

    return {
        "message": "회원 탈퇴가 완료되었습니다."
    }