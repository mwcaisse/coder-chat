import uuid

from pydantic import BaseModel


class ChatRequestModel(BaseModel):
    message: str


class ChatMessage(BaseModel):
    from_user: bool
    content: str


class ChatResponseModel(BaseModel):
    id: uuid.UUID
    messages: list[ChatMessage]
