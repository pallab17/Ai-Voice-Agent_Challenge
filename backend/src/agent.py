
# import logging

# from dotenv import load_dotenv
# from livekit.agents import (
#     Agent,
#     AgentSession,
#     JobContext,
#     JobProcess,
#     MetricsCollectedEvent,
#     RoomInputOptions,
#     WorkerOptions,
#     cli,
#     metrics,
#     tokenize,
#     # function_tool,
#     # RunContext
# )
# from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# logger = logging.getLogger("agent")

# load_dotenv(".env.local")


# class Assistant(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions="""You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
#             You eagerly assist users with their questions by providing information from your extensive knowledge.
#             Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
#             You are curious, friendly, and have a sense of humor.""",
#         )

#     # To add tools, use the @function_tool decorator.
#     # Here's an example that adds a simple weather tool.
#     # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
#     # @function_tool
#     # async def lookup_weather(self, context: RunContext, location: str):
#     #     """Use this tool to look up current weather information in the given location.
#     #
#     #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
#     #
#     #     Args:
#     #         location: The location to look up weather information for (e.g. city name)
#     #     """
#     #
#     #     logger.info(f"Looking up weather for {location}")
#     #
#     #     return "sunny with a temperature of 70 degrees."


# def prewarm(proc: JobProcess):
#     proc.userdata["vad"] = silero.VAD.load()


# async def entrypoint(ctx: JobContext):
#     # Logging setup
#     # Add any other context you want in all log entries here
#     ctx.log_context_fields = {
#         "room": ctx.room.name,
#     }

#     # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
#     session = AgentSession(
#         # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
#         # See all available models at https://docs.livekit.io/agents/models/stt/
#         stt=deepgram.STT(model="nova-3"),
#         # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
#         # See all available models at https://docs.livekit.io/agents/models/llm/
#         llm=google.LLM(
#                 model="gemini-2.5-flash",
#             ),
#         # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
#         # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
#         tts=murf.TTS(
#                 voice="en-US-matthew", 
#                 style="Conversation",
#                 tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
#                 text_pacing=True
#             ),
#         # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
#         # See more at https://docs.livekit.io/agents/build/turns
#         turn_detection=MultilingualModel(),
#         vad=ctx.proc.userdata["vad"],
#         # allow the LLM to generate a response while waiting for the end of turn
#         # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
#         preemptive_generation=True,
#     )

#     # To use a realtime model instead of a voice pipeline, use the following session setup instead.
#     # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
#     # 1. Install livekit-agents[openai]
#     # 2. Set OPENAI_API_KEY in .env.local
#     # 3. Add `from livekit.plugins import openai` to the top of this file
#     # 4. Use the following session setup instead of the version above
#     # session = AgentSession(
#     #     llm=openai.realtime.RealtimeModel(voice="marin")
#     # )

#     # Metrics collection, to measure pipeline performance
#     # For more information, see https://docs.livekit.io/agents/build/metrics/
#     usage_collector = metrics.UsageCollector()

#     @session.on("metrics_collected")
#     def _on_metrics_collected(ev: MetricsCollectedEvent):
#         metrics.log_metrics(ev.metrics)
#         usage_collector.collect(ev.metrics)

#     async def log_usage():
#         summary = usage_collector.get_summary()
#         logger.info(f"Usage: {summary}")

#     ctx.add_shutdown_callback(log_usage)

#     # # Add a virtual avatar to the session, if desired
#     # # For other providers, see https://docs.livekit.io/agents/models/avatar/
#     # avatar = hedra.AvatarSession(
#     #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
#     # )
#     # # Start the avatar and wait for it to join
#     # await avatar.start(session, room=ctx.room)

#     # Start the session, which initializes the voice pipeline and warms up the models
#     await session.start(
#         agent=Assistant(),
#         room=ctx.room,
#         room_input_options=RoomInputOptions(
#             # For telephony applications, use `BVCTelephony` for best results
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     # Join the room and connect to the user
#     await ctx.connect()


# if __name__ == "__main__":
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))




# import logging
# import os
# import json
# from datetime import datetime

