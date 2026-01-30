from pidog.command_base import Command

class SitCommand(Command):
    def __init__(self, pidog):
        self.pidog = pidog

    def execute(self):
        self.pidog.sit()


class StandCommand(Command):
    def __init__(self, pidog):
        self.pidog = pidog

    def execute(self):
        self.pidog.stand()


class WalkCommand(Command):
    def __init__(self, pidog, steps=1):
        self.pidog = pidog
        self.steps = steps

    def execute(self):
        self.pidog.walk(self.steps)

