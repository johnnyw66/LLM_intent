import ollama
import json

DEFAULT_LLM_MODEL = "gemma3:4b"

# -----------------------------
# SYSTEM_PROMPT
# -----------------------------
LLM_SYSTEM_PROMPT = """
You are an intent classifier.

Return ONLY valid JSON.
No explanations. No commentary.

Output format:
{
  "intents": []
}

LANGUAGE NORMALIZATION RULES

Some commands use different wording but mean the same thing.

Before interpreting a command, drop the word "to" if it appears
between a device name and a colour or state.


MANDATORY RULES:

1. Every action MUST be its own intent. Do NOT merge multiple actions into a single intent.
2. Split actions at "and" or "then" in the sentence, keeping execution order.
3. Never mix hat and zigbee fields in the same intent.
4. If the user asks a question, always create a separate chat intent. The chat intent must appear after any preceding action intents. Do NOT answer the question.
5. Sleep / wait / pause rules:
   - If it appears **before an action**, it applies **only to the next intent of the same type** (HAT or Zigbee). It does NOT affect other types.
   - If it appears **after an action**, create a separate intent of the same type with `delay`.
   - Timed phrases like "for X seconds/minutes/hours" **after an action** become a `delay` intent **of the same type**, applied **after the action**.
   - Convert minutes → 60 seconds, hours → 3600 seconds.
6. HAT NeoPixel LED rules:
   - If the user mentions colour, brightness, or effect, create a hat intent with action "set_neo".
   - colour is required if mentioned.
   - brightness optional (default 100).
   - effect optional (default "none").
   - Any explicit duration like "for 10 seconds" becomes a **post-action sleep** intent of type hat.
7. Zigbee rules:
   - Pre-action sleep applies only if it immediately precedes a Zigbee intent.
   - IMPORTANT: For timed phrases like "on for X seconds then off" or "do X for Y seconds then do Z", the delay ALWAYS applies to the **next action of the same type**, not the preceding one. This is critical for 1b.
   - Repeat this behavior in multiple examples to help the small model internalize it.
8. Execution order of intents in JSON MUST match the order of actions in the sentence.

Intent types:
- hat
- zigbee
- chat

Fields:
- hat: action, text (for say), delay (for sleep), colour, brightness, effect (for NeoPixel)
- zigbee: device, room, action, dim (integer), colour, delay (optional pre/post-action)
- chat: text

EXAMPLES (repeated for clarity):

User: Shake your paw
JSON: {"intents":[{"type":"hat","action":"shake_paw"}]}

User: Turn Lamp on for 20 seconds then turn off
JSON: {"intents":[
  {"type":"zigbee","device":"lamp","room":"living room","action":"on"},
  {"type":"zigbee","device":"lamp","room":"living room","action":"off","delay":20}
]}

User: Turn Lamp on for 10 seconds then turn off
JSON: {"intents":[
  {"type":"zigbee","device":"lamp","room":"living room","action":"on"},
  {"type":"zigbee","device":"lamp","room":"living room","action":"off","delay":10}
]}

User: Sleep for 10 seconds. Turn NEO lights red. Shake your Paw. Turn Lamp on for 20 seconds then turn off
JSON: {"intents":[
  {"type":"hat","action":"sleep","delay":10},
  {"type":"hat","action":"set_neo","colour":"red"},
  {"type":"hat","action":"shake_paw"},
  {"type":"zigbee","device":"lamp","room":"living room","action":"on"},
  {"type":"zigbee","device":"lamp","room":"living room","action":"off","delay":20}
]}

User: Turn Neo lights blue for 10 seconds then turn to green for 5 seconds
JSON: {"intents":[
  {"type":"hat","action":"set_neo","colour":"blue"},
  {"type":"hat","action":"sleep","delay":10},
  {"type":"hat","action":"set_neo","colour":"green"},
  {"type":"hat","action":"sleep","delay":5}
]}

User: Bark and sleep for 10 seconds
JSON: {"intents":[
  {"type":"hat","action":"bark"},
  {"type":"hat","action":"sleep","delay":10}
]}

User: Sleep for 10 seconds and then bark
JSON: {"intents":[
  {"type":"hat","action":"sleep","delay":10},
  {"type":"hat","action":"bark"}
]}

User: Shake your paw and tell me what Ohm's law is
JSON: {"intents":[
  {"type":"hat","action":"shake_paw"},
  {"type":"chat","text":"Tell me what Ohm's law is"}
]}

User: Turn on the heat and say I have completed your tasks, mistress!
JSON: {"intents":[
  {"type":"zigbee","device":"heat","room":"living room","action":"on"},
  {"type":"hat","action":"say","text":"I have completed your tasks, mistress!"}
]}
"""



def safe_json_load(content: str) -> dict:
    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        json_text = content[start:end]
        return json.loads(json_text)
    except (ValueError, json.JSONDecodeError):
        return {"error": "invalid_json"}

# -----------------------------
# LLM call (supports optional system prompt)
# -----------------------------
def call_llm(text: str, send_system_prompt: bool = True, session: any = None) -> dict:
    """
    Sends user text to Ollama LLM and returns structured JSON.
    If send_system_prompt is True or session is None, SYSTEM_PROMPT is sent each call.
    If a session is provided, it can be reused for multiple calls.
    """
    
    messages = [{"role": "user", "content": text}]
    if send_system_prompt or session is None:
        messages.insert(0, {"role": "system", "content": LLM_SYSTEM_PROMPT})

    if session:
        # session-based call
        response = session.chat(messages=messages, options={"temperature": 0, "num_predict": 300})
    else:
        # stateless call
        response = ollama.chat(
            model= DEFAULT_LLM_MODEL,
            messages=messages,
            options={"temperature": 0, "num_predict": 300}
        )

    return safe_json_load(response["message"]["content"])


# -----------------------------
# Intent function
# -----------------------------
def classify_intent(text: str, send_system_prompt: bool = True, session: any = None):
    result = call_llm(text, send_system_prompt=send_system_prompt, session=session)

    if "error" in result:
        print("LLM error:", result["error"])
        return

    return result


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":

    print("MODEL ", DEFAULT_LLM_MODEL)
    # Optional: create a persistent session if desired
    # session = ollama.create_session(model=DEFAULT_LLM_MODEL, system_prompt=LLM_SYSTEM_PROMPT)
    session = None  # using stateless calls by default

    examples = [
        #"Set your neo lights to blue. Sleep for 10 seconds and then bark",
        #"Shake your paw and sleep for 10 seconds",
        #"Turn on the living room light and dim it to 50% wait for 10 minutes then turn blue",
	    "Shake your paw",
        "Turn lamp blue",
        "Turn lamp to blue",
        "Turn on the heat and say I have completed your tasks, mistress!",
        "Shake your paw, howl and tell me what Ohm's law is",
        "Turn on the living room light, sleep 2 minutes, dim it to 40%, bark, wait 10 seconds, say Hello, then tell me what Ohm's law is, and finally stand up.",
        "Turn Lamp on for 20 seconds then turn off. Finally tell me Ohm's law'",
        "Sleep for 10 seconds. Turn NEO lights red. Shake your Paw and say doing as you wish, mistress! Turn Lamp on for 20 seconds then turn off"

    ]

    for text in examples:
        print(f"\nUser text: {text}")
        print(f"Result:",classify_intent(text, send_system_prompt=True, session=session))


