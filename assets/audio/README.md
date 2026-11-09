# Dust & Debt sound and music (v2.6)

**Actual audio playback is now available, but optional.** The code works
silently without an audio player. It plays through `ffplay` (preferred) or
`mpv` when one is installed and available on `PATH`. Otherwise **V** uses the
original Tk system bell as a small fallback.

On Archcraft/Arch Linux, one optional command is:

```bash
sudo pacman -S ffmpeg
```

This provides `ffplay`. The game does not install packages automatically.

## Controls

- **V** — toggle game sound effects (off by default).
- **O** — toggle background music/ambience (off by default).
- Enable **O** on the title screen to hear a supplied title theme.
- Preferences are saved with the game. No audio file or device is required to start.

## Sounds bundled as code (not recordings)

`audio_assets.py` lazily creates small, **original synthesized WAV samples**
the first time they are needed. These include gunfire, reloading, rope movement,
hogtie, horse, door, purchases and positive completion cues, and five atmospheric
sound beds for town, wilderness, night, interior and combat. They are intentionally
low-key temporary effects. They are **not realistic recorded SFX** and the beds
are **not a replacement for the game's bespoke title song**.

WAV files are generated only in `~/.cache/dust-and-debt/audio/` to keep the Git
repository small and the game dependency-light. Music loops using an external,
isolated player process; scene changes stop the previous loop. The game does not
wait for or depend on these processes to run. Volume settings are stored in the
audio director and apply when a new clip begins.

## Adding the intended opening theme

The user-created composition **“Forsaken to This Land”** is the intended
cinematic/title theme. Its audio data is **not in this repository yet**. To
connect the actual previously composed track, copy the authorized recording to

```text
assets/audio/music/title.m4a
```

or `title.ogg`, `title.mp3` or `title.wav`. This title recording overrides
any generated fallback. No recreated MIDI/theme approximation is substituted.

You can also put original or properly licensed background tracks in

```text
assets/audio/music/town.ogg
assets/audio/music/wilderness.ogg
assets/audio/music/night.ogg
assets/audio/music/combat.ogg
assets/audio/music/interior.ogg
```

Real audio files at these paths take priority over procedurally generated beds.
Additional effects use the matching `assets/audio/sfx/<cue>.wav` names.
Do not add third-party sound recordings without checking distribution rights.

## Future polish

Properly recorded horse footsteps, gunshots, wind/rain, transitions, crossfades,
independent in-game volume controls and a verified packaged soundtrack still
need to be created. The v2.6 audio work proves playback and scene handling; it
is **not yet a finished professional audio mix**. See the Audio Sprint issue for
the remaining production tasks.
