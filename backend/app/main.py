from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models

from app.domains.kcontents.router import router as kcontent_router
from app.domains.recommendations.router import router as recommendation_router
from app.domains.users.router import router as user_router
from app.domains.literatures.router import router as literatures_router
from app.domains.favorites.router import router as favorite_router
from app.domains.additional_info.router import router as translation_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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