# llm_intent_publisher.py
class LLMIntentPublisher:
    def __init__(self, llm_client, publisher):
        self.llm = llm_client
        self.publisher = publisher

    def handle_text(self, text: str):
        intents = self.llm.parse_intents(text)
        self.publisher.publish(intents)



