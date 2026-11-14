from fastapi import Request
from fastapi.responses import JSONResponse

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
ALLOWED_ORIGINS = set()  # main.py에서 설정


async def csrf_protection(request: Request, call_next):
    if request.method not in SAFE_METHODS:
        origin = request.headers.get("origin")

        if origin not in ALLOWED_ORIGINS:
            return JSONResponse(
                status_code=403,
                content={"detail": "허용되지 않은 요청 출처입니다."},
            )

    return await call_next(request)