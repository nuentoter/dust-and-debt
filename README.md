# DUST & DEBT
### A complete, original top-down Western adventure for Linux

**1889.** Ride your horse Whiskey into Cinder Creek. Sheriff Bell has a job, the railroad is hiding a conspiracy, and an outlaw named Crow controls the desert. Finish **four connected story jobs** to earn your freedom, then continue playing in free roam.

Features include a 4,800×3,200 scrolling handcrafted Western map, 27 buildings, multiple frontier settlements with interactive characters, horseback riding, 6-shot revolver gunplay, reloading, bandit combat, money and shops, a doctor and saloon, enemy pursuit, a wanted system, wildlife, a day/night cycle, an objective marker, a map and journal, health tonics, save/load, story ending and free roam.

## Three-milestone update — v1.6 to v1.8 (November 2026)

### v1.6 Better Gunfights
- Enemy gunfighters approach from a distance, back off if too close, and strafe at firing range instead of always charging.
- Shots are blocked by solid building and terrain cover; enemies need a clear sightline before firing.
- Hit markers, a short combat-warning border and Dead Eye damage improvement make gunfights more legible.
- Reduced enemy firing rate/damage and increased hit invulnerability for fairer combat.

### v1.7 Tile & Terrain Pass
- Procedural outer wilderness now draws separate ground markings and foreground cover props: rocks, cacti, grass and sun-baked cracks.
- Deterministic rock/cactus cover is solid for players, roaming NPCs, and bullets.
- Maintains passable frontier road corridors and bounded, camera-local terrain drawing for older GPUs.
- Original 4,800 × 3,200 area and handcrafted map artwork stay intact; this is a procedural terrain pass, not replacement of all artwork with a full tilemap engine.

### v1.8 Emergent Frontier
- **Bounty board:** Stand near Sheriff Bell or Deputy Grace outdoors and press **B** to accept a repeatable named bounty. The next target appears at a fixed location, and you receive its reward when defeated. Open **J** to see the contract. Five named jobs rotate; contract and completion count persist in saves.
- **Roadside help:** While exploring wilderness away from safe settlements, occasionally meet a stranded traveler. Walk close and press **E** to help; earn $12 and +1 honor.
- Random encounters do not replace story missions. Existing mission NPC coordinates, original stages, and save/load functionality are preserved.
- Added `tests/combat_test.py`, `tests/terrain_test.py`, and `tests/emergent_test.py`, all included in the Linux GitHub Actions smoke-test workflow.

**Known scope:** Bounty targets are lethal-only encounters for now (no capture mechanic). The expanded outer frontier remains mostly procedurally generated and will benefit from additional authored settlements and landmarks. Actual Archcraft playtesting remains optional and unverified for these three updates.

## Living Towns v1.5 (November 2026)

**Milestone 2: moving beyond stationary crowds.** Named civilian residents in Cinder Creek, Sagebrush Crossing, and the surrounding settlements now follow deterministic outdoor routines through four periods: morning (06:00–11:00), workday (11:00–17:00), evening (17:00–21:00) and night (21:00–06:00). Four new civilians inhabit Sagebrush Crossing, with individually named destinations and occupations.

- Civilians walk toward their daytime and evening destinations, then return home at night. They wait at destinations rather than drifting endlessly.
- Nearby civilian labels show what they're doing. Asking **Any news?** via **E**, then **1**, includes their current activity.
- Coffee and hotel sleep immediately refresh NPC schedules after the clock changes.
- Existing mission characters (Sheriff Bell, Nell, and service NPCs) remain fixed so original quest triggers are preserved.
- Saves from earlier game versions remain compatible. Schedules are computed from the saved clock and do not require save migration.
- Regression test: `xvfb-run -a python3 tests/living_towns_test.py`. This runs in GitHub Actions alongside the existing checks.

**Scope:** These are lightweight outdoor waypoint routines, not full indoor pathfinding or independent NPC inventories. Those are later improvements.

## Great Frontier hotfix v1.4.1 (November 2026)

This is a **playtest hotfix before Milestone 2**, responding to feedback that drifters attacked too quickly, saving was unclear, and the territory was too small.

