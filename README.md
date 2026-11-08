# DUST & DEBT
### A complete, original top-down Western adventure for Linux

**1889.** Ride your horse Whiskey into Cinder Creek. Sheriff Bell has a job, the railroad is hiding a conspiracy, and an outlaw named Crow controls the desert. Finish **four connected story jobs** to earn your freedom, then continue playing in free roam.

Features include a 4,800×3,200 scrolling handcrafted Western map, 27 buildings, multiple frontier settlements with interactive characters, horseback riding, 6-shot revolver gunplay, reloading, bandit combat, money and shops, a doctor and saloon, enemy pursuit, a wanted system, wildlife, a day/night cycle, an objective marker, a map and journal, health tonics, save/load, story ending and free roam.

## v2.3 Frontier Justice — field arrests (November 2026)

The lasso now also works on **ordinary roaming bandits**, rather than only active named bounty targets. This is a repeatable, non-lethal arrest activity that fits alongside the existing dead-or-alive wanted posters.

- **Aim with the mouse and press L** to lasso a roaming bandit within about 235 world units, with a clear path.
- Dismount (**H**), approach, and press **G** within eight seconds to hogtie the bandit; **E** picks the prisoner up.
- Carry the prisoner on foot (slower) or ride them on Whiskey. Return to Sheriff Bell, dismount and press **E** to deliver the prisoner alive for **$24 and +2 honor**. The journal tracks completed field arrests.
- Hogtied and carried drifters persist across saves and reloads. An untied captive escapes when the rope timer expires; falling in combat releases your captive.
- You can only handle one field prisoner at a time. A named bounty already roped, tied or carried also blocks new lasso captures until that prisoner is delivered.
- Named bounty contracts retain their original dead/alive payouts and are still separate from field arrests. Story mission enemies are not included in the generic arrest system.

The existing Linux regression suite now includes `tests/field_arrest_test.py`, which covers lassoing, restraint, save/reload, horse transport, delivery and reward, escape timer, and compatibility with named bounty contracts.

## v2.2 Dead or Alive — lasso and bounty capture (November 2026)

All **five named bounty contracts** can now be collected **dead or alive**, with alive delivery paying **twice** the dead reward and granting an additional honor boost. Original dead bounty hunting still works. Your existing active bounty remains compatible with the new feature.

### Capture and delivery

1. Stand near Sheriff Bell (or a sheriff contact) and press **B** to accept the next wanted poster. The journal (**J**) displays the *dead* and *alive* payments and capture state.
2. Ride to the wanted target and aim the mouse at them. Press **L** to **throw the lasso** (range around 235 world units). The throw needs a clear line of sight. It has a brief cooldown and does not consume bullets.
3. A successful lasso holds the outlaw for **eight seconds**. Dismount (**H**), move within 76 units, and press **G** to **hogtie** them. If you wait too long, they break free and you must lasso them again.
4. Press **E** next to the hogtied prisoner to **pick them up**. You can carry the restrained outlaw on foot or ride them back on Whiskey. Carrying on foot reduces walking speed.
5. Return to the sheriff, dismount, and press **E** to hand over the captive and collect the larger **alive** reward. The map waypoint points back to Sheriff Bell once a prisoner is secured.

Shooting the wanted target remains a valid **dead** completion, paying the original listed amount. You can no longer receive both rewards for the same contract. Lassoing does **not** automatically count as a capture: the prisoner must be hogtied and physically brought in.

**Persistence:** New save data tracks whether an active bounty is free, roped, hogtied, or carried, including a tied captive's location and the remaining short rope timer. Earlier bounty saves without capture fields load as ordinary hunting contracts. Loading a save while a prisoner is carried lets you finish the delivery; no new game is necessary.

**Scope:** The lasso and hogtie system currently applies to **wanted bounty targets**, not random civilians or every roaming bandit. The rope is a simple rendered visual, not an animated physics simulation.

**Tests:** `xvfb-run -a python3 tests/bounty_capture_test.py` covers all five alive capture chains, payout, mounting, tied/carried save recovery, previous-version bounty saves, and rope escape. GitHub Actions runs this alongside the earlier story and combat regression suite.

## v2.1.2 — Dust Hollow mission spawn fix (November 2026)

- Corrected the five Dust Hollow mission rider spawn locations. One original position was **inside the Cabin building's collision rectangle**, trapping the enemy behind a bullet-blocking wall and preventing the five-rider quest from completing.
- All story mission riders and bosses now pass a walkable-spawn check before being created. A blocked candidate is moved to a nearby clear position.
- Fix also applies when **loading a save during an active mission**. Previously defeated mission riders stay defeated using the existing `stage_kills` save field. No new game is required.
- Regression test `tests/mission_spawn_test.py` verifies clear spawn positions, unobstructed shooting approaches, save/reload with four of five Dust Hollow riders defeated, continuation to the next mission, and safe spawns in later boss encounters.

**To resume a stuck mission:** press **F5** to save, quit to the desktop, pull the latest GitHub changes, relaunch the game, and press **L** at the title screen. The remaining rider respawns at a reachable position. If your last save predates some kills, those kills may need to be repeated.

## v2.1.1 Input and overlay fixes (November 2026)

