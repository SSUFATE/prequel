from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.domains.kcontents.router import router as kcontent_router
from app.domains.recommendations.router import router as recommendation_router
from app.domains.users.router import router as user_router

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

# User 라우터 등록
app.include_router(user_router, prefix="/api/v1")

# KContent 라우터 등록
app.include_router(kcontent_router, prefix="/api/v1")

# Recommendation 라우터 등록
app.include_router(recommendation_router, prefix="/api/v1")
