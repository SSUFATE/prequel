from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from backend.app.models.additional_info import Translation, VisualAid
from backend.app.models.recommendation import Favorite, Recommendation
from backend.app.models.tag import KContentTag, LiteraryWorkTag

class KContent(Base):
    __tablename__ = "KContent"

    kcontent_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kcontent_type: Mapped[Optional[str]] = mapped_column(String(20))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    platform: Mapped[Optional[str]] = mapped_column(String(100))
    release_year: Mapped[Optional[int]] = mapped_column(Integer)
    director: Mapped[Optional[str]] = mapped_column(String(100))
    writer: Mapped[Optional[str]] = mapped_column(String(100))
    poster_url: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 연관 관계
    tags: Mapped[list["KContentTag"]] = relationship(back_populates="kcontent", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="kcontent", cascade="all, delete-orphan")


class LiteraryWork(Base):
    __tablename__ = "LiteraryWork"

    work_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    literature_type: Mapped[Optional[str]] = mapped_column(String(20))
    author: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    era: Mapped[Optional[str]] = mapped_column(String(50))
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    cover_url: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


    # 일대일 매핑
    tags: Mapped[list["LiteraryWorkTag"]] = relationship(back_populates="literary_work", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="literary_work", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="literary_work", cascade="all, delete-orphan")
    
    # 1:M 매핑
    translations: Mapped[list["Translation"]] = relationship(back_populates="literary_work", cascade="all, delete-orphan")
    visual_aids: Mapped[list["VisualAid"]] = relationship(back_populates="literary_work", cascade="all, delete-orphan")