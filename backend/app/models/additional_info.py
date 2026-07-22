from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from backend.app.models.content import LiteraryWork

class Translation(Base):
    __tablename__ = "Translation"

    translation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_id: Mapped[int] = mapped_column(ForeignKey("LiteraryWork.work_id", ondelete="CASCADE"))
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    translated_title: Mapped[Optional[str]] = mapped_column(String(255))
    translator: Mapped[Optional[str]] = mapped_column(String(100))
    publisher: Mapped[Optional[str]] = mapped_column(String(100))
    isbn: Mapped[Optional[str]] = mapped_column(String(20))
    purchase_url: Mapped[Optional[str]] = mapped_column(Text)
    cover_url: Mapped[Optional[str]] = mapped_column(Text)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)

    literary_work: Mapped["LiteraryWork"] = relationship(back_populates="translations")


class VisualAid(Base):
    __tablename__ = "VisualAid"

    visual_aid_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_id: Mapped[int] = mapped_column(ForeignKey("LiteraryWork.work_id", ondelete="CASCADE"))
    three_line_summary: Mapped[Optional[str]] = mapped_column(Text)
    taste_preview: Mapped[Optional[str]] = mapped_column(Text)
    timeline: Mapped[Optional[str]] = mapped_column(Text)
    relationship_diagram: Mapped[Optional[str]] = mapped_column(Text)
    key_sentence: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    literary_work: Mapped["LiteraryWork"] = relationship(back_populates="visual_aids")