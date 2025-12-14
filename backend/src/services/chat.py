import uuid
from dataclasses import dataclass
from typing import Generator, NamedTuple

from threading import Thread
from uuid import UUID

from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL_NAME = "Qwen/Qwen3-1.7B"


class ChatMessage(NamedTuple):
    from_user: bool
    content: str


@dataclass
class Chat:
    id: UUID
    messages: list[ChatMessage]


CHATS: dict[UUID, Chat] = dict()


def get_chat(chat_id: UUID) -> Chat | None:
    return CHATS.get(chat_id)


def create_chat() -> Chat:
    chat_id = uuid.uuid4()
    chat = Chat(
        id=chat_id,
        messages=[]
    )

    CHATS[chat_id] = chat

    return chat


def stream_message_results(chat_id: UUID, results_stream):
    message = ""

    for text_token in results_stream:
        message += text_token
        yield text_token

    CHATS[chat_id].messages.append(ChatMessage(
        from_user=False,
        content=message
    ))


def send_message_to_chat(chat_id: UUID, message: str):
    if chat_id not in CHATS:
        raise ValueError(f"No chat with id {chat_id} exists")

    chat = CHATS[chat_id]
    chat.messages.append(ChatMessage(
        from_user=True,
        content=message
    ))

    results_stream = process_message(message)

    return stream_message_results(chat_id, results_stream)


def process_message(message: str) -> Generator[str, None, None]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype="auto", device_map="auto"
    )

    prompt = """
    LANGUAGE: python
    RELEVANT LIBRARIES: FastAPI  
    """.strip()
    prompt += message

    messages = [{"role": "user", "content": prompt}]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    print(f"Using device {model.device}")

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generation_args = {"max_new_tokens": 32768, "streamer": streamer, **model_inputs}

    thread = Thread(
        target=model.generate,
        kwargs=generation_args,
    )
    thread.start()

    return streamer
