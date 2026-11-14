import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.middleware.csrf import csrf_protection, ALLOWED_ORIGINS
from app.domains.kcontents.router import router as kcontent_router
from app.domains.recommendations.router import router as recommendation_router
from app.domains.users.router import router as user_router
from app.domains.literatures.router import router as literatures_router
from app.domains.favorites.router import router as favorite_router
from app.domains.additional_info.router import router as translation_router

load_dotenv()

app = FastAPI()

FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000"
    ).split(",")
    if origin.strip()
]

BACKEND_ORIGIN = os.getenv(
    "BACKEND_ORIGIN",
    "http://localhost:8000"
)

ALLOWED_ORIGINS.update(FRONTEND_ORIGINS)
ALLOWED_ORIGINS.add(BACKEND_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

app.middleware("http")(csrf_protection)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(user_router, prefix="/api/v1")
app.include_router(kcontent_router, prefix="/api/v1")
app.include_router(recommendation_router, prefix="/api/v1")
app.include_router(literatures_router, prefix="/api/v1")
app.include_router(favorite_router, prefix="/api/v1")
app.include_router(translation_router, prefix="/api/v1")