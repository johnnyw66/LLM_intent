from abc import ABC, abstractmethod

class Command(ABC):
    """
    Base class for all PiDog commands
    """

    @abstractmethod
    def execute(self):
        pass

    def undo(self):
        """Optional undo support"""
        pass


