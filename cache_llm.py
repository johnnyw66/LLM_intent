import re
from time import time
from typing import Dict, List, Optional


class CommandRouter:
    def __init__(self, llm_client=None, cache_ttl: int = 3600):

        self.llm_client = llm_client

        # -------------------------------
        # Cache
        # -------------------------------
        self.template_cache: Dict[str, tuple] = {}
        self.cache_ttl = cache_ttl

        # -------------------------------
        # Action synonyms / phrases
        # -------------------------------
        self.action_synonyms = {
            "woof": "bark",
            "shake the paw": "shake_paw",
            "wag your tail": "wag_tail",
            "wag tail": "wag_tail",
            "spin around": "spin",
            "light": "led",
            "colour": "color",
            "lie down": "lie",
            "scratch your head": "scratch_head",
            "turn around": "turn",
        }

        self.canonical_actions = [
            "sit", "bark", "shake_paw", "wag_tail", "led", "spin",
            "lie", "howl", "scratch", "scratch_head", "walk", "turn", "say",
        ]

        self.timed_actions = {"sit", "walk", "lie", "bark", "howl", "led"}
        self.counted_actions = {"wag_tail", "shake_paw", "spin", "scratch", "scratch_head", "turn"}

    # -------------------------------
    # Cache helpers
    # -------------------------------
    def _cache_lookup(self, key: str):
        entry = self.template_cache.get(key)
        if entry:
            template, timestamp = entry
            if time() - timestamp < self.cache_ttl:
                return template
            del self.template_cache[key]
        return None

    def _cache_store(self, key: str, template):
        self.template_cache[key] = (template, time())

    # -------------------------------
    # Normalisation
    # -------------------------------
    def normalise(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s.!?]", "", text)

        sorted_phrases = sorted(self.action_synonyms.keys(), key=len, reverse=True)
        for phrase in sorted_phrases:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            text = re.sub(pattern, self.action_synonyms[phrase], text)

        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # -------------------------------
    # Extract numbers
    # -------------------------------
    def extract_numbers_and_replace(self, text: str):
        numbers = []

        def repl(match):
            numbers.append(int(match.group(1)))
            return f"<VAR{len(numbers)}>"

        modified_text = re.sub(
            r"(\d+)\s*(seconds|second|secs|sec|times|time)?",
            repl,
            text,
        )
        return modified_text, numbers

    # -------------------------------
    # Parse template into actions
    # -------------------------------
    def parse_actions(self, template_text: str) -> List[dict]:
        action_list = []

        temp_text = template_text
        for act in self.canonical_actions:
            temp_text = re.sub(rf"\b{act}\b", f"|||{act}", temp_text)

        splits = [s.strip() for s in temp_text.split("|||") if s.strip()]

        for action_str in splits:
            action_match = None
            for act in self.canonical_actions:
                if action_str.startswith(act):
                    action_match = act
                    break

            if not action_match:
                continue

            placeholders = re.findall(r"<VAR\d+>", action_str)
            params = {}

            if action_match == "say":
                params["text"] = "<TEXT>"
            else:
                for i, ph in enumerate(placeholders):
                    if action_match in self.timed_actions:
                        params["duration" if i == 0 else f"count{i}"] = ph
                    elif action_match in self.counted_actions:
                        params[f"count{i + 1}"] = ph
                    else:
                        params[f"param{i + 1}"] = ph

            action_list.append({"action": action_match, "parameters": params})

        return action_list

    # -------------------------------
    # LLM hook (override-friendly)
    # -------------------------------
    def call_llm_for_template(self, template_text: str):
        print(f"** ROUTE TO LLM: ** '{template_text}'")

        if self.llm_client is not None:
            return self.llm_client.parse_intents(template_text)

        return self.parse_actions(template_text)


    # -------------------------------
    # Fill template
    # -------------------------------
    def fill_template(
        self,
        template: List[dict],
        numbers: List[int],
        text: Optional[str] = None,
        defaults: Optional[dict] = None,
    ):

        if isinstance(template, dict):
            template = [template]

        if defaults is None:
            defaults = {"duration": 5}

        filled = []
        idx = 0

        for step in template:
            #print(f"STEP <{step}> {type(step)}")
            filled_step = {"action": step["action"], "parameters": {}}
            if ("parameters" in step):
                for param in step["parameters"]:
                    if param == "text":
                        filled_step["parameters"][param] = text
                    elif idx < len(numbers):
                        filled_step["parameters"][param] = numbers[idx]
                        idx += 1
                    else:
                        if param.startswith("count"):
                            filled_step["parameters"][param] = defaults.get(param, 1)
                        elif param == "duration":
                            filled_step["parameters"][param] = defaults.get("duration", 5)
                        else:
                            filled_step["parameters"][param] = 1

            filled.append(filled_step)

        return filled

    # -------------------------------
    # Public API
    # -------------------------------
    def route_command(self, raw_text: str, defaults: Optional[dict] = None):
        if defaults is None:
            defaults = {"duration": 5}

        norm_text = self.normalise(raw_text)

        # Extract SAY text first
        say_text = None
        say_match = re.search(r"\bsay\b", norm_text)
        if say_match:
            raw_lower = raw_text.lower()
            say_pos = raw_lower.find("say", say_match.start())
            say_text = raw_text[say_pos + 3:].strip()
            norm_text = norm_text[:say_match.start()] + "say <TEXT>"

        template_text, numbers = self.extract_numbers_and_replace(norm_text)

        cached = self._cache_lookup(template_text)
        if cached:
            print("*CACHE HIT*")
            return self.fill_template(cached, numbers, text=say_text, defaults=defaults)

        print("*CACHE MISS*")
        template = self.call_llm_for_template(template_text)

        self._cache_store(template_text, template)

        return self.fill_template(template, numbers, text=say_text, defaults=defaults)


    def load_templates(self, templates: dict):
        """
        Load a dictionary of {template_text: parsed_template} into the cache.
        These templates are treated as already valid and cached.
        """
        now = time()
        for key, template in templates.items():
            self.template_cache[key] = (template, now)
        print(f"*Loaded {len(templates)} templates into cache*")

    def load_templates_from_file(self, filepath: str):
        """
        Load templates from a JSON file.
        File format: {template_text: parsed_template}
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.load_templates(data)

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":

    from SYSTEM_PROMPT_INTENT import SYSTEM_PROMPT
    from llm_intent_processor import LLMIntentProcessor
    from ollama_client import OllamaClient as LLMClient

    LLM_SERVER = f"http://localhost:11434"
    LLM_MODEL = "gemma3:4b"

    commands = [
        #"Please say Welcome mistress",
        "sit for 10 seconds say Hello PiDog!",
        "sit for 20 seconds and say I obey",  # 'and' causes a LLM hit
        "sit for 10 seconds and say I obey. Finally bark",
        "sit for 10 seconds say I obey",

        "sit for 5 seconds and wag your tail 2 times",
        "sit for 10 seconds and wag your tail 3 times",
        "say I am your robot friend",
        "lie down and howl",
        "scratch 2 times and scratch your head",
        "walk 10 seconds and turn around",
        "sit for 4 seconds say tasks completed mistress!",
        "sit for 4 seconds say sit for 2 seconds!",
        "sit for 4 seconds and sit for 3 seconds",
        "sit for 4 seconds sit for 3 seconds",
        "sit for 2 seconds sit for 13 seconds",



    ]


    llm = LLMClient(SYSTEM_PROMPT, model=LLM_MODEL, host=LLM_SERVER)

    router = CommandRouter(llm_client=llm)

    # Load programmatically
    preloaded = {
        "sit for <VAR1> say <TEXT>": [
            {"action": "sit", "parameters": {"duration": "<VAR1>"}},
            {"action": "say", "parameters": {"text": "<TEXT>"}}
        ],

        "sit for <VAR1> and say <TEXT>": [
            {"action": "sit", "parameters": {"duration": "<VAR1>"}},
            {"action": "say", "parameters": {"text": "<TEXT>"}}
        ],

        "sit for <VAR1> wag tail <COUNT1> times": [
            {"action": "sit", "parameters": {"duration": "<VAR1>"}},
            {"action": "wag_tail", "parameters": {"count1": "<VAR1>"}}
        ]
    }
    router.load_templates(preloaded)
    print(router.template_cache)
    # Or from JSON file
    # router.load_templates_from_file("templates.json")


    for cmd in commands:
        seq = router.route_command(cmd)
        print(cmd)
        print(seq)
        print("-"*40)
