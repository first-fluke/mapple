import datetime

from sqlalchemy import String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.lib.database import Base


class UserAuth(Base):
    __tablename__ = "user_auth"
    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="uq_user_auth_provider"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(20))
    provider_id: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
