from model_capabilities import get_model_capability
import re

def preprocess_text_for_model(text: str, model_name: str) -> str:
    cap = get_model_capability(model_name)

    # Remove nested quotes if model can't handle them
    if not cap.get("supports_nested_quotes", True):
        text = text.replace("'", "")

    # Drop "to" in commands like "turn lamp to blue"
    text = re.sub(r'\bto\b', '', text, flags=re.IGNORECASE)

    # Truncate if text is too long for model
    max_len = cap.get("max_input_length")
    if max_len and len(text) > max_len:
        text = text[:max_len]

    return text.strip()

