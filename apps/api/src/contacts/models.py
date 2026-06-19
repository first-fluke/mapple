import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import DateTime, Float, ForeignKey, PrimaryKeyConstraint, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.lib.database import Base

if TYPE_CHECKING:
    from src.tags.models import Tag


class ContactTag(Base):
    __tablename__ = "contact_tag"
    __table_args__ = (
        PrimaryKeyConstraint("contact_id", "tag_id"),
    )

    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id", ondelete="CASCADE"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"))
    # sa.text() ensures the server_default is emitted as a proper SQL string literal
    # '#6366f1' (7 chars), not the double-quoted Python string "'#6366f1'" (9 chars).
    color: Mapped[str] = mapped_column(String(7), server_default=sa.text("'#6366f1'"))
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class Contact(Base):
    __tablename__ = "contact"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("user.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    country: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    # M2M to Tag via the contact_tag association table.
    # Using ContactTag.__table__ (the Table object) as secondary avoids conflicts
    # between the mapped ContactTag class and the relationship insert path — the
    # ORM then inserts only (contact_id, tag_id) and lets the DB apply the
    # server defaults for color and updated_at.
    # overlaps="contact_id,tag_id" silences the SA2.0 relationship overlap warning.
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=lambda: ContactTag.__table__,
        lazy="selectin",
        overlaps="contact_id,tag_id",
    )
