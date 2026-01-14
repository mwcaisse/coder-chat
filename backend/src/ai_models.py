from typing import NamedTuple, Any

from transformers import AutoTokenizer, AutoModelForCausalLM

from src.config import CONFIG
from src.logs import get_logger

logger = get_logger(__name__)


class AiModel(NamedTuple):
    tokenizer: AutoTokenizer
    model: Any


AI_MODELS: dict[str, AiModel] = {}


def initialize_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            CONFIG.model_path, local_files_only=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            CONFIG.model_path, dtype="auto", device_map="auto"
        )
        AI_MODELS[CONFIG.model_path] = AiModel(tokenizer, model)
        logger.info(f"Loaded model {CONFIG.model_path} on device: {model.device}")
    except:
        logger.error(f"Failed to load model {CONFIG.model_path}")
        raise
