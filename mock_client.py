class MockLLMClient:
    def parse_intents(self, user_text):
        # Return dummy JSON for testing
        return {"intents": [{"type": "hat", "action": "shake_paw"}]}


