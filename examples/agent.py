"""A voice agent that listens with AirCaps Live 1.

LiveKit's basic voice agent with AirCaps as its speech-to-text; the LLM and the voice come from LiveKit Inference.

    uv sync --extra example
    uv run examples/agent.py console      # talk to it in the terminal
    uv run examples/agent.py dev          # or join it from a LiveKit room

Set AIRCAPS_API_KEY, and LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET for your LiveKit project (in .env).
Set AIRCAPS_END_OF_TURN=1 to let the AirCaps model decide when each turn ends.
"""

import os

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
)
from livekit.plugins import aircaps, silero

load_dotenv()

END_OF_TURN = os.environ.get("AIRCAPS_END_OF_TURN") == "1"


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful assistant in a voice conversation. Keep your answers short, "
            "and do not use emojis, markdown or other formatting that cannot be spoken."
        )

    async def on_enter(self) -> None:
        self.session.generate_reply(instructions="Greet the user and offer your help.")


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession(
        stt=aircaps.STT(end_of_turn=END_OF_TURN),
        llm=inference.LLM("openai/gpt-4.1-mini"),
        tts=inference.TTS("cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        vad=silero.VAD.load(),
        # With AirCaps end of turn, the model's decision already includes the user's pause:
        # LiveKit adds no delay of its own.
        turn_handling=TurnHandlingOptions(turn_detection="stt", endpointing={"min_delay": 0})
        if END_OF_TURN
        else TurnHandlingOptions(turn_detection="vad"),
    )
    await session.start(agent=Assistant(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
