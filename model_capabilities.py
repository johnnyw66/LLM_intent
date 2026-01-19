# model_capabilities.py

MODEL_CAPABILITIES = {
    "gemma3:1b": {
        "max_input_length": 1000,
        "supports_chat": True,
        "supports_complex_json": False,
        "preferred_for_intents": True,
        "supports_nested_quotes": False,
    },
    "gemma3:4b": {
        "max_input_length": 4000,
        "supports_chat": True,
        "supports_complex_json": True,
        "preferred_for_intents": True,
        "supports_nested_quotes": True,
    },
    "gemini-alpha": {
        "max_input_length": 8000,
        "supports_chat": True,
        "supports_complex_json": True,
        "preferred_for_intents": True,
        "supports_nested_quotes": True,
    }
}

def get_model_capability(model_name: str) -> dict:
    return MODEL_CAPABILITIES.get(model_name, {})


