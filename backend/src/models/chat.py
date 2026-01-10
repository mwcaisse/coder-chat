import uuid
from datetime import datetime

from pydantic import BaseModel


class ChatRequestModel(BaseModel):
    message: str


class ChatMessageResponseModel(BaseModel):
    from_user: bool
    content: str
    summary: str | None = None


class CreateChatRequestModel(BaseModel):
    name: str
    language: str | None


class CreateChatWithMessageRequestModel(BaseModel):
    message: str
    name: str | None = None
    language: str | None = None


class ChatResponseModel(BaseModel):
    id: uuid.UUID
    name: str
    language: str | None
    messages: list[ChatMessageResponseModel]
    # TODO: Add create_date to this


class SimpleChatResponseModel(BaseModel):
    id: uuid.UUID
    name: str
    language: str | None
    create_date: datetime
