import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase


class CoderChatBaseModel(DeclarativeBase):
    pass


def generate_uuid() -> UUID:
    return uuid.uuid4()


def generate_current_date() -> datetime:
    return datetime.now(tz=timezone.utc)