# from dotenv import load_dotenv
# from livekit.agents import (
#     Agent,
#     AgentSession,
#     JobContext,
#     JobProcess,
#     MetricsCollectedEvent,
#     RoomInputOptions,
#     WorkerOptions,
#     cli,
#     metrics,
# )
# from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# logger = logging.getLogger("agent")

# load_dotenv(".env.local")

# # =======================================
# #         ORDER LOGIC (DAY 2)
# # =======================================

# ORDERS_DIR = os.path.join(os.path.dirname(__file__), "..", "orders")
# os.makedirs(ORDERS_DIR, exist_ok=True)

# ORDER_FIELDS = {
#     "drinkType": "Sure! What drink would you like?",
#     "size": "Great! What size would you prefer? Small, medium or large?",
#     "milk": "Nice! What milk would you like?",
#     "extras": "Any extras? You can say none.",
#     "name": "Perfect! What name should I put on the order?"
# }


# def normalize_extras(x: str):
#     x = x.lower().strip()
#     if x in ["no", "none", "nothing"]:
#         return []
#     parts = [p.strip() for p in x.replace("and", ",").split(",")]
#     return parts


# def save_order(order: dict):
#     ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
#     file_path = os.path.join(ORDERS_DIR, f"order_{ts}.json")

#     # Save latest
#     json.dump(order, open(os.path.join(ORDERS_DIR, "latest.json"), "w"), indent=2)
#     # Save timestamped
#     json.dump(order, open(file_path, "w"), indent=2)


# # =======================================
# #              ASSISTANT
# # =======================================

# class Assistant(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions="""
#             You are JavaJoy — a friendly coffee shop barista.
#             You take coffee orders step by step.
#             Required fields: drinkType, size, milk, extras, name.
#             Ask one question at a time. Keep answers short & friendly.
#             When order is complete:
#               - Confirm it
#               - DO NOT talk about JSON or code.
#             """,
#         )
#         self.order_state = {}
#         self.waiting_for = None

#     async def handle_barista(self, text: str) -> str:
#         clean = text.strip().lower()

#         # If we were waiting for a field answer
#         if self.waiting_for:
#             field = self.waiting_for

#             if field == "extras":
#                 self.order_state["extras"] = normalize_extras(clean)
#             else:
#                 self.order_state[field] = text.strip()

#             self.waiting_for = None

#         # Ask next missing field
#         for field, question in ORDER_FIELDS.items():
#             if field not in self.order_state or not self.order_state[field]:
#                 self.waiting_for = field
#                 return question

#         # Order complete → save
#         order = self.order_state.copy()
#         order["timestamp"] = datetime.utcnow().isoformat()
#         save_order(order)

#         drink = order["drinkType"]
#         size = order["size"]
#         milk = order["milk"]
#         extras = ", ".join(order["extras"]) if order["extras"] else "no extras"
#         name = order["name"]

#         # Reset for next order
#         self.order_state = {}
#         self.waiting_for = None

#         return f"Thanks {name}! Your {size} {drink} with {milk} milk and {extras} is placed."


# # =======================================
# #            ENTRYPOINT
# # =======================================

# def prewarm(proc: JobProcess):
#     proc.userdata["vad"] = silero.VAD.load()


# async def entrypoint(ctx: JobContext):
#     ctx.log_context_fields = { "room": ctx.room.name }

#     session = AgentSession(
#         stt=deepgram.STT(model="nova-3"),
#         llm=google.LLM(model="gemini-2.5-flash"),
#         tts=murf.TTS(
#             voice="en-US-matthew",
#             style="Conversation"
#         ),
#         turn_detection=MultilingualModel(),
#         vad=ctx.proc.userdata["vad"],
#         preemptive_generation=True,
#     )

#     usage_collector = metrics.UsageCollector()

#     @session.on("metrics_collected")
#     def _on_metrics(ev: MetricsCollectedEvent):
#         metrics.log_metrics(ev.metrics)
#         usage_collector.collect(ev.metrics)

#     async def log_usage():
#         logger.info(f"Usage: {usage_collector.get_summary()}")

#     ctx.add_shutdown_callback(log_usage)

