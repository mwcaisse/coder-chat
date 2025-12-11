from fastapi import APIRouter

from src.models.chat import ChatResponseModel, ChatRequestModel

router = APIRouter()


@router.post("/chat/",
             response_model=ChatResponseModel)
def send_message(model: ChatRequestModel):
    return ChatResponseModel(message=model.message)