- **E** now exclusively talks/interacts outdoors, even when an NPC stands beside a building entrance. In particular, talking to **Sheriff Bell** beside the jail no longer mistakenly enters the jail.
- **Shift+E** explicitly enters a nearby building when its entrance is within range. The X11 Shift event modifier and held Shift key are both recognized.
- Mounting Whiskey with **H** explicitly disengages Dead Eye. **Q** remains the dedicated Dead Eye toggle.
- Dust storms now show directional gusts rather than an all-screen yellow wash; Dead Eye retains its distinct sepia overlay, so these two effects no longer look identical.
- New automated regression test: `tests/input_fix_test.py`, covering the jail entrance, both interaction controls, horseback Dead Eye state, and weather rendering. No save migration is needed.

## v2.1 Frontier Reborn — major content expansion (November 2026)

This source update fills part of the large 19,200 × 12,800 wilderness with **six new named settlements**, residents, activities, and handcrafted two-stage side jobs. All original towns and the main four-job campaign remain.

### New frontier settlements

- **Drybone Junction** — messenger routes and missing mail
- **Ironwell** — ore surveys and a dangerous abandoned shaft
- **Painted Mesa** — scouts and missing trail markers
- **Saltwater Crossing** — lost ferry supplies and medicine
- **Ember Gulch** — smuggling evidence
- **Sundown Station** — telegraph repair clues

Each settlement has a trading post, boarding house, clinic, named quest contact, merchant, medic, and three civilian residents. The new towns are placed near the existing road grid and are protected from ordinary bandit aggression. Town squares, buildings, signs, lanterns, hitching rails, water troughs, and camps are drawn using lightweight Tkinter primitives rather than enormous world textures.

### New side missions and activities

- **Six two-stage side jobs** — talk with a town's named guide (E), visit the two clue locations indicated on the map, and press **E** at each marked crate to progress. Each job pays a different reward, and all six can be completed in a single save. The journal (**J**) shows the current job and progress. Side-job rewards and completion flags persist.
- **Resource gathering** — find herb and ore markers near settlements and press **F** to collect. Herb sites give a health tonic; ore sites pay $9. There are 12 collectible nodes, and collected sites stay collected in the save.
- **Campfire rest** — press **T** near the center of a new settlement to recover 30 HP and advance six game hours. Each camp can be used once per save.
- **Exploration rewards** — entering a new settlement for the first time awards $5 in trail supplies, with discovery progress saved.
- **New civilian routines and local dialogue** — couriers, farmers and watchers follow differing daytime routes; townsfolk share local rumors and respond to honor and wanted status.
- **World navigation** — settlement markers, side-objective clues, resource markers and on-screen prompts appear in addition to existing story/bounty/waypoint markers.

### Compatibility and limitations

Existing saves load without migration; new activity progress is optional save data. All new scenes are part of the same low-dependency Python/Tkinter game. This update adds a sizable playable layer to the expanded world, **not** dozens of fully scripted main-story chapters, advanced indoor AI, or a complete hand-painted 16× tileset. Side jobs are exploration/recovery missions; bounty hunting remains the combat-focused repeatable activity.

Automated regression: `xvfb-run -a python3 tests/frontier_reborn_test.py`, included in GitHub Actions. Local Archcraft playtesting remains unverified.

## v2.0 Complete Frontier — source release (November 2026)

**The seven-milestone development roadmap is implemented.** This version introduces reliability and performance work over v1.9:

- Autosaves use a real-time 90-second game-time interval instead of a frame counter, including when indoors. F5 manual saves and quit-saves remain available.
- A recoverable `save.json.bak` is maintained when possible. Continue tries the backup if the primary save fails validation, and will not silently overwrite both broken saves with a fresh game.
- Distant actors go dormant beyond roughly 1,200 world units; actor drawing is culled to the current camera view.
- Includes new regression tests for save recovery, damaged saves, mission progression, autosave scheduling, and outer-world rendering.
- Existing saves, original towns and story coordinates, and the large procedurally generated territory are preserved.

Read the full [v2.0 release notes](RELEASE_NOTES_v2.0.md) for controls, source-based installation and known limitations. Automated Linux testing does not guarantee end-to-end playthrough completeness or performance on your particular Archcraft laptop.

## v1.9 World Polish (November 2026)

The map and interiors now have more detail, with low-cost procedural weather and an optional audio cue.

- **Navigation:** Press **M** for the full territory map and **click** anywhere inside the map to place a personal waypoint. The waypoint is shown on the full map and minimap, and a distance/direction indicator appears during play. Press **C** during outdoor gameplay to clear it. Active bounty targets are marked in maroon; the original mission target remains gold.
- **Weather:** Region- and game-time-dependent rain or dust overlays; clear weather remains common. Weather is procedural and requires no extra graphics or Python libraries.
- **Interiors:** Added distinctive thematic furnishings and color details to saloons, sheriff offices, doctors, stores, stations, hotels, cabins, stables, chapels and hideouts; counters and exits retain their original interaction positions.
- **Audio:** Press **V** to toggle a small number of optional system-bell cues, including gunshots and completed bounties. Audio is **off by default** and depends on the user's Linux desktop bell configuration; it is not a soundtrack or a full sample-based audio engine.
- **Compatibility:** Waypoints and sound preferences are optional save fields. Older saves and original quests remain compatible. No additional dependencies.
- **Testing:** `tests/world_polish_test.py` covers map interaction, waypoint persistence, weather, interiors and disabled audio. The existing Linux CI suite also runs every previous milestone's checks.

**Current scope:** Lightweight UI and atmosphere improvements, not a complete rebuild of the pixel art or a full sound engine. Archcraft-specific performance is not independently measured.

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