#     assistant = Assistant()

#     await session.start(
#         agent=assistant,
#         room=ctx.room,
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     # Tie user messages to barista logic
#     @session.on("user_message")
#     async def on_user_message(ev):
#         reply = await assistant.handle_barista(ev.text)
#         await session.send_text(reply)

#     await ctx.connect()


# if __name__ == "__main__":
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))

# import logging
# import os
# import json
# from datetime import datetime

# from dotenv import load_dotenv
# from livekit.agents import (
#     Agent,
#     AgentSession,
#     JobContext,
#     JobProcess,
#     MetricsCollectedEvent,
#     RoomInputOptions,
#     WorkerOptions,
#     cli,
#     metrics,
# )
# from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# logger = logging.getLogger("agent")

# load_dotenv(".env.local")

# # =======================================
# #         ORDER LOGIC (DAY 2)
# # =======================================

# ORDERS_DIR = os.path.join(os.path.dirname(__file__), "..", "orders")
# os.makedirs(ORDERS_DIR, exist_ok=True)

# print("ORDERS_DIR resolved as:", ORDERS_DIR)

# ORDER_FIELDS = {
#     "drinkType": "Sure! What drink would you like?",
#     "size": "Great! What size would you prefer? Small, medium or large?",
#     "milk": "Nice! What milk would you like?",
#     "extras": "Any extras? You can say none.",
#     "name": "Perfect! What name should I put on the order?"
# }

# def normalize_extras(x: str):
#     x = x.lower().strip()
#     if x in ["no", "none", "nothing"]:
#         return []
#     parts = [p.strip() for p in x.replace("and", ",").split(",")]
#     return parts

# def save_order(order: dict):
#     ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
#     file_path = os.path.join(ORDERS_DIR, f"order_{ts}.json")

#     print("Saving ORDER to:", file_path)
#     print("Saving LATEST to:", os.path.join(ORDERS_DIR, "latest.json"))

#     # Save latest
#     json.dump(order, open(os.path.join(ORDERS_DIR, "latest.json"), "w"), indent=2)
#     # Save timestamped
#     json.dump(order, open(file_path, "w"), indent=2)

# # =======================================
# #              ASSISTANT
# # =======================================

# class Assistant(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions="""
#             You are JavaJoy — a friendly coffee shop barista.
#             You take coffee orders step by step.
#             Required fields: drinkType, size, milk, extras, name.
#             Ask one question at a time. Keep answers short & friendly.
#             When order is complete:
#               - Confirm it
#               - DO NOT talk about JSON or code.
#             """,
#         )
#         self.order_state = {}
#         self.waiting_for = None

#     async def handle_barista(self, text: str) -> str:
#         clean = text.strip().lower()
#         print("\n--- USER SAID:", text)

#         # If we were waiting for a field answer
#         if self.waiting_for:
#             field = self.waiting_for
#             print("Field expected:", field)

#             if field == "extras":
#                 self.order_state["extras"] = normalize_extras(clean)
#             else:
#                 self.order_state[field] = text.strip()

#             print("Field stored:", self.order_state)

#             self.waiting_for = None

#         # Ask next missing field
#         print("Checking next missing field…")
#         for field, question in ORDER_FIELDS.items():
#             if field not in self.order_state or not self.order_state[field]:
#                 print("Missing field found:", field)
#                 self.waiting_for = field
#                 return question

#         # Order complete → save
#         print("ORDER COMPLETE! Final order:")
#         print(self.order_state)

#         order = self.order_state.copy()
#         order["timestamp"] = datetime.utcnow().isoformat()
#         save_order(order)

#         drink = order["drinkType"]
#         size = order["size"]
#         milk = order["milk"]
#         extras = ", ".join(order["extras"]) if order["extras"] else "no extras"
#         name = order["name"]

#         # Reset for next order
#         self.order_state = {}
#         self.waiting_for = None

#         return f"Thanks {name}! Your {size} {drink} with {milk} milk and {extras} is placed."


# # =======================================
# #            ENTRYPOINT
# # =======================================

# def prewarm(proc: JobProcess):
#     proc.userdata["vad"] = silero.VAD.load()

