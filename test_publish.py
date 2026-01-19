# test_publish.py
from ollama_client import OllamaClient
from stdout_publisher import StdoutPublisher
from llm_intent_publisher import LLMIntentPublisher
from model_capabilities import get_model_capability
from text_preprocessor import preprocess_text_for_model

examples = [
    "Shake your paw",
    "Turn on the living room light and dim it to 50%",
    "Sleep for 10 seconds. Turn NEO lights red. Shake your paw",
    "Turn lamp on for 20 seconds then turn off",
    "Shake your paw and tell me what Ohm's law is"
]


model_name = "gemma3:4b"

llm = OllamaClient(model=model_name)

publisher = StdoutPublisher()
router = LLMIntentPublisher(llm, publisher)

for text in examples:
    print(f"\nUser text: {text}")

    clean_text = preprocess_text_for_model(text, model_name)
    print(f"cleaned text: {clean_text}")
    router.handle_text(clean_text)


