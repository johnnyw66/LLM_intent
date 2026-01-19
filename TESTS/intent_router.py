class IntentRouter:
    def __init__(self, llm_client):
        self.llm = llm_client

    def parse(self, text: str) -> dict:
        """
        Parse the text using the LLM backend and return structured intents.
        """
        return self.llm.parse_intents(text)



