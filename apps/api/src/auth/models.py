import datetime

from sqlalchemy import Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.lib.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)
    email_verified: Mapped[bool] = mapped_column(
        "emailVerified", Boolean, server_default="false"
    )
    image: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        "createdAt", server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        "updatedAt", server_default=func.now()
    )
