# The Great Territory — World Atlas (Map Foundation)

**Build:** v2.6-map (the map-first stage before v2.6 Roads & Consequences)  
**Current territory:** **60,000 × 40,960 world units**  
**Previous territory:** 19,200 × 12,800  
**Area growth:** **exactly 10×** (3.125× wider and 3.2× taller)  
**Source of geography:** `frontier_world.py`; source of existing towns and side jobs: `frontier_expansion.py`.

This is the stable *physical layout* to use for the upcoming road encounters, settlement improvements, music/audio regions, and questlines. It is not a claim that the entire playable area has hand-authored stories or buildings.

## Territory sectors

The map is divided into six columns and four rows; each named sector spans 10,000 × 10,240 world units. The southwest of the *original* game world remains in the top-left corner. Coordinates increase eastward and southward.

| North-to-south band | Western 1 | 2 | 3 | 4 | 5 | Eastern 6 |
|---|---|---|---|---|---|---|
| 0–10,240 | The Old Frontier | Rustbelt Plains | Thornwood | Black Mesa | Saltwind Basin | Northern Range |
| 10,240–20,480 | The Borderlands | Broken Prairie | Oxhead Gulch | Whisper Hills | Deadwater Flats | Far Lanterns |
| 20,480–30,720 | Sunbleached Trail | Prairie Sea | Copper Divide | Redstone Maze | Blueglass Country | Distant Run |
| 30,720–40,960 | South Marches | Three Forks | Fallen Timber | Devil's Reach | Ashfall Desert | Last Horizon |

Biomes use lightweight, deterministic terrain coloring/props: grassland, prairie, desert, scrub, forest, mesas, canyon, salt, lakes, and mountains. The exact sector labels and centers are intentional; future expansion should not arbitrarily relocate them.

## Settlements preserved from previous builds

- Cinder Creek (original Sheriff Bell story hub and the hand-authored map), with Dust Hollow, Sagebrush Crossing, Blackspur, Silverwater and Copper Ridge, all unchanged in local coordinates.
- Drybone Junction at (6,000, 4,300)
- Ironwell at (10,200, 4,300)
- Painted Mesa at (14,400, 4,300)
- Saltwater Crossing at (6,000, 7,900)
- Ember Gulch at (10,200, 7,900)
- Sundown Station at (14,400, 7,900)

The existing hand-painted world image remains **4,800 × 3,200**. It is composited over the camera-local procedural land only when on screen. We do **not** scale it up or convert the huge whole territory into a giant PNG.

## 22 discoverable wilderness landmarks

| Region | Landmarks |
|---|---|
| Far northern and northeastern trails | Rustwatch Tower, White Stag Grove, Black Spire, Salt Bell Flats, North Pass |
| Borderlands | Deadman's Mill, Oxhead Fossil, Stillwater Falls, Broken Dam, Last Lantern Post |
| Mid-territory | Mirage Well, Twin Pines, Copper Gate, Devil's Stair, Blueglass Shore, Far Station |
| Southern trails | Coyote Crossing, Three Forks, Timberfall, Red Obelisk, Ash Garden, Horizon Gates |

Landmarks each use camera-local vector sprites, a unique map position, a discoverable name, and saved discovery flags. These sites serve as stable locations for future stories and encounters.

## 13 resting waystations

West Ridge Post, Juniper Gate, Flintwater Depot, Bitter Salt Wells, Northern Spur, Long Prairie Camp, Copper Relay, Hollowstone Post, Blueglass Ferry, Three Forks Station, Timber Lodge, Ashfall Outpost, and Horizon Rest.

The smaller waystations provide a recognizable local sign/tent/water trough/campfire and **T** rest while on foot. They are protected against ambient bandit aggression, and each rest stop is usable once per save just like the existing town camps. They are **not yet** full shops, saloons, or NPC towns.

## Roads and navigation

- North–south tracks at x = 6,000, 10,200, 14,400, etc., as far as the eastern edge.
- East–west tracks at y = 4,300, 7,900, 11,500, etc., as far as the southern edge.
- A connector joins the original starting area to the first trade-road intersection. Collision checks recognize the tracks and suppress random rock/cactus obstruction on them.
- These routes will support escort and wagon pathfinding in v2.6; visual route art is already included.

**M:** Toggle full territory atlas. **Z:** Toggle region zoom centered on Jesse. **WASD / arrow keys:** Pan the regional map. **Click:** Set a navigational waypoint accurately in full or zoomed mode. **Escape or M:** Close.

The tiny lower-right minimap is now a **local trail radar**, not a compressed image of the entire territory. It shows nearby roads, settlements, stations, enemies, landmarks, objectives, and the player within a 6,400 × 5,600 unit window.

## Engineering rules for further development

1. Keep `WORLD_WIDTH`, `WORLD_HEIGHT`, named sector geometry, road anchors, and landmark coordinates stable unless intentionally redesigning the map.
2. Render **only visible** terrain cells and nearby landmarks, stations, buildings and NPCs. Never generate an uncompressed 60,000 × 40,960 image in RAM.
3. Use the same deterministic terrain/obstacle logic for collision and artwork. Don't place mission enemies inside obstacles.
4. Keep story/NPC/quest locations in the original area. New missions can be placed in outer sectors to populate empty travel routes.
5. Sound/music integration can switch by biome, weather, time and proximity to settlements using region names and music states.
6. Remain on Python/Tkinter without new heavy dependencies; retain CI testing under Xvfb. Performance on the user's specific Archcraft Intel machine still requires optional local verification.

## Verification

Run `xvfb-run -a python3 tests/great_territory_test.py` or run the GitHub Actions suite. The regression checks geography, 10× area growth, core story locations, collision, distant corners, view limits, map coordinate roundtrips, camp rest and discoverable landmark saves.

## Artwork reference

The screenshot supplied during map finalization is the **existing Dust Hollow game viewport** (with in-game HUD and desktop UI visible), not a clean world atlas. It serves as a reference for the minimalist sunbaked top-down Western art style; importing the screenshot itself as terrain would paint the HUD and desktop into the world.
