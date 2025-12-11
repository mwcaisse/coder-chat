from pydantic import BaseModel


class ChatRequestModel(BaseModel):
    message: str
