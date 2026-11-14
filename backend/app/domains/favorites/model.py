from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.domains.users.model import User
    from app.domains.literatures.model import LiteraryWork


class Favorite(Base):
    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "work_id",
            name="uq_favorites_user_work",
        ),
    )

    favorite_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        )
    )

    work_id: Mapped[int] = mapped_column(
        ForeignKey(
            "literatures.work_id",
            ondelete="CASCADE",
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # 관계 연결
    user: Mapped["User"] = relationship(
        back_populates="favorites"
    )

    literary_work: Mapped["LiteraryWork"] = relationship(
        back_populates="favorites",
    )