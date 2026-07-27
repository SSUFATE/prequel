from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.domains.additional_info.model import Translation, VisualAid
    from app.domains.recommendations.model import Recommendation
    from app.domains.favorites.model import Favorite
    from app.domains.tag.model import LiteraryWorkTag


class LiteraryWork(Base):
    __tablename__ = "LiteraryWork"

    work_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    literature_type: Mapped[Optional[str]] = mapped_column(String(20))
    author: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    era: Mapped[Optional[str]] = mapped_column(String(50))
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    cover_url: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # 1:N 관계
    tags: Mapped[list["LiteraryWorkTag"]] = relationship(
        back_populates="literary_work",
        cascade="all, delete-orphan",
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="literary_work",
        cascade="all, delete-orphan",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="literary_work",
        cascade="all, delete-orphan",
    )

    translations: Mapped[list["Translation"]] = relationship(
        back_populates="literary_work",
        cascade="all, delete-orphan",
    )

    visual_aids: Mapped[list["VisualAid"]] = relationship(
        back_populates="literary_work",
        cascade="all, delete-orphan",
    )