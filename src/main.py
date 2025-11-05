from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "Qwen/Qwen3-Coder-30B-A3B-Instruct"


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype="auto", device_map="auto"
    )

    prompt = "How can I hash a file in python?"
    messages = [{"role": "user", "content": prompt}]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(**model_inputs, max_new_tokens=65536)
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()

    content = tokenizer.decode(output_ids, skip_special_tokens=True)

    print(content)


if __name__ == "__main__":
    main()
