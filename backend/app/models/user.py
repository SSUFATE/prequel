# SQLAlchemy 모델
# DB 테이블 정의

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer, 
        primary_key=True
    )

    login_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    username = Column(
        String(50),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    language = Column(
        String(10),
        nullable=False,
        default="ko"
    )

    role = Column(
        String(20),
        nullable=False,
        default="USER"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    is_email_verified = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )