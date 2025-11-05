from threading import Thread

from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL_NAME = "Qwen/Qwen3-1.7B"


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype="auto", device_map="auto"
    )

    prompt = "How can I create an API endpoint in python with Quart?"
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

    for text_token in streamer:
        print(text_token, end="")

    thread.join()


if __name__ == "__main__":
    main()
