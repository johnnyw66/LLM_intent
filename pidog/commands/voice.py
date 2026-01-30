from pidog.command_base import Command

class SayCommand(Command):
    def __init__(self, pidog, text):
        self.pidog = pidog
        self.text = text

    def execute(self):
        self.pidog.say(self.text)


class BarkCommand(Command):
    def __init__(self, pidog):
        self.pidog = pidog

    def execute(self):
        self.pidog.bark()


class HowlCommand(Command):
    def __init__(self, pidog):
        self.pidog = pidog

    def execute(self):
        self.pidog.howl()


