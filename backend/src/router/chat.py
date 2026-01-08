from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from src.database import DatabaseSessionDepend
from src.models.chat import (
    ChatRequestModel,
    CreateChatRequestModel,
)
from src.services.chat import send_message_to_chat, create_chat, get_chat
from src.util.auth import verify_auth_token

router = APIRouter()


@router.get("/chat/{chat_id}/")
def fetch_chat_r(
    chat_id: UUID, db: DatabaseSessionDepend, user=Depends(verify_auth_token)
):
    chat = get_chat(chat_id, user, db)
    if chat is None:
        raise HTTPException(status_code=404, detail="No chat with given ID found")

    return chat


@router.post("/chat/")
def create_chat_r(
    model: CreateChatRequestModel,
    db: DatabaseSessionDepend,
    user=Depends(verify_auth_token),
):
    return create_chat(model, user, db)


@router.post("/chat/{chat_id}/message")
def send_message(
    chat_id: UUID,
    model: ChatRequestModel,
    db: DatabaseSessionDepend,
    user=Depends(verify_auth_token),
):
    response_generator = send_message_to_chat(chat_id, model.message, user, db)
    return StreamingResponse(response_generator)
