import datetime
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.data_models.base import CoderChatBaseModel, generate_current_date


class Chat(CoderChatBaseModel):
    __tablename__ = "chat"

    name: Mapped[str] = mapped_column(nullable=False)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=generate_current_date
    )


class ChatMessage(CoderChatBaseModel):
    __tablename__ = "chat_message"

    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat.id"), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    summary: Mapped[str | None] = mapped_column(nullable=True)
    from_user: Mapped[bool]
    create_date: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=generate_current_date
    )
