from pidog.command_base import Command

class SetLEDCommand(Command):
    def __init__(self, pidog, r, g, b):
        self.pidog = pidog
        self.color = (r, g, b)

    def execute(self):
        self.pidog.set_led(*self.color)


