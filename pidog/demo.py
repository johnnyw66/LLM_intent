# Temporary hardware test harness

from pidog.invoker import CommandInvoker
from pidog.commands.voice import SayCommand
from pidog.commands.motion import SitCommand

def main(pidog):
    invoker = CommandInvoker()
    invoker.add(SayCommand(pidog, "System online"))
    invoker.add(SitCommand(pidog))
    invoker.run()

if __name__ == "__main__":
    print("Wire real hardware here")


