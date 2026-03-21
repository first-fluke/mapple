from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.lib.database import Base

contact_tags = Table(
    "contact_tags",
    Base.metadata,
    Column("contact_id", Integer, ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    location = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

    tags: Mapped[list["Tag"]] = relationship(
        secondary=contact_tags, back_populates="contacts"
    )
    meetings: Mapped[list["Meeting"]] = relationship(
        secondary="meeting_contacts", back_populates="contacts"
    )

    __table_args__ = (
        Index("ix_contacts_not_deleted", "user_id", postgresql_where=(deleted_at.is_(None))),
    )


class ContactRelationship(Base):
    __tablename__ = "contact_relationships"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    contact_a_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE")
    )
    contact_b_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE")
    )
    type: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("contact_a_id < contact_b_id", name="ck_contact_relationship_order"),
        UniqueConstraint("user_id", "contact_a_id", "contact_b_id", name="uq_contact_relationship"),
    )
