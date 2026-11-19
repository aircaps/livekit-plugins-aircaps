# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-19

### Added

- `aircaps.STT`: streaming speech-to-text with AirCaps Live 1 (`aircaps-live-1`) for LiveKit Agents. Interim
  transcripts while the user speaks; a final transcript per turn when the stream is flushed (`manual_flush`), or when
  the model detects the end of the turn (`end_of_turn=True`, with `end_of_turn_mode` and single-value overrides).
- Start/end-of-speech events around each worded turn, recognition usage events, and `update_options()` for open
  streams.
- Endpoint lookup before each session; reconnection with a new lookup when a session drops or ends; a turn cut short
  by a dropped session ends with its text so far; refused keys, models and options are not retried.
- Audio paced to real time, and at most the newest 1.25 s of audio that queued while a session connected is sent.
- Keepalive pings while no audio is sent.
- Example voice agent `examples/agent.py`.
- Tests against a local fake of the AirCaps API.

Tested with LiveKit Agents 1.8.13.

[Unreleased]: https://github.com/aircaps/livekit-plugins-aircaps/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/aircaps/livekit-plugins-aircaps/releases/tag/v0.1.0
