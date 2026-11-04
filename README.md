# DUST & DEBT
### A complete, original top-down Western adventure for Linux

**1889.** Ride your horse Whiskey into Cinder Creek. Sheriff Bell has a job, the railroad is hiding a conspiracy, and an outlaw named Crow controls the desert. Finish **four connected story jobs** to earn your freedom, then continue playing in free roam.

Features include a 4,800×3,200 scrolling handcrafted Western map, 27 buildings, multiple frontier settlements with interactive characters, horseback riding, 6-shot revolver gunplay, reloading, bandit combat, money and shops, a doctor and saloon, enemy pursuit, a wanted system, wildlife, a day/night cycle, an objective marker, a map and journal, health tonics, save/load, story ending and free roam.

## Expanded Territory — Map Update

The world is now **4,800 × 3,200 pixels** (four times the original territory), with **27 enterable-area landmarks/building exteriors**, roads, river bridges, an extended railroad, and distinct biomes. Key locations:

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
| E | Talk to people / pick up evidence |
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
