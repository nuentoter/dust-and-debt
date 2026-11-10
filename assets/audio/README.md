# Dust & Debt — original recorded soundtrack

The creator has already composed/collected **twelve M4A recordings** for the game. The gameplay soundtrack uses those original files, **not a procedurally generated Western substitute**. The project Library contains their filenames, but the raw media data has not yet been added to this GitHub repository.

## Install actual recordings

Copy all original files into `assets/audio/music/` *with their current filenames*. Or use the idempotent installer, pointing at the folder where the original audio files live:

```bash
cd ~/dust-and-debt-github
python tools/install_soundtrack.py "$HOME/Music/Dust-and-Debt"
```

The installer prints which files were installed or missing and copies without changing audio encoding. If you only have the tracks in the ChatGPT Library, retrieve the M4As there first. Files must actually exist on disk for playback.

**Title:** `Forsaken to This Land.m4a` (the agreed original opening theme).

**Wilderness:** `Whistling the Frontier.m4a`, `Dust on Our Sleeves.m4a`, `Mournful Frontier Ballad.m4a`.

**Town:** `The Good.m4a`, `Sol de Harmonica.m4a`, `Mm-Hmm.m4a`.

**Night:** `Rainy Night Blues.m4a`, `Why Me.m4a`, `Mournful Hymn.m4a`.

**Interior:** `Sol de Harmonica.m4a`, `Mournful Hymn.m4a`.

**Combat:** `Blood Money Spends.m4a`.

**Unassigned:** `Untitled.m4a` is copied but deliberately not used until its intended role is known.

These assignments are provisional. Edit the Python tuple lists in `soundtrack_manifest.py` to change which music plays where. Playlists rotate when a track finishes. `title.m4a`, `town.m4a` etc. also work as direct scene overrides.

## Playback on Linux

Install a supported M4A-capable command-line player if necessary:

```bash
sudo pacman -S mpv
```

`ffplay` (FFmpeg) also works. `pw-play` / `aplay` only handle WAV music files and cannot decode these M4As unaided. The title screen displays the detected backend and number of installed recordings.

**O** toggles music (on by default for the new music update). **V** toggles effects. In-game **F8 → 5** toggles music, and your choice saves. Missing music tracks cause silence, never a generated replacement.

The earlier procedural WAV **sound effects** in `audio_assets.py` are separate and remain optional. Their bell fallback works even when music is unavailable.

## Distribution and polish

Only upload/distribute these M4As if you hold the necessary rights. The user-owned recordings have not yet been copied into GitHub by this assistant because the Library file entries could not be materialized as raw bytes in the current environment. Crossfades, volume sliders and real-device testing remain open in the audio sprint issue.
