from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.domains.literatures.model import LiteraryWork


class Favorite(Base):
    __tablename__ = "Favorite"

    favorite_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "User.user_id",
            ondelete="CASCADE",
        )
    )
    work_id: Mapped[int] = mapped_column(
        ForeignKey(
            "LiteraryWork.work_id",
            ondelete="CASCADE",
        )
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # user: Mapped["user"] = relationship(back_populates="favorites")
    literary_work: Mapped["LiteraryWork"] = relationship(
        back_populates="favorites",
    )