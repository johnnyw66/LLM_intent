# async_intent_router_aiomqtt.py
import asyncio
import json
from aiomqtt import Client, MqttError

from llm_intent_processor import LLMIntentProcessor
from ollama_client import OllamaClient
from text_preprocessor import preprocess_text_for_model
from normalisation_rules import normalise_object

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
SUB_TOPIC = "stt/text"
PUB_TOPICS = {
    "hat": "intent/hat",
    "zigbee": "intent/zigbee",
    "chat": "intent/chat"
}

# LLM setup
MODEL_NAME = "gemma3:4b"  # or "gemma3:4b"
llm = OllamaClient(model=MODEL_NAME)
llm_processor = LLMIntentProcessor(llm, preprocess_text_for_model, normalise_object)


async def handle_message(msg: str):
    """Preprocess text, get intents from LLM, publish per type."""
    #clean_text = preprocess_text_for_model(msg, MODEL_NAME)
    print(f"\nReceived text: {msg}")
    #print(f"Cleaned text: {clean_text}")

    intents = llm_processor.handle_text(msg)
    print(intents)

    for intent in intents.get("intents", []):
        intent_type = intent.get("type", "").lower()
        topic = PUB_TOPICS.get(intent_type)
        if topic:
            print("Topic", topic, "MESSAGE", intent)
            print(json.dumps(intent, indent=2))

    #        payload = json.dumps(intent)
    #        await mqtt_client.publish(topic, payload)
    #        print(f"Published to {topic}: {payload}")


async def mqtt_loop():
    """Main MQTT loop with automatic reconnects."""
    global mqtt_client
    mqtt_client = Client(MQTT_BROKER, MQTT_PORT)

    while True:
        try:
            async with mqtt_client as client:
                await client.subscribe(SUB_TOPIC)
                async for message in client.messages:
                    payload = message.payload.decode()
                    await handle_message(payload)

        except MqttError as error:
            print(f"MQTT Error: {error}, reconnecting in 5 seconds...")
            await asyncio.sleep(5)

        asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(mqtt_loop())


