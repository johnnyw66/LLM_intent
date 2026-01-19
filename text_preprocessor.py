from model_capabilities import get_model_capability

def preprocess_text_for_model(text: str, model_name: str) -> str:
    cap = get_model_capability(model_name)

    # Strip problematic nested quotes if unsupported
    if not cap.get("supports_nested_quotes", True):
        text = text.replace("'", "")

    # Optionally split into multiple sentences for simple models
    if not cap.get("supports_complex_json", True):
        # naive split by period
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        text = '. '.join(sentences[:2])  # take only first 2 sentences

    # Truncate if longer than max input length
    max_len = cap.get("max_input_length")
    if max_len and len(text) > max_len:
        text = text[:max_len]

    return text


