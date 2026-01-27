import json
import requests

# -----------------------------
# Configuration
# -----------------------------

OLLAMA_URL = "http://aiplus2:8000/api/chat"
#DEFAULT_LLM_MODEL = "llama3.2:3b"  # change if needed
DEFAULT_LLM_MODEL = "qwen2:1.5b"

LLM_SYSTEM_PROMPT = """
You are a robot control interpreter.
You must respond ONLY with valid JSON.
Do not include any commentary or explanation.
"""



LLM_SYSTEM_PROMPT = """
You are an intent router.

Convert spoken user commands into a single JSON object.

Rules:
- Output ONLY valid JSON
- Do NOT include explanations, comments, or markdown
- Do NOT include any text outside the JSON
- Use lowercase strings unless required
- If the intent is unclear, return {"actions": []}

Schema:
{
  "actions": [
    {
      "type": string,
      "...": "additional fields as required"
    }
  ]
}

Allowed action types:
- neo_light   (fields: color)
- bark
- sit
- stand
- walk
- sleep
- roll
- lie
- wag
- wag_tail
- shake_paw

Examples:

User: set the neo lights to red and bark
Output:
{"actions":[{"type":"neo_light","color":"red"},{"type":"bark"}]}

User: bark
Output:
{"actions":[{"type":"bark"}]}

"""
# -----------------------------
# Helpers
# -----------------------------

def safe_json_load(text: str) -> dict:
    """
    Attempts to parse JSON from LLM output.
    Raises ValueError if parsing fails.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON:\n{text}") from e


def call_llm_http(text: str, send_system_prompt: bool = True) -> dict:

    messages = [{"role": "user", "content": text}]
    if send_system_prompt:
        messages.insert(0, {"role": "system", "content": LLM_SYSTEM_PROMPT})
    #print(messages)
    payload = {
        "model": DEFAULT_LLM_MODEL,
        "messages": messages,
        "options": {
            "temperature": 0,
            "num_predict": 300,
        },
        "format": "json",
        "stream": False,
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=360,
    )
    response.raise_for_status()
    #print(response, response.content)

    data = response.json()
    return safe_json_load(data["message"]["content"])


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":

    examples = [
       "set the neo lights to blue, wag your tail  and bark",
       "set neo to blue, wait for 10 seconds and bark",
       "lie down for 20 seconds. sit up for 3 seconds. walk for 10 seconds and then sit.  bark, shake a paw and wag your tail"
    ]
    for user_sentence in examples:
     result = call_llm_http(user_sentence)
     print(f"LLM structured output for '{user_sentence}':")
     print(json.dumps(result, indent=2))


