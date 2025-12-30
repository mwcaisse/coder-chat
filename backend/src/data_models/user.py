import datetime
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.data_models.base import (
    CoderChatBaseModel,
    generate_uuid,
    generate_current_date,
)


class User(CoderChatBaseModel):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # TODO: Double check the length on this
    password: Mapped[str] = mapped_column(String(1024), nullable=False)
    locked: Mapped[bool] = mapped_column(nullable=False)
    last_login: Mapped[datetime.datetime] = mapped_column(nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=generate_current_date
    )
