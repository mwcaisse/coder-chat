import uuid
from dataclasses import dataclass
from typing import Generator

from threading import Thread
from uuid import UUID

from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL_NAME = "Qwen/Qwen3-1.7B"


@dataclass
class ChatMessage:
    from_user: bool
    content: str
    summary: str | None = None


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

    chat_message = ChatMessage(
        from_user=False,
        content=message
    )
    CHATS[chat_id].messages.append(chat_message)
    summarize_chat_message(chat_message)


def send_message_to_chat(chat_id: UUID, message: str):
    if chat_id not in CHATS:
        raise ValueError(f"No chat with id {chat_id} exists")

    chat = CHATS[chat_id]

    chat.messages.append(ChatMessage(
        from_user=True,
        content=message
    ))

    previous_messages = [cm.content for cm in chat.messages[:-1]]
    results_stream = process_message(message, previous_messages)

    return stream_message_results(chat_id, results_stream)


def process_message(message: str, previous_messages: list[str]) -> Generator[str, None, None]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype="auto", device_map="auto"
    )

    prompt = """
    LANGUAGE: python      
    """.strip()

    if previous_messages is not None and len(previous_messages) > 0:
        previous_messages_prompt = """
        PREVIOUS MESSAGES (SEPARATED BY ______)
        """.strip()

        previous_messages_prompt += "______".join(previous_messages) + "______"
        prompt += previous_messages_prompt

    prompt += "QUESTION:" + message

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


def summarize_chat_message(message: ChatMessage):
    def thread_fun():
        message.summary = summarize_message(message.content)

    thread = Thread(
        target=thread_fun,
        kwargs={}
    )
    thread.start()


def summarize_message(message: str) -> str:
    # TODO: Deduplicate this with process_message above, but leave here for now
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype="auto", device_map="auto"
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

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    content = tokenizer.decode(output_ids[0:], skip_special_tokens=True).strip("\n")

    print("Summarized message")
    print(content)

    return content
