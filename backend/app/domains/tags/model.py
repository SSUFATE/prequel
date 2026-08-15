from datetime import datetime
from typing import TYPE_CHECKING

from app.database import Base
from sqlalchemy import DateTime, ForeignKey, Text, SmallInteger, String, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from app.domains.kcontents.model import KContent
    from app.domains.literatures.model import LiteraryWork

class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(50)
    )

    description: Mapped[str] = mapped_column(
        Text
    )

    selection_guide: Mapped[str] = mapped_column(
        Text
    )

    __table_args__ = (
        UniqueConstraint(
            "category",
            "name",
            name="uq_tags_category_name"
        ),
    )

    # 관계 연결
    kcontent_tags: Mapped[list["KContentTag"]] = relationship(
        back_populates="tag", 
        cascade="all, delete-orphan"
    )

    literature_tags: Mapped[list["LiteraryWorkTag"]] = relationship(
        back_populates="tag", 
        cascade="all, delete-orphan"
    )


class KContentTag(Base):
    __tablename__ = "kcontent_tags"

    __table_args__ = (
        UniqueConstraint(
            "content_id",
            "tag_id",
            name="uq_kcontent_tags_content_tag",
        ),
    )

    content_tag_id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True
    )

    content_id: Mapped[int] = mapped_column(
        ForeignKey(
            "kcontents.content_id", 
            ondelete="CASCADE"
        )
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tags.tag_id", 
            ondelete="CASCADE"
        )
    )

    weight: Mapped[int] = mapped_column(
        SmallInteger, 
        default=1
    )

    created_by: Mapped[str | None] = mapped_column(
        String(100)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=func.now(),
    )

    #@ManyToOne
    kcontent: Mapped["KContent"] = relationship(
        back_populates="tags"
    )

    tag: Mapped["Tag"] = relationship(
        back_populates="kcontent_tags"
    )


class LiteraryWorkTag(Base):
    __tablename__ = "literature_tags"

    __table_args__ = (
        UniqueConstraint(
            "work_id",
            "tag_id",
            name="uq_literature_tags_work_tag",
        ),
    )

    work_tag_id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True
    )

    work_id: Mapped[int] = mapped_column(
        ForeignKey(
            "literatures.work_id", 
            ondelete="CASCADE"
        )
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tags.tag_id", 
            ondelete="CASCADE"
        )
    )

    weight: Mapped[int] = mapped_column(
        SmallInteger, 
        default=1
    )

    created_by: Mapped[str | None] = mapped_column(
        String(100)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=func.now())

    #@ManyToOne 
    literary_work: Mapped["LiteraryWork"] = relationship(
        back_populates="tags"
    )

    tag: Mapped["Tag"] = relationship(
        back_populates="literature_tags"
    )