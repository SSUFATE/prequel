from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from backend.app.models.content import KContent, LiteraryWork

class Favorite(Base):
    __tablename__ = "Favorite"

    favorite_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.user_id", ondelete="CASCADE"))
    work_id: Mapped[int] = mapped_column(ForeignKey("LiteraryWork.work_id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # user: Mapped["user"] = relationship(back_populates="favorites")
    literary_work: Mapped["LiteraryWork"] = relationship(back_populates="favorites")


class Recommendation(Base):
    __tablename__ = "Recommendation"

    recommendation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.user_id", ondelete="CASCADE"))
    kcontent_id: Mapped[int] = mapped_column(ForeignKey("KContent.kcontent_id", ondelete="CASCADE"))
    work_id: Mapped[int] = mapped_column(ForeignKey("LiteraryWork.work_id", ondelete="CASCADE"))
    similarity_score: Mapped[Optional[float]] = mapped_column(Float)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # user: Mapped["user"] = relationship(back_populates="recommendations")
    kcontent: Mapped["KContent"] = relationship(back_populates="recommendations")
    literary_work: Mapped["LiteraryWork"] = relationship(back_populates="recommendations")