- **16× total explorable area:** World bounds are now 19,200 × 12,800 (previously 4,800 × 3,200). All original towns, missions, and map art keep their positions. Outer regions are drawn from deterministic terrain cells only when visible, avoiding a 245-million-pixel world texture. These additional regions are currently wilderness/exploration zones, not densely authored new towns.
- **More forgiving opening:** random bandits cannot spawn within 950 px of the starting position or in protected towns. New games have 50 seconds of bandit protection, and loaded saves have 18 seconds. Ordinary drifters engage at closer range and won't start a firefight while you stand in a protected settlement. Mission enemies still defend their missions.
- **Reliable, visible save reporting:** Press **F5** during normal play, pause, or conversation. Saving performs an atomic disk write and reports a timestamp and exact file path, or a visible error if it fails. Pausing shows the latest save status. The save file remains at `~/.local/share/dust-and-debt/save.json`; the title screen's **L** key loads it.
- **Whole-territory map:** Press **M** to see the 16× region overview. The original hand-drawn map occupies the northwest portion, with procedural region labels outside it. Old saves remain loadable.
- **Regression tests:** `tests/frontier_hotfix_test.py` checks protected spawning, the expanded dimensions, disk save/reload, and rendering far out in the new frontier. GitHub Actions workflow is configured in `.github/workflows/linux-tests.yml`; check the repository Actions tab for execution results.

**Important:** No save migration or deletion is required. After pulling, verify F5 displays the saved file path, quit to the title screen, and press L to check that position and money are restored.

## Frontier Conversations v1.4 (November 2026)

**Milestone 1 of the sequential roadmap.** Talk to ordinary townsfolk with **E** and select one of three replies using **1**, **2**, or **3**; **Esc** exits the choice menu. You can ask for local news, ask how people view your reputation, or say goodbye. Greetings and reactions reflect your honor and wanted status. Story mission-giver dialogue is unchanged. The feature uses the existing Tkinter renderer and requires no new assets or dependencies.

Run the existing smoke test and new dialogue regression test in a virtual display:

```bash
xvfb-run -a python3 tests/smoke_test.py
xvfb-run -a python3 tests/dialogue_test.py
```

The dialogue implementation was tested in a Linux virtual display, but final Archcraft playtesting is still requested before Milestone 1 is marked complete.

## Outlaw Systems v1.3 (November 2026)

This release adapts gameplay ideas from **A Western Tale** (Godot) to Dust & Debt's lightweight Python/Tkinter engine, without requiring Godot or third-party Python libraries.

- **Dead Eye:** Press **Q** while outdoors to toggle slow motion. World actors and bullets move at 25% speed while you can continue moving and firing normally. Dead Eye consumes its 100-point meter at 25 per real-time second, regenerates after a short cooldown, and gains 12 points when you defeat an outlaw. The HUD displays the meter; Dead Eye adds a sepia tint, targeting line and aiming reticle. Press Q again to turn it off.
- **Honor:** 0–100 reputation score (starts at 50). Defeating outlaws raises honor slightly; assaults and murder lower it. Paying off a bounty restores a small amount. Civilians and Sheriff Bell react differently to your record.
- **Law enforcement:** Peace → Investigating → Wanted. Firing in town or attacking bystanders can attract witnesses and raise the wanted level. Deputies pursue when sufficiently wanted. Heat decays only while not actively pursued, and more slowly in town; paying off a bounty clears the status. Crimes and honor persist in saves.
- **Combat feedback:** Short-lived bullet trails, hit sparks, distinct Dead Eye aiming overlays and clearer crime notifications.
- **Layered scenery:** Deterministic foreground grass, scrub and rock details drawn over the existing world map. Existing coordinates, collision footprints and quest positions stay fixed. This is a *lightweight procedural overlay*, not a full tilemap engine conversion.
- **Existing games:** Older save files remain readable, with missing honor, crime and Dead Eye fields initialized to sensible defaults. Original missions and Living Frontier interiors are unchanged.

**Controls:** Q toggles Dead Eye. Use the mouse to aim and left-click to fire. R reloads. F1 shows the complete controls. Save with F5.

**Asset note:** A Western Tale contains some third-party assets with explicit CC0 license files, but this release does not import its third-party sprites or music. Those need an asset-by-asset provenance and visual compatibility review before reuse.

**Validation:** `python3 game.py --self-test` checks assets and core game definitions. For an automated graphical smoke check, run `xvfb-run -a python3 tests/smoke_test.py` (requires Xvfb). Final gameplay compatibility should be verified on your own Linux installation.

## Living Frontier v1.2 (November 2026)

