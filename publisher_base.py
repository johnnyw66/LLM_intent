# publisher_base.py
from abc import ABC, abstractmethod

class Publisher(ABC):
    @abstractmethod
    def publish(self, data: dict):
        pass


