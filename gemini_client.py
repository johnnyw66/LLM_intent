import json
import requests
from llm_client import LLMClient
from google import genai


class GeminiClient(LLMClient):
    def __init__(self, system_prompt, model="gemini-2.5-flash", api_key="???"):

        print(model, api_key)
        self.model = model
        self.api_key = api_key
        self.system_prompt = system_prompt

    def parse_intents(self, user_text: str) -> dict:

        genai_client = genai.Client(api_key=self.api_key)
        chat = genai_client.chats.create(model=self.model)

        response = chat.send_message(self.system_prompt + "\n" + user_text)

        raw = response.candidates[0].content.parts[0].text

        # Remove code fences
        clean = raw.strip()
        clean = clean.removeprefix("```json")
        clean = clean.removesuffix("```")
        clean = clean.strip()

        data = json.loads(clean)

        return data #safe_json_load(clean_text)


if __name__ == "__main__":
    import os
    from BANANA_PROMPT import SYSTEM_PROMPT

    # Configure API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Set your GOOGLE_API_KEY environment variable first!")

    client = GeminiClient(SYSTEM_PROMPT, api_key = api_key)

    response = client.parse_intents("I like toy ducks, bananas, oranges and the sun. On Wednesdays I eat sweetcorn.")
    print("RESPONSE ", response)