# async def entrypoint(ctx: JobContext):
#     ctx.log_context_fields = { "room": ctx.room.name }

#     session = AgentSession(
#         stt=deepgram.STT(model="nova-3"),
#         llm=google.LLM(model="gemini-2.5-flash"),
#         tts=murf.TTS(
#             voice="en-US-matthew",
#             style="Conversation"
#         ),
#         turn_detection=MultilingualModel(),
#         vad=ctx.proc.userdata["vad"],
#         preemptive_generation=True,
#     )

#     usage_collector = metrics.UsageCollector()

#     @session.on("metrics_collected")
#     def _on_metrics(ev: MetricsCollectedEvent):
#         metrics.log_metrics(ev.metrics)
#         usage_collector.collect(ev.metrics)

#     assistant = Assistant()

#     await session.start(
#         agent=assistant,
#         room=ctx.room,
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     # Tie user messages to barista logic
#     @session.on("user_message")
#     async def on_user_message(ev):
#         print("RAW USER MESSAGE EVENT:", ev.text)
#         reply = await assistant.handle_barista(ev.text)
#         print("BOT REPLY:", reply)
#         await session.send_text(reply)

#     await ctx.connect()

# if __name__ == "__main__":
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))

# import logging
# import os
# import json
# from datetime import datetime

# from dotenv import load_dotenv
# from livekit.agents import (
#     Agent,
#     AgentSession,
#     JobContext,
#     JobProcess,
#     MetricsCollectedEvent,
#     RoomInputOptions,
#     WorkerOptions,
#     cli,
#     metrics,
# )
# from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# logger = logging.getLogger("agent")

# load_dotenv(".env.local")

# # =======================================
# #         ORDER LOGIC (DAY 2)
# # =======================================

# # 🔥 FIX 100% WORKING PATH
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ORDERS_DIR = os.path.join(BASE_DIR, "orders")
# os.makedirs(ORDERS_DIR, exist_ok=True)

# print("🔥 ORDERS_DIR =", ORDERS_DIR)  # DEBUG

# ORDER_FIELDS = {
#     "drinkType": "Sure! What drink would you like?",
#     "size": "Great! What size would you prefer? small, medium or large?",
#     "milk": "Nice! What milk would you like?",
#     "extras": "Any extras? You can say 'none'.",
#     "name": "Perfect! What name should I put on the order?"
# }


# def normalize_extras(x: str):
#     x = x.lower().strip()
#     if x in ["no", "none", "nothing"]:
#         return []
#     parts = [p.strip() for p in x.replace("and", ",").split(",")]
#     return parts


# def save_order(order: dict):
#     ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
#     file_path = os.path.join(ORDERS_DIR, f"order_{ts}.json")

#     print("🔥 Saving order JSON to:", file_path)  # DEBUG

#     with open(file_path, "w") as f:
#         json.dump(order, f, indent=2)

#     with open(os.path.join(ORDERS_DIR, "latest.json"), "w") as f:
#         json.dump(order, f, indent=2)


# # =======================================
# #             ASSISTANT
# # =======================================

# class Assistant(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions="""
#             You are JavaJoy — a friendly coffee shop barista.
#             You take coffee orders step by step.
#             Required fields: drinkType, size, milk, extras, name.
#             Ask one question at a time. Keep answers short & friendly.
#             When order is complete:
#               - Confirm politely
#               - Do NOT mention JSON or code.
#             """,
#         )
#         self.order_state = {}
#         self.waiting_for = None

#     async def handle_barista(self, text: str) -> str:
#         clean = text.strip().lower()

#         # If waiting for specific field
#         if self.waiting_for:
#             field = self.waiting_for

#             if field == "extras":
#                 self.order_state["extras"] = normalize_extras(clean)
#             else:
#                 self.order_state[field] = text.strip()

#             print("🔥 Current state:", self.order_state)  # Debug

#             self.waiting_for = None

#         # Ask next missing field
#         for field, question in ORDER_FIELDS.items():
#             if field not in self.order_state or not self.order_state[field]:
#                 self.waiting_for = field
#                 return question

