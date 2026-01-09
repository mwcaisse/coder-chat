from typing import Generator

from threading import Thread
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

from src.config import CONFIG
from src.data_models.chat import Chat, ChatMessage
from src.exceptions import EntityNotFoundError
from src.models.chat import (
    ChatResponseModel,
    CreateChatRequestModel,
    ChatMessageResponseModel,
    CreateChatWithMessageRequestModel,
    SimpleChatResponseModel,
)
from src.services.user import JwtUser


def _chat_message_to_response_model(
    chat_message: ChatMessage,
) -> ChatMessageResponseModel:
    return ChatMessageResponseModel(
        content=chat_message.content,
        summary=chat_message.summary,
        from_user=chat_message.from_user,
    )


def _chat_to_response_model(chat: Chat, messages: list[ChatMessage]):
    return ChatResponseModel(
        id=chat.id,
        name=chat.name,
        language=chat.language,
        messages=[_chat_message_to_response_model(message) for message in messages],
    )


def _query_raw_chat(
    chat_id: UUID, user: JwtUser, db: Session
) -> tuple[Chat | None, list[ChatMessage]]:
    chat_query = (
        select(Chat)
        .select_from(Chat)
        .where(and_(Chat.user_id == user.id, Chat.id == chat_id))
    )
    chat = db.scalars(chat_query).first()
    if chat is None:
        return None, []

    messages_query = (
        select(ChatMessage)
        .select_from(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.create_date)
    )
    chat_messages = db.scalars(messages_query).all()

    return chat, chat_messages


def get_chat(chat_id: UUID, user: JwtUser, db: Session) -> ChatResponseModel | None:
    chat, chat_messages = _query_raw_chat(chat_id, user, db)

    if chat is None:
        return None

    return _chat_to_response_model(chat, chat_messages)


def get_chats_for_user(
    user: JwtUser, db: Session, limit=25
) -> list[SimpleChatResponseModel]:
    chats_query = (
        select(Chat)
        .select_from(Chat)
        .where(Chat.user_id == user.id)
        .order_by(Chat.create_date.desc())
        .limit(limit)
    )
    chats = db.scalars(chats_query).all()

    return [
        SimpleChatResponseModel(
            id=chat.id,
            name=chat.name,
            language=chat.language,
            create_date=chat.create_date,
        )
        for chat in chats
    ]


def create_chat(
    create_model: CreateChatRequestModel, user: JwtUser, db: Session
) -> ChatResponseModel:
    chat = Chat(name=create_model.name, language=create_model.language, user_id=user.id)
    db.add(chat)
    db.commit()

    return _chat_to_response_model(chat, [])


def create_chat_with_message(
    create_model: CreateChatWithMessageRequestModel, user: JwtUser, db: Session
):
    name = create_model.name if create_model.name else create_model.message[:50]

    chat = Chat(name=name, language=create_model.language, user_id=user.id)
    db.add(chat)
    db.flush()

    message_model = ChatMessage(
        chat_id=chat.id, content=create_model.message, from_user=True
    )
    db.add(message_model)
    db.commit()

    chat_response = _chat_to_response_model(chat, [message_model])
    yield chat_response.model_dump_json()
    yield "\n"

    results_stream = process_message(create_model.message, [])
    yield from stream_message_results(chat.id, results_stream, db)


def stream_message_results(chat_id: UUID, results_stream, db: Session):
    message = ""

    for text_token in results_stream:
        message += text_token
        yield text_token

    chat_message = ChatMessage(chat_id=chat_id, content=message, from_user=False)
    db.add(chat_message)
    db.commit()

    # TODO: re-add in the summary, we aren't using them right now anyway though
    # summarize_chat_message(chat_message)


def send_message_to_chat(chat_id: UUID, message: str, user: JwtUser, db: Session):
    chat, chat_messages = _query_raw_chat(chat_id, user, db)
    if chat is None:
        raise EntityNotFoundError(f"No chat with id {chat_id} exists")

    # the chat exists, we must add our message to the chat now
    message_model = ChatMessage(chat_id=chat_id, content=message, from_user=True)
    db.add(message_model)
    db.commit()

    previous_messages = [m.content for m in chat_messages]
    results_stream = process_message(message, previous_messages)

    return stream_message_results(chat_id, results_stream, db)


def process_message(
    message: str, previous_messages: list[str]
) -> Generator[str, None, None]:
    tokenizer = AutoTokenizer.from_pretrained(CONFIG.model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        CONFIG.model_path, dtype="auto", device_map="auto"
    )

    prompt = """
    LANGUAGE: python      
    """.strip()

    if previous_messages is not None and len(previous_messages) > 0:
        previous_messages_prompt = """
        PREVIOUS MESSAGES (SEPARATED BY ______)
        """.strip()

        previous_messages_prompt += "______\n".join(previous_messages) + "______"
        prompt += previous_messages_prompt

    prompt += "\nQUESTION:" + message

    messages = [{"role": "user", "content": prompt}]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generation_args = {"max_new_tokens": 32768, "streamer": streamer, **model_inputs}

    thread = Thread(
        target=model.generate,
        kwargs=generation_args,
    )
    thread.start()

    return streamer


# TODO: Re-add generating summaries for messages + actually using them
# def summarize_chat_message(message: ChatMessage):
#     def thread_fun():
#         message.summary = summarize_message(message.content)
#
#     thread = Thread(target=thread_fun, kwargs={})
#     thread.start()


def summarize_message(message: str) -> str:
    # TODO: Deduplicate this with process_message above, but leave here for now
    tokenizer = AutoTokenizer.from_pretrained(CONFIG.model_path)
    model = AutoModelForCausalLM.from_pretrained(
        CONFIG.model_path, dtype="auto", device_map="auto"
    )

    prompt = """
        SUMMARIZE THE FOLLOWING MESSAGE:
    """.strip()
    prompt += message

    messages = [{"role": "user", "content": prompt}]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(**model_inputs, max_new_tokens=32768)
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()
    content = tokenizer.decode(output_ids[0:], skip_special_tokens=True).strip("\n")

    return content
