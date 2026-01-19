from ollama_client import OllamaClient
from intent_router import IntentRouter

# Example array of commands
EXAMPLES = [
    "Shake your paw",
    "Turn on the living room light and dim it to 50%",
    "Set the bedroom lamp to blue and stand up",
    "Turn on the heat and say doing as you wish, mistress!",
    "Shake your paw and tell me what Ohm's law is",
    "Sleep for 10 seconds. Turn NEO lights red. Shake your paw and say doing as you wish, mistress! Turn Lamp on for 20 seconds then turn off",
    "Turn lamp to blue",
    "Sit and howl for 5 seconds",
]

# Initialize LLM client and router
llm = OllamaClient(model="gemma3:1b")
router = IntentRouter(llm)

# Parse examples
for example in EXAMPLES:
    result = router.parse(example)
    print("User text:", example)
    print("Result:", result)
    print("-" * 60)

