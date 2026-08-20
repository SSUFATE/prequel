from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.domains.additional_info.model import Translation, VisualAid
    from app.domains.favorites.model import Favorite
    from app.domains.tags.model import LiteraryWorkTag


class LiteraryWork(Base):
    __tablename__ = "literatures"

    work_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    source_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(50)
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    literature_type: Mapped[str | None] = mapped_column(
        String(20)
    )

    author: Mapped[str | None] = mapped_column(
        String(100)
    )

    summary: Mapped[str | None] = mapped_column(
        Text
    )

    genre: Mapped[str | None] = mapped_column(
        String(100)
    )

    era: Mapped[str | None] = mapped_column(
        String(50)
    )

    published_year: Mapped[int | None] = mapped_column(
        Integer
    )

    cover_url: Mapped[str | None] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    tags: Mapped[list["LiteraryWorkTag"]] = relationship(
        back_populates="literary_work",
        cascade="all, delete-orphan",
    )

    favorites: Mapped[list["Favorite"]] = relationship(
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