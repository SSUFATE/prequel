from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.domains.recommendations.model import Recommendation
    from app.domains.tag.model import KContentTag


class KContent(Base):
    __tablename__ = "KContent"

    kcontent_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # 연관 관계
    tags: Mapped[list["KContentTag"]] = relationship(
        back_populates="kcontent",
        cascade="all, delete-orphan",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="kcontent",
        cascade="all, delete-orphan",
    )