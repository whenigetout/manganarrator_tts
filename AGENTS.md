# Agent entry point — manganarrator_tts

## Read only what the task needs

1. Read this file, then [project context](docs/PROJECT_CONTEXT.md).
2. Check `git status --short` and recent commits. The context doc records the review baseline; inspect changes to relevant paths since that baseline if needed.
3. Use the path map below to open only the affected modules, their contracts and relevant tests. Do not begin every session with a full-repository or eight-repository audit.
4. If a documented fact disagrees with code, verify the smallest relevant path and correct the note. Documentation is a map, not proof that runtime behavior works.

## Responsibility

Chatterbox speech service with speaker references, emotion settings, and versioned dialogue audio.

Start here: tts_server.py; app/tts_runner.py; app/backends/chatterbox_backend.py; app/services/tts_resolver.py; app/models/domain/; app/data_maps/speaker_map.yaml; app/data_maps/emotion_map.yaml.

## Working rules

- Preserve existing manga behavior and public API shapes. Keep novel/story models separate from OCR geometry.
- Prefer the smallest useful increment. Reuse the ecosystem's existing rendering, voice and media facilities.
- Keep user manuscripts, conversation exports, generated private story assets, credentials and tokens out of public source control. Use synthetic fixtures.
- The owner prefers coherent tested commits directly to `main`; follow the current task's authorization and branch protections. Never force-push over others' work.
- YouTube publishing, paid generation and sharing private content require the owner's explicit task authorization. Do not enable them as a test side effect.
- Report exactly which checks ran, passed, failed or were blocked. A syntax check is not an end-to-end test.

## Verification entry point

Use the existing Chatterbox/GPU environment and matching model dependencies. `python -m uvicorn tts_server:app --host 127.0.0.1 --port 8002` is an example port; match the frontend TTS API URL. Review config.yaml and voice_refs before startup. No checked-in automated test suite was found.

## End-of-task handoff

Update `docs/PROJECT_CONTEXT.md` when architecture, entry points, configuration or commands change. Keep its dated **Current state / next work** section short: implemented behavior, concrete gaps, commands actually run and relevant limitations. Record decisions with reasons; remove superseded facts. Do not append chat transcripts or an unbounded diary.

For cross-service changes, update affected repo notes and the [central ecosystem map](https://github.com/whenigetout/manganarrator/blob/main/docs/ECOSYSTEM.md). Leave unrelated repos alone. A new agent should be able to start from these notes and a targeted diff.
