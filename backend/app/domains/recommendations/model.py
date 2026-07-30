from datetime import datetime

from sqlalchemy import (
    DateTime, 
    Float, 
    ForeignKey, 
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# if TYPE_CHECKING:
#     from app.domains.users.model import User
#     from app.domains.kcontents.model import KContent
#     from app.domains.literatures.model import LiteraryWork


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    content_id: Mapped[int] = mapped_column(
        ForeignKey(
            "kcontents.content_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    work_id: Mapped[int] = mapped_column(
        ForeignKey(
            "literatures.work_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    similarity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # # 관계 연결
    # user: Mapped["User"] = relationship(
    #     back_populates="recommendations"
    # )
    # kcontent: Mapped["KContent"] = relationship(
    #     back_populates="recommendations",
    # )

    # literary_work: Mapped["LiteraryWork"] = relationship(
    #     back_populates="recommendations",
    # )