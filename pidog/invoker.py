from collections import deque

class CommandInvoker:
    """
    Handles execution order, queuing, and history
    """

    def __init__(self):
        self.queue = deque()
        self.history = []

    def add(self, command):
        self.queue.append(command)

    def run(self):
        while self.queue:
            cmd = self.queue.popleft()
            cmd.execute()
            self.history.append(cmd)


