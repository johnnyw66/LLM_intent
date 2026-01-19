# test_publish.py
from ollama_client import OllamaClient
from llm_intent_processor import LLMIntentProcessor
from model_capabilities import get_model_capability
from text_preprocessor import preprocess_text_for_model
from normalisation_rules import normalise_object


examples = [
    "Shake your paw",
    "Turn on the living room light and dim it to 50%",
    "Sleep for 10 seconds. Turn NEO lights red. Shake your paw",
    "Turn lamp on for 20 seconds then turn off",
    "Shake your paw and tell me what Ohm's law is"
]


model_name = "gemma3:4b"

llm = OllamaClient(model=model_name)

process = LLMIntentProcessor(llm,
    preprocess_fn=preprocess_text_for_model,
    normalise_fn=normalise_object)

for text in examples:
    print(f"\nUser text: {text}")
    processed_intent = process.handle_text(text)
    print(f"Intent {processed_intent}")	


