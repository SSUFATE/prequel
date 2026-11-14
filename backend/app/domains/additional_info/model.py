from datetime import datetime
from typing import TYPE_CHECKING

from app.database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.domains.literatures.model import LiteraryWork


# 서비스에서 실제 사용할 번역본 데이터
class Translation(Base):
    __tablename__ = "translations"

    translation_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    work_id: Mapped[int] = mapped_column(
        ForeignKey(
            "literatures.work_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # LTI 번역서지 식별자
    lti_nid: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    # 번역본 기본 정보
    translated_title: Mapped[str | None] = mapped_column(
        Text
    )

    # 해외 표기 작가명
    author: Mapped[str | None] = mapped_column(
        Text
    )

    language: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    country: Mapped[str | None] = mapped_column(
        String(100)
    )

    translator: Mapped[str | None] = mapped_column(
        Text
    )

    publisher: Mapped[str | None] = mapped_column(
        Text
    )

    isbn: Mapped[str | None] = mapped_column(
        String(50)
    )

    published_year: Mapped[int | None] = mapped_column(
        Integer
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    cover_url: Mapped[str | None] = mapped_column(
        Text
    )

    # LTI 상세 페이지
    source_url: Mapped[str | None] = mapped_column(
        Text
    )

    # Google Books 보조 정보
    google_books_id: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
    )

    preview_url: Mapped[str | None] = mapped_column(
        Text
    )

    purchase_url: Mapped[str | None] = mapped_column(
        Text
    )

    # 관계 연결
    literary_work: Mapped["LiteraryWork"] = relationship(
        back_populates="translations"
    )

class VisualAid(Base):
    __tablename__ = "visual_aids"

    visual_aid_id: Mapped[int] = mapped_column(
        primary_key=True, 
    )

    work_id: Mapped[int] = mapped_column(
        ForeignKey(
            "literatures.work_id", 
            ondelete="CASCADE"
        )
    )
    
    three_line_summary: Mapped[str | None] = mapped_column(
        Text
    )
    
    taste_preview: Mapped[str | None] = mapped_column(
        Text
    )
    
    timeline: Mapped[str | None] = mapped_column(
        Text
    )
    
    relationship_diagram: Mapped[str | None] = mapped_column(
        Text
    )
    
    key_sentence: Mapped[str | None] = mapped_column(
        Text
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    # 관계 연결
    literary_work: Mapped["LiteraryWork"] = relationship(
        back_populates="visual_aids"
    )


# LTI API에서 받은 원본 데이터 보관
class LtiBibliographyCache(Base):
    __tablename__ = "lti_bibliography_cache"

    nid: Mapped[str] = mapped_column(
        String(50), 
        primary_key=True
    )

    # 번역본 제목
    title: Mapped[str | None] = mapped_column(Text)
    # 한국어 원작 제목
    original_title: Mapped[str | None] = mapped_column(Text)

    # 한국어 작가명  
    author_kor: Mapped[str | None] = mapped_column(Text)
    # 해외 표기 작가명
    author: Mapped[str | None] = mapped_column(Text)

    language: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))

    translator: Mapped[str | None] = mapped_column(Text)
    publisher: Mapped[str | None] = mapped_column(Text)

    isbn: Mapped[str | None] = mapped_column(String(50))
    published_year: Mapped[str | None] = mapped_column(String(50))

    description: Mapped[str | None] = mapped_column(Text)

    image: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)