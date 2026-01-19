# llm_intent_processor.py
class LLMIntentProcessor:
    def __init__(self, llm_client, preprocess_fn=None, normalise_fn=None):
        self.llm = llm_client
        self.preprocess_fn = preprocess_fn
        self.normalise_fn = normalise_fn

    def handle_text(self, text: str):

        # optional preprocessing
        clean_text = tex if not self.preprocess_fn else self.preprocess_fn(text, self.llm.model)

        intents_json = self.llm.parse_intents(clean_text)

        # optional normalisation

        if (self.normalise_fn):
            for intent in intents_json.get("intents", []):
                if "device" in intent:
                    intent["device"] = self.normalise_fn(intent["device"])
            
        return intents_json


