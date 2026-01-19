# normalization_rules.py
SYNONYMS = {
    "lamp": ["lamp", "light", "ceiling light"],
    "neo": ["neo", "neopixel", "neolight"],
}

def normalise_object(text_object: str) -> str:
    for key, variants in SYNONYMS.items():
        if text_object.lower() in variants:
            return key
    return text_object


