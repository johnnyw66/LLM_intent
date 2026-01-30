class PiDog:
    """
    Hardware abstraction for Sunfounder PiDog + Pi Hat 5+
    """

    def __init__(self, dog, rgb):
        self.dog = dog
        self.rgb = rgb

    def say(self, text: str):
        self.dog.say(text)

    def sit(self):
        self.dog.sit()

    def stand(self):
        self.dog.stand()

    def walk(self, steps=1):
        for _ in range(steps):
            self.dog.walk()

    def bark(self):
        self.dog.bark()

    def howl(self):
        self.dog.howl()

    def lie_down(self):
        self.dog.lie()

    def shake_paw(self):
        self.dog.shake()

    def scratch(self):
        self.dog.scratch()

    def set_led(self, r, g, b):
        self.rgb.set_color((r, g, b))


