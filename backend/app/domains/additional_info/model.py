from datetime import datetime
from typing import TYPE_CHECKING

from app.database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from app.domains.literatures.model import LiteraryWork
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.domains.literatures.model import LiteraryWork

class Translation(Base):
    __tablename__ = "translations"

    translation_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    work_id: Mapped[int] = mapped_column(
        ForeignKey(
            "literatures.work_id", 
            ondelete="CASCADE"
        )
    )

    language: Mapped[str] = mapped_column(
        String(20), 
        nullable=False
    )

    translated_title: Mapped[str | None] = mapped_column(
        String(255)
    )

    translator: Mapped[str | None] = mapped_column(
        String(100)
    )

    publisher: Mapped[str | None] = mapped_column(
        String(100)
    )

    isbn: Mapped[str | None] = mapped_column(
        String(20)
    )

    purchase_url: Mapped[str | None] = mapped_column(
        Text
    )

    cover_url: Mapped[str | None] = mapped_column(
        Text
    )

    published_year: Mapped[int | None] = mapped_column(
        Integer
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