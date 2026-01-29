import json
import requests
from llm_client import LLMClient
import re

def safe_json_load(content: str) -> dict:
    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        json_text = content[start:end]
        return json.loads(json_text)
    except (ValueError, json.JSONDecodeError):
        return {"error": "invalid_json"}

class OllamaClient(LLMClient):
    def __init__(self, prompt, model="gemma3:1b", host="http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")
        self.prompt = prompt

    def parse_json_safe(self, raw_text: str):
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            # Print raw text for debugging
            print("WARNING: LLM returned invalid JSON:", repr(raw_text))
            return {"intents": []}

    def parse_intents(self, user_text: str) -> dict:
        payload = {
            "model": self.model,
            "prompt": f"{self.prompt}\n\nUser text: {user_text}",
            "stream": False,
            "options": {"temperature": 0}
        }
        r = requests.post(f"{self.host}/api/generate", json=payload, timeout=90)
        r.raise_for_status()

        resp_str = r.content.decode("utf-8")

        resp_json = json.loads(resp_str)
        # Remove 'json' header
        # print(resp_json)
        clean_text = re.sub(r"```json\s*|\s*```", "", resp_json['response']).strip()

        # Load JSON from LLM
        #return safe_json_load(clean_text)

        return json.loads(clean_text)

