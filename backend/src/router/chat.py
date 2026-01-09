from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from src.database import DatabaseSessionDepend
from src.models.chat import (
    ChatRequestModel,
    CreateChatRequestModel,
    CreateChatWithMessageRequestModel,
    ChatResponseModel,
)
from src.services.chat import (
    send_message_to_chat,
    create_chat,
    get_chat,
    create_chat_with_message,
    get_chats_for_user,
)
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


@router.get("/chat/")
def fetch_all_chats_r(db: DatabaseSessionDepend, user=Depends(verify_auth_token)):
    return get_chats_for_user(user, db)


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


def chat_with_message_streaming_response(chat: ChatResponseModel, chat_response):
    yield chat.model_dump_json()
    yield "\n"
    yield from chat_response


@router.post("/chat/message")
def create_chat_with_message_r(
    model: CreateChatWithMessageRequestModel,
    db: DatabaseSessionDepend,
    user=Depends(verify_auth_token),
):
    """
    Creates a chat and sends the given message at the same time.
    If no name for the chat is provided it uses the first 50 characters from the message as the chat name

    Streams the JSON representation of the chat model back as well as the response to the chat message.
        The first line will be the chat model in JSON
        The following lines will be the response to the chat message

    :param model:
    :param db:
    :param user:
    :return:
    """
    return StreamingResponse(create_chat_with_message(model, user, db))
