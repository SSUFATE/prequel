import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()

DATABASE_url = os.getenv("POSTGRESQL_URL")

if not DATABASE_url:
    raise RuntimeError(
        "POSTGRESQL_URL이 .env에 설정되어 있지 않습니다."
    )

engine = create_engine(DATABASE_url, echo=True)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()