from datetime import datetime
from typing import TYPE_CHECKING, Optional

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
    from app.domains.recommendations.model import Recommendation
    from app.domains.tag.model import KContentTag


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
        Integer,
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

    release_date: Mapped[Date | None] = mapped_column(
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

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 연관 관계
    # tags: Mapped[list["KContentTag"]] = relationship(
    #     back_populates="kcontent",
    #     cascade="all, delete-orphan",
    # )

    # recommendations: Mapped[list["Recommendation"]] = relationship(
    #     back_populates="kcontent",
    #     cascade="all, delete-orphan",
    # )