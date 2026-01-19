from abc import ABC, abstractmethod

class LLMClient(ABC):
	@abstractmethod
	def parse_intents(self, user_text: str) -> dict:
		"""
		Sends text to LLM and returns LLM response according to SYSTEM_PROMPT
		"""
		pass
	
