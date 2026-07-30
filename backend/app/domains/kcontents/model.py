from datetime import datetime, date
from typing import TYPE_CHECKING

from app.database import Base
from sqlalchemy import (
    Date,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from app.domains.tags.model import KContentTag


class KContent(Base):
    __tablename__ = "kcontents"

    __table_args__ = (
        UniqueConstraint(
            "tmdb_id",
            "content_type",
            name="uq_kcontents_tmdb_id_content_type",
        ),
    )

    content_id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    tmdb_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    overview: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tmdb_genres: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    runtime: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    platform: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    release_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    poster_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="TMDB",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 관계 연결
    tags: Mapped[list["KContentTag"]] = relationship(
        back_populates="kcontent",
        cascade="all, delete-orphan",
    )

    # recommendations: Mapped[list["Recommendation"]] = relationship(
    #     back_populates="kcontent",
    #     cascade="all, delete-orphan",
    # )