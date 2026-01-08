import datetime
import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.data_models.base import (
    CoderChatBaseModel,
    generate_current_date,
)


class User(CoderChatBaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(1024), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    locked: Mapped[bool] = mapped_column(nullable=False)
    last_login: Mapped[datetime.datetime] = mapped_column(nullable=True)
    create_date: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=generate_current_date
    )


class UserRefreshToken(CoderChatBaseModel):
    __tablename__ = "user_refresh_token"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "token_prefix", name="uc_user_refresh_token_user_id_token_prefix"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    token_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    token_hash = mapped_column(String(1024), nullable=False)

    create_date: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=generate_current_date
    )
    expire_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
