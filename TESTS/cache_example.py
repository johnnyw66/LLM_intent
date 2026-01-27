import re
from time import time

# -------------------------------
# Cache for templates
# -------------------------------
TEMPLATE_CACHE = {}
CACHE_TTL = 3600  # 1 hour

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
# Normalisation
# -------------------------------
ACTION_SYNONYMS = {
    "woof": "bark",
    "shake the paw": "shake_paw",
    "light": "led",
    "colour": "color",
    "wag tail": "wag_tail"
}

def normalise(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    for k, v in ACTION_SYNONYMS.items():
        text = text.replace(k, v)
    return text.strip()

# -------------------------------
# Extract numbers and map them to placeholders
# -------------------------------
def extract_numbers_and_replace(text):
    """
    Finds all numbers and replaces them with placeholders like <VAR1>, <VAR2>, ...
    Returns:
        - modified text with placeholders
        - list of numbers in order
    """
    numbers = []
    def repl(match):
        numbers.append(int(match.group(1)))
        return f"<VAR{len(numbers)}>"
    modified_text = re.sub(r"(\d+)\s*(seconds|second|secs|sec|times|time)?", repl, text)
    return modified_text, numbers

# -------------------------------
# Parse actions into a sequence template
# -------------------------------
def parse_actions(template_text):
    """
    Converts template text with placeholders into a list of actions with parameter placeholders
    """
    action_list = []
    # Split by "and" (could also add "," etc.)
    splits = [s.strip() for s in re.split(r"\band\b", template_text) if s.strip()]
    
    for action_str in splits:
        # Identify action name (first known keyword)
        action_match = re.match(r"(sit|bark|shake_paw|wag_tail|led)", action_str)
        if not action_match:
            continue
        action_name = action_match.group(1)
        # Find all placeholders in this action
        placeholders = re.findall(r"<VAR\d+>", action_str)
        params = {}
        for idx, ph in enumerate(placeholders, start=1):
            # Use generic param names: duration, count, count2...
            if "duration" not in params:
                params[f"duration"] = ph
            else:
                # if multiple numbers in same action, give them numbered param
                params[f"count{idx}"] = ph
        action_list.append({"action": action_name, "parameters": params})
    return action_list

# -------------------------------
# Main parsing function
# -------------------------------
def parse_multi_action_command(raw_text: str):
    norm_text = normalise(raw_text)
    
    # Check cache first
    cached_template = cache_lookup(norm_text)
    if cached_template:
        # Fill in numbers for runtime
        numbers = [int(m.group(1)) for m in re.finditer(r"(\d+)", raw_text)]
        filled_sequence = []
        num_idx = 0
        for step in cached_template:
            filled_step = {"action": step["action"], "parameters": {}}
            for param, placeholder in step["parameters"].items():
                filled_step["parameters"][param] = numbers[num_idx]
                num_idx += 1
            filled_sequence.append(filled_step)
        return filled_sequence

    # First time: create template
    template_text, numbers = extract_numbers_and_replace(norm_text)
    sequence_template = parse_actions(template_text)
    
    # Cache template
    cache_store(norm_text, sequence_template)
    
    # Fill numbers for this run
    filled_sequence = []
    num_idx = 0
    for step in sequence_template:
        filled_step = {"action": step["action"], "parameters": {}}
        for param in step["parameters"]:
            filled_step["parameters"][param] = numbers[num_idx]
            num_idx += 1
        filled_sequence.append(filled_step)
    
    return filled_sequence

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    commands = [
        "sit for 10 seconds and wag tail 3 times",
        "bark 2 times and sit for 5 seconds",
        "shake the paw for 4 seconds and wag tail 2 times"
    ]
    
    for cmd in commands:
        seq = parse_multi_action_command(cmd)
        print(cmd)
        print(seq)
        print("-"*40)
