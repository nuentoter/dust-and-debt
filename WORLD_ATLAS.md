# Dust & Debt — The Frontier Lands of New Austellia (1898)

**Source of truth:** The *illustrated map supplied by the game creator*, titled “The Frontier Lands of New Austellia”. It is a real parchment atlas, **not a screenshot of the game**. All named geography here is traced from that reference.

**Playable world dimensions:** 60,000 × 40,960 world units, retaining the requested 10× area expansion. The pictured map was 1448 × 1086 pixels; all atlas coordinates are translated linearly to the playable world:

`world_x = atlas_x × 60,000 / 1448` and `world_y = atlas_y × 40,960 / 1086`.

The Python module [new_austellia.py](new_austellia.py) owns these authoritative locations and route polylines. In-game atlas view, navigational pins, coastal water, rivers, town sprites and railroad track visuals use the same coordinates. Only nearby terrain and landmarks are drawn during gameplay.

## Named geographical regions

| North | Center | South |
|---|---|---|
| Glacier Peaks | Heartland Plains | Copper Sands Desert |
| Graystone Range | Everwood Forest | Red Mesa Buttes |
| Cinder Ridge Badlands | Cedarheart Woods | Cypress Bayou |
| Northridge Territory | Sablestone Territory | Auburn Gulf |
| Iron Mesa | Red Thorn Canyon | Sundown Plateau |

These are irregular geographic areas approximated by distance to source-map regional anchors, not the discarded 4 × 6 fictional checkerboard. Biomes include mountain, forest, prairie/grassland, dry mesas, canyon, desert, water country and scrub.

## Major towns and illustrated destinations

**Central and northern routes:** Galloway, Saint's Hollow, Roan Creek, Hollow Bend, Blackwater Crossing, Larkfield, Pineheart Trading Post, Elmshade.

**Southern routes and seaboard:** Harper's Landing, Valleyford, Dustwell, Riversend, Saint Brigid's Port, Bayou Haven.

**Camps, mines, landmarks, forts:** Cinder Ridge Mining Camp, Silvervein Mine, Iron Mesa Fort, Stonewall Fort, Brimstone Point, Bearclaw Lookout, Mercy Flats Ranch, Prairie View Ranch, Black Rock Ranch, Rattler's Rest, Old Kestrel Mill, Widow's Pass, Lone Pine Mine, Driftwood Springs, Highfalls.

**Geography:** Frostvein Lake, Northstar Lake, Sable River, Blackwater River, Roan Creek, Riversend Channel, Dustwell Wash, Cypress Bayou, Auburn Gulf, Calhoun Island, Heron's Key, Drake Isles.

The coordinates of these destinations have been traced from the atlas rather than distributed arbitrarily throughout a square grid.

## Roads, railway and water

The illustrated railroad is a branched network through **Galloway, Saint's Hollow, Roan Creek, Blackwater Crossing, Larkfield, Harper's Landing, Valleyford, Dustwell, Riversend and Saint Brigid's Port**. Secondary wagon roads link mining camps, forts and trading posts. The original old-world approach road is retained only in its limited starting province so legacy opening missions still work.

The named rivers and lakes visibly exist in the top-down world and act as geographical obstacles. **Crossings now use actual intersections between the traced river channels and railway/wagon-road segments**, rather than making every road that touches water an unrestricted ford. Planked bridge decks and timber guard rails are drawn at these sites. The Gulf has a traced coastline, beach trim, and nearby visible islands. Port locations have raised docks; open water remains impassable. The original Cinder Creek map edge now has a lightweight dust-feather transition.

Routes and boundaries are approximations of the illustration, not survey-grade hydrology. Bridge behavior is determined by explicit route/river segment intersections; specialized ferry and boat navigation remain future work.

## Relocated existing gameplay settlements

The existing six extra towns and their six side quests have been relocated to named sites on this map, rather than being abandoned:

| Existing gameplay location ID | New Austellia location |
|---|---|
| drybone | Galloway |
| ironwell | Iron Mesa |
| painted | Dustwell |
| saltwater | Roan Creek |
| ember | Larkfield |
| sundown | Riversend |

Their guides, schedules, resource gathering, camps, shop buildings, clinics and objective points remain functional. The **original Cinder Creek game zone** remains at its old starting coordinates to preserve Sheriff Bell, Dust Hollow, Blackspur and the original story missions. It represents the inherited western playable area rather than a separate city on the New Austellia atlas.

The 13 waystations in v2.6 are now based on actual New Austellia transport hubs; the dispatcher/escort system uses their new positions. All future v2.7 content should use the New Austellia coordinates rather than the discarded temporary geography.

## Map artwork

The game supports an optimized PNG of the actual illustrated atlas at:

```text
assets/new_austellia_map.png
```

The expected dimensions are **610 × 457 pixels** (matching the built-in full-map rectangle). The user's original image was 1448 × 1086; the image can be resized once using Pillow, ImageMagick or ffmpeg, then copied under that path. If the artwork file is unavailable, the built-in vector atlas displays the same named places, rivers, lakes, railroads and region colors. **The source PNG is not yet stored as a binary asset in GitHub**, so this file is optional until it is distributed. The main world and route mechanics do not depend on it.

With the source PNG available locally, a conversion command is:

```bash
ffmpeg -i "Vintage Map of the Frontier Lands.png" -vf scale=610:457 -frames:v 1 assets/new_austellia_map.png
```

The genuine artwork appears in the map overview; regional zoom renders the vector atlas for correct pan and coordinate labels.

## Controls and testing

**M** shows the atlas; **Z** toggles regional zoom; **WASD / arrows** pan; **click** places a waypoint; **M/Escape** closes. The map click coordinates are projected through the same source as the land and towns.

Run `xvfb-run -a python3 tests/new_austellia_test.py` and the full GitHub Actions suite for map coordinates, coasts, bridge safety, new town locations, atlas rendering, mission compatibility and saves.

**Save compatibility:** Earlier development-format saves are not guaranteed to load with every location/state fully correct, at the owner's request; start a new game after any intentional geographical reset if behavior is inconsistent.