**New in this update:**
- Explore **27 enterable buildings** across the existing 4,800 × 3,200 world. Doors are on the south-facing side: dismount, approach the middle of the building's south wall, and press **Shift+E** (or **E** when no NPC is close).
- Each building has its own procedurally rendered indoor room, including saloons, stores, sheriff's offices, doctors, stables, hotels, cabins and more.
- Walk indoors with **WASD** or arrow keys. Walk north to the counter and press **E** (or **B**) to open a shop, or south to the door and **E** to leave. **Esc** also leaves a room.
- Working **number-key shop menus**: buy ammunition, health tonics, supplies, meals, treatment, horse care, lodging, and pay off wanted bounties. Prices are deducted and items take effect immediately.
- Civilian NPCs now follow simple time-of-day outdoor routes between home, daytime and evening positions, while avoiding building footprints. Existing quest NPCs remain available at their original locations.
- Existing missions, combat and outdoor map coordinates are preserved. Saves are compatible with the earlier Expanded Frontier edition.
- Save while indoors with **F5**. Reloading starts outdoors near the building you entered.

**Scope note:** This release adds functional single-room interiors and basic NPC daily movement. It does not yet include elaborate multi-room buildings, sophisticated indoor NPC conversations, indoor combat or navigation pathfinding around distant obstacles.

## Expanded Territory — Map Update

The world is now **4,800 × 3,200 pixels** (four times the original territory), with **27 building exteriors with enterable interiors**, roads, river bridges, an extended railroad, and distinct biomes. Key locations:

- **Cinder Creek** — original town, sheriff, saloon, shops and story starting point
- **Dust Hollow** — outlaw camp to the northeast of Cinder Creek
- **Blackspur Outpost** — bandit territory near the original eastern railroad
- **Sagebrush Crossing** — new trading town, second saloon, sheriff annex and livery
- **Silverwater Lake** — lake, riverside forest, fishing shack and cabins
- **Copper Ridge** — mountain mining settlement, bunkhouse and assay office
- **High Mesa** — remote red-rock wilderness, watchtower and mesa camp
- **Southern Badlands** — old mission, ghost chapel, ranch country and smuggler shed

Press **M** for the complete territory map, including the player and mission markers. The lower-right minimap shows an overview of the entire territory. Newly discovered regions are announced as you travel. The original eight story stages and all original mission positions are preserved.

**Existing save files remain compatible:** saved coordinates and mission progress are unchanged. You can replace your old game folder and press L to continue. Saves are kept outside the game folder.

## Start the game

Unzip the game. Inside the folder open a terminal and run:

```bash
./Play_Dust_and_Debt.sh
```

Or:

```bash
python3 game.py
```

**Dependencies:** Python 3 and Tkinter (Tk 8.6). **No pygame, pip, Steam, internet or external downloads required** when Tkinter is already installed. The game comes with its original art assets. In Arch Linux / Archcraft, if Tkinter is missing: `sudo pacman -S python tk`.

The game opens a 960×600 window and targets modest older computers. Press **F11** for fullscreen.

## Controls

| Key | Action |
|---|---|
| W A S D / arrow keys | Move |
| Shift | Sprint / horse gallop |
| Mouse aim + left click | Fire revolver |
| Space | Fire towards mouse pointer |
| R | Reload six-round revolver |
| E | Talk, enter buildings if clear, use indoor counters and exits |
| Shift+E | Enter nearby building even when an NPC stands near its door |
| B | Open a shop while near an indoor counter |
| 1–4 | Select items in an indoor shop |
| H | Mount/dismount Whiskey when near him |
| 1 | Use health tonic |
| M | World map |
| J | Mission journal |
| F1 | Help |
| F5 | Save |
| F11 | Fullscreen |
| Esc | Pause |
| Enter | Next dialogue / confirm |

**Tip:** Speak with Sheriff Bell below the sheriff's office (northwest of the town). Your horse Whiskey is just southeast of your starting position. The objective marker is shown on the minimap; use **M** for a larger map.

**Important:** Shooting in town attracts the law. Keep a good supply of ammunition from Silas at the general store ($18 for 30 rounds), and visit the doctor if wounded ($15). Shooting bandits earns small bounties; story missions pay more.

## Saving

Saves automatically between missions and periodically, also with **F5** or when closing normally. Continue from the title screen by pressing **L**. Saves live at:

`~/.local/share/dust-and-debt/save.json`

## Credits

Original game design, narrative, code, and graphics made for this request. Inspired by classic frontier Westerns and retro overhead action games. No Red Dead Redemption graphics, characters, music, or proprietary assets are included. `build_assets.py` is an optional development-only art generator using Pillow; it is **not** required to play.

## Building the art (optional)

The expanded world and overview are already included. `expand_world.py` can regenerate them from `assets/world_original.png` using Pillow. Pillow is **not** needed to play.
