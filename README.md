# DUST & DEBT
### A complete, original top-down Western adventure for Linux

**1889.** Ride your horse Whiskey into Cinder Creek. Sheriff Bell has a job, the railroad is hiding a conspiracy, and an outlaw named Crow controls the desert. Finish **four connected story jobs** to earn your freedom, then continue playing in free roam.

Features include a 4,800×3,200 scrolling handcrafted Western map, 27 buildings, multiple frontier settlements with interactive characters, horseback riding, 6-shot revolver gunplay, reloading, bandit combat, money and shops, a doctor and saloon, enemy pursuit, a wanted system, wildlife, a day/night cycle, an objective marker, a map and journal, health tonics, save/load, story ending and free roam.

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