#         # Order complete
#         order = self.order_state.copy()
#         order["timestamp"] = datetime.utcnow().isoformat()
#         save_order(order)

#         drink = order["drinkType"]
#         size = order["size"]
#         milk = order["milk"]
#         extras = ", ".join(order["extras"]) if order["extras"] else "no extras"
#         name = order["name"]

#         # Reset
#         self.order_state = {}
#         self.waiting_for = None

#         return f"Thanks {name}! Your {size} {drink} with {milk} milk and {extras} is placed."


# # =======================================
# #            ENTRYPOINT
# # =======================================

# def prewarm(proc: JobProcess):
#     proc.userdata["vad"] = silero.VAD.load()


# async def entrypoint(ctx: JobContext):
#     ctx.log_context_fields = { "room": ctx.room.name }

#     session = AgentSession(
#         stt=deepgram.STT(model="nova-3"),
#         llm=google.LLM(model="gemini-2.5-flash"),
#         tts=murf.TTS(
#             voice="en-US-matthew",
#             style="Conversation"
#         ),
#         turn_detection=MultilingualModel(),
#         vad=ctx.proc.userdata["vad"],
#         preemptive_generation=True,
#     )

#     usage_collector = metrics.UsageCollector()

#     @session.on("metrics_collected")
#     def _on_metrics(ev: MetricsCollectedEvent):
#         metrics.log_metrics(ev.metrics)
#         usage_collector.collect(ev.metrics)

#     async def log_usage():
#         logger.info(f"Usage: {usage_collector.get_summary()}")

#     ctx.add_shutdown_callback(log_usage)

#     assistant = Assistant()

#     await session.start(
#         agent=assistant,
#         room=ctx.room,
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     @session.on("user_message")
#     async def on_user_message(ev):
#         reply = await assistant.handle_barista(ev.text)
#         await session.send_text(reply)

#     await ctx.connect()


# if __name__ == "__main__":
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))






# import logging
# import os
# import json
# from datetime import datetime

# from dotenv import load_dotenv
# from livekit.agents import (
#     Agent,
#     AgentSession,
#     JobContext,
#     JobProcess,
#     MetricsCollectedEvent,
#     RoomInputOptions,
#     WorkerOptions,
#     cli,
#     metrics,
# )
# from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# logger = logging.getLogger("agent")

# load_dotenv(".env.local")

# # =======================================
# #         ORDER SYSTEM (DAY 2)
# # =======================================

# # Correct orders directory (inside /src)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ORDERS_DIR = os.path.join(BASE_DIR, "orders")
# os.makedirs(ORDERS_DIR, exist_ok=True)

# print("🔥 ORDERS_DIR =", ORDERS_DIR)

# ORDER_FIELDS = {
#     "drinkType": "Sure! What drink would you like?",
#     "size": "Great! What size would you like? Small, medium or large?",
#     "milk": "Nice! What milk should I use?",
#     "extras": "Any extras? You can say 'none'.",
#     "name": "Perfect! What name should I put on the order?"
# }


# def normalize_extras(x: str):
#     x = x.lower().strip()
#     if x in ["no", "none", "nothing"]:
#         return []
#     return [p.strip() for p in x.replace("and", ",").split(",")]


# def save_order(order: dict):
#     ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
#     filepath = os.path.join(ORDERS_DIR, f"order_{ts}.json")

#     print("🔥 Saving order JSON to:", filepath)

#     with open(filepath, "w") as f:
#         json.dump(order, f, indent=2)

#     with open(os.path.join(ORDERS_DIR, "latest.json"), "w") as f:
#         json.dump(order, f, indent=2)


# # =======================================
# #        BARISTA ASSISTANT
# # =======================================

# class Assistant(Agent):
#     def __init__(self):
#         super().__init__(
#             instructions="""
#             You are JavaJoy — a friendly coffee shop barista.
#             Take orders step-by-step.
#             Required fields: drinkType, size, milk, extras, name.
#             Ask one question at a time.
#             Be friendly, short and simple.
#             When order is done: confirm politely. Do NOT mention JSON.
#             """,
#         )
#         self.order_state = {}
#         self.waiting_for = None

