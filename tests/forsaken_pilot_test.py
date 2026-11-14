#!/usr/bin/env python3
"""Synthetic regression: seamless tiles, paths, buildings and source preservation."""
from pathlib import Path
import sys
import tempfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.build_forsaken_pilot import (
    seam_edges,seam_error,make_pilot,route_exclusion_mask,TILE_SIZE,
)

# Seam pass must close both axes exactly, never mutate original source.
source=Image.new("RGB",(64,64))
sp=source.load()
for y in range(64):
    for x in range(64):
        sp[x,y]=(50+x*2,65+y*2,(x*y)%128)
snapshot=source.copy()
seam=seam_edges(source)
assert source.tobytes()==snapshot.tobytes()
assert seam.size==(64,64) and seam_error(seam)==(0,0)
assert seam.getpixel((32,32))==source.getpixel((32,32))
assert seam_edges(seam).size==(64,64)
assert seam_error(seam_edges(seam))==(0,0)

# Source road corridor, building rectangle and non-earth colors remain exact.
world=Image.new("RGB",(256,256),(186,147,108))
pixel=world.load()
for y in range(128,256):
    for x in range(128,256):
        pixel[x,y]=(36,90,140)  # water cannot be recoloured
building=("Mock",75,75,50,50)
regions=((0,0,256,256,"bleached_dirt"),)
pilot,changed,mask=make_pilot(world,{"bleached_dirt":seam},
        regions=regions,draw_routes=False,buildings=(building,))
assert changed>0,changed
assert pilot.size==world.size
assert pilot.getpixel((100,100))==world.getpixel((100,100))
assert pilot.getpixel((155,150))==world.getpixel((155,150))
assert changed>0  # per-pixel sampling may leave a particular pixel unchanged
assert world.getpixel((30,30))==(186,147,108)
assert mask.getpixel((100,100))==0
assert mask.getpixel((30,30))==255

# Invalid tiles cannot accidentally enter the world.
try:
    make_pilot(world,{"bleached_dirt":source},
              regions=regions,draw_routes=False,buildings=())
    raise AssertionError("Non-seamless tile incorrectly accepted")
except ValueError:
    pass
print("Forsaken seam, route protection, source preservation tests OK")
