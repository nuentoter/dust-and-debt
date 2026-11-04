# Dust & Debt 2.0 — Complete Frontier

**Release:** 2.0 (source release)
**Runtime:** Python 3, Tkinter/Tk 8.6 and a Linux X11 desktop. No pip dependencies.
**Target:** lightweight, low-spec Linux computers.

## Highlights

- Original four-job Western campaign with horseback travel, shops, interior scenes, wanted level, honor, and persistent progression.
- Dead Eye slow-motion combat and improved gunfighter movement, hit feedback, bullet cover, and adjusted damage.
- 19,200 × 12,800 explorable world area (16× the original map area), preserving the handcrafted starting territory.
- Procedural outer terrain and roadside hazards, with rocks, cacti and visible road corridors.
- NPC routines, conversations based on time and reputation, and varied townsfolk.
- Repeatable named bounty targets and occasional roadside assistance encounters.
- Clickable full-world map pins, minimap navigation, time/region weather visuals, and improved interior detail.
- Optional system-bell feedback (V, off by default; depends on desktop sound configuration).

## 2.0 stability and performance changes

- Autosaves occur approximately every **90 seconds of active game time**, including while indoors, instead of every 300 rendered frames. Manual F5 and quit-save remain available.
- Save files are atomically replaced. A valid previous save is kept in `save.json.bak` when possible. If the primary save cannot be read, Continue attempts the backup. If both are invalid, the game stays on the title screen rather than silently replacing saved progress.
- AI outside roughly 1,200 map units from the player is dormant, reducing idle simulation work; distant wildlife and civilians resume when approached.
- The renderer sorts/draws only actors in the visible camera area.
- Earlier save files are supported, with optional fields defaulting to safe values.

## Install or update

Clone the repository or update an existing checkout:

```bash
git clone https://github.com/nuentoter/dust-and-debt.git
cd dust-and-debt
./Play_Dust_and_Debt.sh
```

Existing checkout:

```bash
cd ~/dust-and-debt-github
git pull origin main
./Play_Dust_and_Debt.sh
```

**Back up your saves** before a major update:

```bash
cp ~/.local/share/dust-and-debt/save.json ~/dust-and-debt-save-backup.json
```

Save location: `~/.local/share/dust-and-debt/save.json`.

## Controls

| Key | Action |
|---|---|
| WASD / Arrow keys | Move |
| Shift | Sprint / gallop |
| Mouse / left click | Aim / fire |
| Space | Fire in facing direction |
| Q | Dead Eye |
| R | Reload |
| H | Mount / dismount |
| E / Shift+E | Speak / interact / enter |
| M | Open territory map; click inside to set pin |
| C | Clear map pin |
| J | Journal and active bounty |
| B | Bounty board near Sheriff Bell; shop interaction indoors |
| V | Toggle optional system-bell audio |
| F5 | Save |
| F1 | Help |
| Esc | Pause / leave interior |
| L on title screen | Continue from save |

## Verification

The Linux GitHub Actions suite runs the game's built-in self-test plus smoke/regression tests for saves, dialogue, town routines, gunfights, terrain, bounties, waypoints, interiors, weather, and story progression. Successful CI does **not** guarantee full playthrough coverage or performance on every Linux desktop. No user Archcraft playtest was carried out for this version at release time.

## Known limitations

- The 16× expansion is mostly procedurally generated wilderness, not a 16× increase in hand-built settlements and quests.
- Interior scenes and sound effects are intentionally lightweight; the sound feature uses the Linux desktop bell rather than recorded audio.
- There is no graphical installer or packaged binary; run from the Python source checkout.
- Some world systems are intentionally simple. Full mission playthrough, visual polish, and game balance can still benefit from real-device testing.

## Development

See [the milestone roadmap](https://github.com/nuentoter/dust-and-debt/issues/2). Both this repository and A Western Tale remain separate projects.