#     async def handle_barista(self, text: str) -> str:
#         clean = text.strip().lower()

#         # If answering a previous question
#         if self.waiting_for:
#             field = self.waiting_for

#             if field == "extras":
#                 self.order_state["extras"] = normalize_extras(clean)
#             else:
#                 self.order_state[field] = text.strip()

#             print("🔥 Current order state:", self.order_state)

#             self.waiting_for = None

#         # Ask next missing field
#         for field, question in ORDER_FIELDS.items():
#             if field not in self.order_state or not self.order_state[field]:
#                 self.waiting_for = field
#                 return question

#         # Order done → save it
#         order = self.order_state.copy()
#         order["timestamp"] = datetime.utcnow().isoformat()
#         save_order(order)

#         drink = order["drinkType"]
#         size = order["size"]
#         milk = order["milk"]
#         extras = ", ".join(order["extras"]) if order["extras"] else "no extras"
#         name = order["name"]

#         # Reset for next customer
#         self.order_state = {}
#         self.waiting_for = None

#         return f"Thanks {name}! Your {size} {drink} with {milk} milk and {extras} is placed."


# # =======================================
# #            ENTRYPOINT
# # =======================================

# def prewarm(proc: JobProcess):
#     proc.userdata["vad"] = silero.VAD.load()


# async def entrypoint(ctx: JobContext):
#     ctx.log_context_fields = {"room": ctx.room.name}

#     session = AgentSession(
#         stt=deepgram.STT(model="nova-3"),
#         llm=google.LLM(model="gemini-2.5-flash"),
#         tts=murf.TTS(
#             voice="en-US-matthew",
#             style="Conversation"
#         ),
#         turn_detection=MultilingualModel(),
#         vad=ctx.proc.userdata["vad"],
#         preemptive_generation=True,
#     )

#     usage_collector = metrics.UsageCollector()

#     @session.on("metrics_collected")
#     def _on_metrics(ev: MetricsCollectedEvent):
#         metrics.log_metrics(ev.metrics)
#         usage_collector.collect(ev.metrics)

#     async def log_usage():
#         logger.info(f"Usage: {usage_collector.get_summary()}")

#     ctx.add_shutdown_callback(log_usage)

#     assistant = Assistant()

#     await session.start(
#         agent=assistant,
#         room=ctx.room,
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     # Connect barista logic to messages
#     @session.on("user_message")
#     async def handle(ev):
#         reply = await assistant.handle_barista(ev.text)
#         await session.send_text(reply)

#     await ctx.connect()


# if __name__ == "__main__":
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))




import logging
# add near top of file (adjust import path if needed)
from tools.coffee_tool import update_order, finalize_order, get_missing_field 

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    # function_tool,
    # RunContext
)
from livekit.agents import function_tool, RunContext
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")




class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are BrewBuddy, a friendly coffee shop barista.

Start every conversation by introducing yourself:
"Hi, I am BrewBuddy, your barista."

Your job is to collect a complete coffee order with these fields:
- drinkType
- size
- milk
- extras
- name

Ask questions in this exact order:
1) "What drink would you like?"
2) "What size would you like? Small, medium, or large?"
3) "What type of milk would you prefer?"
4) "Any extras? Caramel, whipped cream, sugar, extra shot, or none?"
5) "What name should I save the order under?"

RULES:
- When the user gives an answer, emit EXACTLY:
  CALL_TOOL updateOrder {"field":"<fieldName>","value":"<value>"}

- When ALL fields are filled, emit EXACTLY:
  CALL_TOOL finalizeOrder {}

AFTER finalizeOrder:
You MUST say:
"Great! Your order is saved. Have a nice day."

Do not skip this final confirmation.
Do not use emojis or special characters.
Keep responses short and friendly.


""",
        )

    # Coffee Order Tools

    @function_tool
    async def updateOrder(self, ctx: RunContext, field: str, value: str):
        """Update a specific field of the coffee order."""
        return update_order(field, value)

    @function_tool
    async def finalizeOrder(self, ctx: RunContext):
        """Finalize and save the coffee order as a JSON file."""
        return finalize_order()



def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))