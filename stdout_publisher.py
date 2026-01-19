# stdout_publisher.py
import json
from publisher_base import Publisher

class StdoutPublisher(Publisher):
    def publish(self, data: dict):
        print(json.dumps(data, indent=2))

