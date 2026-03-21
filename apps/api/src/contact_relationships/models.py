import datetime

from sqlalchemy import CheckConstraint, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.lib.database import Base


class ContactRelationship(Base):
    __tablename__ = "contact_relationship"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "contact_id_1",
            "contact_id_2",
            name="uq_contact_relationship_pair",
        ),
        CheckConstraint("contact_id_1 < contact_id_2", name="ck_contact_relationship_ordered"),
        CheckConstraint("strength > 0", name="ck_contact_relationship_positive_strength"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_auth.id", ondelete="CASCADE"))
    contact_id_1: Mapped[int] = mapped_column(ForeignKey("contact.id", ondelete="CASCADE"))
    contact_id_2: Mapped[int] = mapped_column(ForeignKey("contact.id", ondelete="CASCADE"))
    strength: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
