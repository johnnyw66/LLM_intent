import asyncio
from fusion_hat.stt import Vosk as STT
from fusion_hat.tts import Piper

import neopixel_spi as neopixel
import board

from aiomqtt import Client as MQTTClient
HOST = "192.168.1.77"

class MQTTPublisher:
    def __init__(self, host=HOST, port=1883):
        self.host = host
        self.port = port
        self.client = None
        print(f"init: {self.host} {self.port}" )
    async def connect(self):
        self.client = MQTTClient(self.host, port=self.port)
        await self.client.__aenter__()

    async def publish(self, topic: str, payload: str):
        if self.client:
            await self.client.publish(topic, payload, qos=1)

    async def close(self):
        if self.client:
            await self.client.__aexit__(None, None, None)


# ---------------- LED SETUP ----------------

spi = board.SPI()
LED_COUNT = 3
PIXEL_ORDER = neopixel.GRB

strip = neopixel.NeoPixel_SPI(
    spi,
    LED_COUNT,
    pixel_order=PIXEL_ORDER,
    auto_write=False
)

def led(color):
    strip.fill(color)
    strip.show()

# ---------------- TTS / STT ----------------

tts = Piper()
tts.set_model("en_GB-semaine-medium")

stt = STT(language="en-gb")

# ---------------- THREAD WORKER ----------------

def stt_worker_dep(loop: asyncio.AbstractEventLoop, queue: asyncio.Queue):
    for result in stt.listen(stream=True):
        if result["done"]:
            text = result["final"].strip()
            if text and text != "huh":
                loop.call_soon_threadsafe(queue.put_nowait, text)

def stt_worker(loop: asyncio.AbstractEventLoop, queue: asyncio.Queue):
    print("sst_worker")
    while True:
        try:
            print("READY FOR SPEECH")
            for result in stt.listen(stream=True):
                if result["done"]:
                    text = result["final"].strip()
                    if text and text != "huh":
                        loop.call_soon_threadsafe(queue.put_nowait, text)
                    break   # 🔴 exit inner loop → restart STT
        except Exception as e:
            print("STT error:", e)


# ---------------- ASYNC HELPERS ----------------

async def say(text: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, tts.say, text)

# ---------------- MAIN LOOP ----------------

async def main():
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()
    mqtt = MQTTPublisher(host = HOST, port=1883)
    await mqtt.connect()

    # Start STT listener in background thread
    loop.run_in_executor(None, stt_worker, loop, queue)

    led((0, 255, 0))
    await say("Say something")

    while True:
        print("awaiting queue")
        text = await queue.get()

        print(f"\nFinal: {text}")
        led((0, 0, 255))
        await say(text)
        print("Text completed")
        await mqtt.publish("stt/text", text)

        led((0, 255, 0))

        # 🔜 MQTT publish goes HERE
        # await mqtt_publish(text)

# ---------------- ENTRY ----------------

try:
    asyncio.run(main())
except KeyboardInterrupt:
    led((0, 0, 0))
    print("Exiting cleanly")

