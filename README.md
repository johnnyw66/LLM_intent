Intent Router (LLM-Based Command Parser)

This Python module implements a deterministic intent router for spoken or textual commands, designed for use with:

SunFounder Fusion / PiDog HAT

Zigbee devices (via Node-RED or MQTT)

Local or remote LLMs (Ollama, Gemini, etc.)

Its sole responsibility is to convert natural language text into structured JSON intents.
It does not execute commands.

What this module does

The module accepts plain text (typically the output of Speech-to-Text) and returns a JSON structure describing:

HAT actions (PiDog movements, sounds, Neo LEDs, speech)

Zigbee actions (lights, color, dimming, power)

Chat requests (questions that should be answered by a conversational LLM)

Example input:

Sleep for 10 seconds. Turn NEO lights red. Shake your paw.
Turn lamp on for 20 seconds then turn off.


Example output:
'''
{
  "intents": [
    { "type": "hat", "action": "sleep", "delay": 10 },
    { "type": "hat", "action": "set_neo", "color": "red" },
    { "type": "hat", "action": "shake_paw" },
    { "type": "zigbee", "device": "lamp", "room": "living room", "action": "on" },
    { "type": "zigbee", "device": "lamp", "room": "living room", "action": "off", "delay": 20 }
  ]
}
'''

What this module deliberately does not do

❌ No hardware control

❌ No Zigbee, MQTT, or Node-RED logic

❌ No scheduling or timing logic

❌ No speech synthesis or playback

❌ No orchestration

Those responsibilities belong to downstream services.

This module is a pure intent classifier.

Design philosophy
1. Deterministic output

LLM temperature is set to 0

Output must be valid JSON

No free-form text

No hallucinated fields

The LLM is treated as a parser, not a chatbot.

2. Small-model friendly (gemma3:1b)

The SYSTEM_PROMPT is intentionally written to work reliably with small LLMs:

No placeholders (<device>, {value}, etc.)

No symbolic grammar

No angle brackets

Plain English rules only

This allows the module to run on constrained hardware.

3. Lexical normalization over semantic inference

Instead of asking the LLM to “understand” language, the prompt defines normalization rules, for example:

Dropping the word "to" before parsing

"turn lamp to blue" → "turn lamp blue"

Treating "sleep", "wait", and "pause" as equivalent

Normalizing PiDog action synonyms (sit, sit down, etc.)

This dramatically improves reliability on small models.

Supported intent types
HAT intents (type: "hat")

Examples of supported actions:

Movement: sit, lie, stand, roll, stretch, shake_paw

Sound: bark, howl

Speech: say

LEDs: set_neo (color, brightness, effects)

Timing: sleep

Example:

{ "type": "hat", "action": "bark" }

Zigbee intents (type: "zigbee")

Supported operations include:

Power: on, off

Color: set_color

Brightness: dim

Example:

{
  "type": "zigbee",
  "device": "lamp",
  "room": "bedroom",
  "action": "set_color",
  "color": "blue"
}


Delays can be attached to the preceding action:

{ "action": "off", "delay": 20 }

Chat intents (type: "chat")

Any request that is not a command is classified as a chat intent.

Example:

{ "type": "chat", "text": "What is Ohm's law?" }


Chat intents are intended to be passed to a separate conversational LLM.

Ordering and delays

Intents are returned in spoken order

Delays (sleep, wait, pause, or “for N seconds”) apply to:

The intent they appear with, or

The immediately preceding intent (depending on phrasing)

This module does not schedule delays — it only describes them

Typical pipeline usage
Speech-to-Text
      ↓
Intent Router (this module)
      ↓
Orchestrator / MQTT Router
      ↓
HAT Controller / Zigbee / Chat LLM

Why use an LLM at all?

A traditional rules engine struggles with:

Compound commands

Natural phrasing

Mixed domains (robot + home automation + chat)

Using a small, constrained LLM provides:

Flexible language input

Deterministic structured output

No hard-coded grammar explosion

Model compatibility

Tested primarily with:

gemma3:1b (preferred for embedded / edge)

gemma3:4b (more forgiving, higher accuracy)

The SYSTEM_PROMPT is tuned specifically for 1b stability.

Status

This module is intentionally narrow in scope and considered stable once the SYSTEM_PROMPT is frozen.

Future extensions should:

Add new actions

Add new normalization rules

Avoid changing output structure
