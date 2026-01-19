# test_publish.py
from ollama_client import OllamaClient
from stdout_publisher import StdoutPublisher
from llm_intent_publisher import LLMIntentPublisher

examples = [
    "Shake your paw",
    "Turn on the living room light and dim it to 50%",
    "Sleep for 10 seconds. Turn NEO lights red. Shake your paw",
    "Turn lamp on for 20 seconds then turn off",
    "Shake your paw and tell me what Ohm's law is"
]

llm = OllamaClient(model="gemma3:4b")
publisher = StdoutPublisher()
router = LLMIntentPublisher(llm, publisher)

for text in examples:
    print(f"\nUser text: {text}")
    router.handle_text(text)


