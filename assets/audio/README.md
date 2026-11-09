# Audio assets and upcoming soundtrack

This directory prepares the future sound/music milestone. **No recorded audio
or original music is bundled yet.** The game currently uses a lightweight
system-bell fallback for optional effects.

Suggested layout for future original or appropriately licensed material:

- `sfx/` — mono WAV/OGG cues: gunshot, reload, lasso, hogtie, steps,
  horse, shop, bounty, rain, thunder.
- `music/` — loopable original OGG tracks: title, town, wilderness,
  night, combat, interior.
- `manifest.json` — cue IDs, file paths, license/attribution,
  approximate loudness, and loop points.

The `audio_system.py` interface already defines semantic cues, music states,
volume settings, and a playback backend boundary. A later milestone should:
select and integrate a Linux-compatible backend, implement overlapping SFX,
stream music rather than loading large assets, crossfade scenes, respect mute,
and avoid failing startup when there is no audio device. Any sound used must
be original or licensed for distribution.

Avoid adding third-party recordings to the repository before license review.
