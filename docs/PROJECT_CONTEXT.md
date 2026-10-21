# manganarrator_tts: project context

Source review: 2026-10-21. Baseline commit: `97f1fe22a1310b3d4fa23d0e2e4669b794de19ae`.
For later sessions, compare relevant paths against that commit; avoid re-auditing unrelated services.

## Purpose and boundaries

Chatterbox speech service with speaker references, emotion settings, and versioned dialogue audio.

POST /tts/dialogue uses a manga-oriented image_ref and dialogue_id. GET /tts/emotions supplies emotion options. Story Studio initially imports audio; a future native story-segment endpoint must not invent image refs or bounding boxes.

## Code map

tts_server.py; app/tts_runner.py; app/backends/chatterbox_backend.py; app/services/tts_resolver.py; app/models/domain/; app/data_maps/speaker_map.yaml; app/data_maps/emotion_map.yaml

## Setup and checks

Use the existing Chatterbox/GPU environment and matching model dependencies. `python -m uvicorn tts_server:app --host 127.0.0.1 --port 8002` is an example port; match the frontend TTS API URL. Review config.yaml and voice_refs before startup. No checked-in automated test suite was found.

## Known details and gaps

Model loads in FastAPI lifespan. Speaker selection passes through resolve_speaker; preserve explicit speaker choices. Runtime voice files and GPU model availability were not exercised in the documentation pass. Keep this separate from the video service environment.

## Current state / next work

This note was grounded in source inspection at the baseline above. Runtime verification for this service is recorded below only when actually executed. Documentation-only edits do not establish that GPU inference, external APIs, or the complete distributed manga pipeline work in this environment.

For story production, first inspect [Story Studio in the video service](https://github.com/whenigetout/manganarrator_video/blob/main/docs/STORY_STUDIO.md). The first slice uses imported segment audio; OCR and Paddle are unchanged. Native story TTS is a later adapter, not an image-shaped workaround.

## Related repositories

[Central ecosystem map](https://github.com/whenigetout/manganarrator/blob/main/docs/ECOSYSTEM.md) owns service responsibilities and the cross-repo task routing table. Consult it only for work crossing a service boundary.
