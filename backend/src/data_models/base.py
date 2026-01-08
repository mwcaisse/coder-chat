import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid() -> UUID:
    return uuid.uuid4()


def generate_current_date() -> datetime:
    return datetime.now(tz=timezone.utc)


class CoderChatBaseModel(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
