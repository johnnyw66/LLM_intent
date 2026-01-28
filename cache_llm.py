import re
from time import time

# -------------------------------
# Cache for templates
# -------------------------------
TEMPLATE_CACHE = {}
CACHE_TTL = 3600  # seconds

def cache_lookup(key):
    entry = TEMPLATE_CACHE.get(key)
    if entry:
        template, timestamp = entry
        if time() - timestamp < CACHE_TTL:
            return template
        del TEMPLATE_CACHE[key]
    return None

def cache_store(key, template):
    TEMPLATE_CACHE[key] = (template, time())

# -------------------------------
# Action synonyms / multi-word phrases
# -------------------------------
ACTION_SYNONYMS = {
    "woof": "bark",
    "shake the paw": "shake_paw",
    "wag your tail": "wag_tail",
    "wag tail": "wag_tail",
    "spin around": "spin",
    "light": "led",
    "colour": "color",
    "lie down": "lie",
    "scratch your head": "scratch_head",
    "turn around": "turn"
}

CANONICAL_ACTIONS = [
    "sit", "bark", "shake_paw", "wag_tail", "led", "spin",
    "lie", "howl", "scratch", "scratch_head", "walk", "turn", "say"
]

# -------------------------------
# Action type classification
# -------------------------------
TIMED_ACTIONS = {"sit", "walk", "lie", "bark", "howl", "led"}
COUNTED_ACTIONS = {"wag_tail", "shake_paw", "spin", "scratch", "scratch_head", "turn"}

# -------------------------------
# Normalisation
# -------------------------------
def normalise(text: str) -> str:
    """
    Normalise text:
    - lowercase, remove punctuation except sentence delimiters
    - map multi-word phrases to canonical actions
    - collapse whitespace
    """
    text = text.lower()
    text = re.sub(r"[^\w\s.!?]", "", text)
    # Replace multi-word phrases first
    sorted_phrases = sorted(ACTION_SYNONYMS.keys(), key=len, reverse=True)
    for phrase in sorted_phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        text = re.sub(pattern, ACTION_SYNONYMS[phrase], text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------------------
# Extract numbers and replace with placeholders
# -------------------------------
def extract_numbers_and_replace(text):
    numbers = []
    def repl(match):
        numbers.append(int(match.group(1)))
        return f"<VAR{len(numbers)}>"
    modified_text = re.sub(r"(\d+)\s*(seconds|second|secs|sec|times|time)?", repl, text)
    return modified_text, numbers

# -------------------------------
# Parse actions into structured template
# -------------------------------
def parse_actions(template_text):
    action_list = []

    # Split on 'and', '.', '!', '?' and also detect known action names sequentially
    splits = []
    # Add spaces around known actions to help splitting
    temp_text = template_text
    for act in CANONICAL_ACTIONS:
        temp_text = re.sub(rf"\b{act}\b", f"|||{act}", temp_text)
    splits = [s.strip() for s in temp_text.split("|||") if s.strip()]

    for action_str in splits:
        # Identify which canonical action this is
        action_match = None
        for act in CANONICAL_ACTIONS:
            if action_str.startswith(act):
                action_match = act
                break
        if not action_match:
            continue

        action_name = action_match
        placeholders = re.findall(r"<VAR\d+>", action_str)
        params = {}

        if action_name == "say":
            # Take the rest of the string after "say" as text placeholder
            params["text"] = "<TEXT>"
        else:
            for i, ph in enumerate(placeholders):
                if action_name in TIMED_ACTIONS:
                    if i == 0:
                        params["duration"] = ph
                    else:
                        params[f"count{i}"] = ph
                elif action_name in COUNTED_ACTIONS:
                    if i == 0:
                        params["count1"] = ph
                    else:
                        params[f"count{i+1}"] = ph
                else:
                    params[f"param{i+1}"] = ph

        action_list.append({"action": action_name, "parameters": params})

    return action_list

# -------------------------------
# Mock LLM call
# -------------------------------
def call_llm_for_template(template_text):
    print(f"** ROUTE TO LLM: ** call_llm_for_template: '{template_text}'")  # Debug
    return parse_actions(template_text)

# -------------------------------
# Fill numbers and text dynamically
# -------------------------------
def fill_template(template, numbers, text=None, defaults=None):
    if defaults is None:
        defaults = {"duration": 5}
    
    filled = []
    idx = 0
    for step in template:
        filled_step = {"action": step["action"], "parameters": {}}
        for param, value in step["parameters"].items():
            if param == "text":
                filled_step["parameters"][param] = text
            elif idx < len(numbers):
                filled_step["parameters"][param] = numbers[idx]
                idx += 1
            else:
                # default values
                if param.startswith("count"):
                    filled_step["parameters"][param] = defaults.get(param, 1)
                elif param == "duration":
                    filled_step["parameters"][param] = defaults.get("duration", 5)
                else:
                    filled_step["parameters"][param] = 1
        filled.append(filled_step)
    return filled

# -------------------------------
# Full route_command function
# -------------------------------
def route_command(raw_text: str, defaults=None):
    if defaults is None:
        defaults = {"duration": 5}

    # 1. Normalise (intent only)
    norm_text = normalise(raw_text)

    # 2. Extract SAY text FIRST (from RAW text)
    say_text = None
    say_match = re.search(r"\bsay\b", norm_text)
    if say_match:
        # Extract everything after "say" from RAW text (not normalised)
        raw_lower = raw_text.lower()
        say_pos = raw_lower.find("say", say_match.start())
        say_text = raw_text[say_pos + 3:].strip()

        # Replace EVERYTHING after 'say' in the normalised string
        norm_text = norm_text[:say_match.start()] + "say <TEXT>"

    # 3. Extract numbers AFTER say replacement
    template_text, numbers = extract_numbers_and_replace(norm_text)

    # 4. Cache lookup (intent-only key)
    cached_template = cache_lookup(template_text)
    if cached_template:
        print("*CACHE HIT*")
        return fill_template(
            cached_template,
            numbers,
            text=say_text,
            defaults=defaults
        )

    # 5. First time → build template (LLM or rule-based)
    template = call_llm_for_template(template_text)
    cache_store(template_text, template)
    print("*CACHE MISS*")
    return fill_template(
        template,
        numbers,
        text=say_text,
        defaults=defaults
    )

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    commands = [
        "Please say ''Welcome mistress''",
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

    for cmd in commands:
        seq = route_command(cmd)
        print(cmd)
        print(seq)
        print("-"*40)
