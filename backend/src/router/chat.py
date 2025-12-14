from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.models.chat import ChatRequestModel, ChatResponseModel, ChatMessage
from src.services.chat import send_message_to_chat, create_chat, get_chat

router = APIRouter()


@router.get("/chat/{chat_id}/")
def fetch_chat_r(chat_id: UUID):
    chat = get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="No chat with given ID found")

    return ChatResponseModel(
        id=chat.id,
        messages=[ChatMessage(from_user=cm.from_user, content=cm.content, summary=cm.summary) for cm in chat.messages]
    )


@router.post("/chat/")
def create_chat_r():
    chat = create_chat()
    return ChatResponseModel(id=chat.id, messages=[])


@router.post("/chat/{chat_id}/message")
def send_message(chat_id: UUID, model: ChatRequestModel):
    response_generator = send_message_to_chat(chat_id, model.message)
    return StreamingResponse(response_generator)
