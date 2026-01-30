from pidog.command_base import Command

class MacroCommand(Command):
    """
    Execute multiple commands in order
    """

    def __init__(self, commands):
        self.commands = commands

    def execute(self):
        for cmd in self.commands:
            cmd.execute()


