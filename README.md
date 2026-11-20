# livekit-plugins-aircaps

[![PyPI](https://img.shields.io/pypi/v/livekit-plugins-aircaps)](https://pypi.org/project/livekit-plugins-aircaps/)
[![CI](https://github.com/aircaps/livekit-plugins-aircaps/actions/workflows/ci.yml/badge.svg)](https://github.com/aircaps/livekit-plugins-aircaps/actions/workflows/ci.yml)

[AirCaps AI](https://aircaps.ai) speech-to-text for [LiveKit Agents](https://github.com/livekit/agents).

`aircaps.STT` streams the user's audio to **AirCaps Live 1** (`aircaps-live-1`), a low-latency real-time English
speech-to-text model built for voice agents. It sends interim transcripts while the user speaks and the turn's final
transcript the moment the turn ends: when LiveKit's turn handling says so, or, with `end_of_turn=True`, when the model
detects it.

Maintained by AirCaps AI, the company that provides AirCaps Live 1.

## Installation

```bash
pip install livekit-plugins-aircaps
```

or `uv add livekit-plugins-aircaps`.

## Prerequisites

An AirCaps AI API key: sign in to the [AirCaps AI Console](https://console.aircaps.ai), open **API keys** and create one.
AirCaps Live 1 is available to every account, one session at a time by default
([talk to us](https://aircaps.ai/contact) for more). The [AirCaps Live 1 guide](https://aircaps.ai/docs/guides/live-1)
describes the model and its protocol.

```bash
export AIRCAPS_API_KEY=...
```

## Usage

By default the session's own turn handling decides when the user has finished speaking. LiveKit flushes the stream
at the end of each turn (from its VAD or turn detector, or a manual commit), and the final transcript comes back right
away:

```python
from livekit.agents import AgentSession
from livekit.plugins import aircaps, silero

session = AgentSession(
    stt=aircaps.STT(),
    vad=silero.VAD.load(),
    # ... llm, tts, turn_handling, etc.
)
```

Without a flush, words stay interim until the stream ends, so use a VAD (or a turn detector) in this mode.

### Model-detected end of turn

To let the model detect the end of each turn instead, turn on `end_of_turn` and use the STT's turn detection. The
model's end of turn has already waited out the user's pause, so set LiveKit's own endpointing delay to 0 (its default
adds 0.5 s to every turn):

```python
from livekit.agents import AgentSession, TurnHandlingOptions
from livekit.plugins import aircaps

session = AgentSession(
    stt=aircaps.STT(end_of_turn=True, end_of_turn_mode="balanced"),
    turn_handling=TurnHandlingOptions(turn_detection="stt", endpointing={"min_delay": 0}),
    # ... llm, tts, vad, etc.
)
```

### Options

| Option | Default | |
| --- | --- | --- |
| `model` | `"aircaps-live-1"` | The AirCaps AI model |
| `end_of_turn` | `False` | Let the model detect the end of each turn |
| `end_of_turn_mode` | `"balanced"` | `"min_latency"`, `"balanced"` or `"max_accuracy"`. A mode sets the values below; any of them given beside it overrides that one |
| `end_of_turn_threshold` | the mode's | How sure the model must be that the turn ended, 0.2 to 0.9 |
| `min_turn_silence_ms` | the mode's | The shortest pause that can end a turn, 0 to 1000 ms |
| `max_turn_silence_ms` | the mode's | A pause this long always ends the turn, 500 to 5000 ms, or 0 for no limit |
| `vad_threshold` | the mode's | How sure the model's voice detector must be that a sound is speech, 0.3 to 0.9 |
| `api_key` | `AIRCAPS_API_KEY` | AirCaps AI API key |
| `base_url` | `"https://api.aircaps.com"` | AirCaps AI API address |
| `http_session` | LiveKit's shared session | An `aiohttp.ClientSession` to use |

`stt.update_options(...)` changes the end-of-turn settings, also for streams already open.

Audio is resampled to 16 kHz mono. The model transcribes English and supports streaming recognition only; key terms
and speaker labels are not available.

How it works:

- Before each session the plugin asks the AirCaps AI API where to connect
  (`GET /v1/realtime/endpoint?model=aircaps-live-1`), then opens that WebSocket, so audio goes to the nearest server.
- A flush sends `finalize`; the turn's final transcript comes straight back.
- A dropped or ended session (sessions last up to an hour) is reopened, with a new address lookup. A turn cut short by
  the drop ends with its text so far.

## Running the example

[`examples/agent.py`](examples/agent.py) is LiveKit's basic voice agent with AirCaps AI as its speech-to-text (the LLM
and the voice come from LiveKit Inference).

```bash
git clone https://github.com/aircaps/livekit-plugins-aircaps.git
cd livekit-plugins-aircaps
cp .env.example .env      # add AIRCAPS_API_KEY and your LiveKit project's URL, key and secret
uv sync --extra example
uv run examples/agent.py console
```

`console` runs the agent in your terminal with your microphone and speakers; `dev` connects it to your LiveKit
project. `AIRCAPS_END_OF_TURN=1` switches it to model-detected end of turn.

## Tests

```bash
uv sync
uv run pytest
```

The tests run against a local fake of the AirCaps AI API; no key is needed.

## Compatibility

Tested with LiveKit Agents 1.8.13, on Python 3.10 to 3.13.

## Support

Open an [issue](https://github.com/aircaps/livekit-plugins-aircaps/issues), or [contact AirCaps AI](https://aircaps.ai/contact).

## License

Apache 2.0, see [LICENSE](LICENSE).
