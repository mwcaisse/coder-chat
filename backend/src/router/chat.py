from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.models.chat import ChatRequestModel
from src.services.chat import process_message

router = APIRouter()


@router.post("/chat/")
def send_message(model: ChatRequestModel):
    response_generator = process_message(model.message)
    return StreamingResponse(response_generator)
