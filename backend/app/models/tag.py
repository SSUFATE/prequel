from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, SmallInteger, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from backend.app.models.content import KContent, LiteraryWork

class Tag(Base):
    __tablename__ = "Tag"

    tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))

    kcontent_tags: Mapped[list["KContentTag"]] = relationship(back_populates="tag", cascade="all, delete-orphan")
    work_tags: Mapped[list["LiteraryWorkTag"]] = relationship(back_populates="tag", cascade="all, delete-orphan")


class KContentTag(Base):
    __tablename__ = "KContentTag"

    kcontent_tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kcontent_id: Mapped[int] = mapped_column(ForeignKey("KContent.kcontent_id", ondelete="CASCADE"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("Tag.tag_id", ondelete="CASCADE"))
    weight: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    #@ManyToOne
    kcontent: Mapped["KContent"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(back_populates="kcontent_tags")


class LiteraryWorkTag(Base):
    __tablename__ = "LiteraryWorkTag"

    work_tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_id: Mapped[int] = mapped_column(ForeignKey("LiteraryWork.work_id", ondelete="CASCADE"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("Tag.tag_id", ondelete="CASCADE"))
    weight: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    #@ManyToOne 
    literary_work: Mapped["LiteraryWork"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(back_populates="work_tags")