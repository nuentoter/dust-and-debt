#!/usr/bin/env python3
"""GFX-07: genuine source-road removal and world-alpha seam regression."""
import json
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.gfx07_starter_roads import (
    road_geometry_mask,building_protection_mask,
    render_starter_roads,add_world_edge_feather,get_palette,
    START_ROADS,START_RAIL,resolve_base,
)
from forsaken_route_renderer import DEFAULT_PALETTE
from cinder_creek_gfx import select_world_image,STARTER_BUILDINGS

assert START_ROADS[0][1]==((0,570),(2350,570))
assert START_ROADS[1][1]==((640,-20),(680,1620))
assert START_RAIL==((0,1420),(2400,1420))
assert len(STARTER_BUILDINGS)==10

# Synthetic Cinder Creek with a primary horizontal/vertical junction and
# a building at the crossing. Check preserved source pixels outside the
# ORIGINAL road corridors and protected building ink inside them.
roads=(("primary",((0,90),(280,90)),36),
       ("primary",((150,0),(150,220)),35))
rail=((0,170),(280,170))
buildings=(("Mock Sheriff",120,60,45,38),)
world=Image.new("RGB",(320,240),(185,145,110))
p=ImageDraw.Draw(world)
p.line(roads[0][1],fill=(166,125,82),width=36)
p.line(roads[1][1],fill=(166,125,82),width=35)
p.line(rail,fill=(85,74,60),width=32)
p.rectangle((120,60,165,98),fill=(46,32,23))
p.ellipse((285,15,300,31),fill=(45,76,48))
original=world.copy()
out,manifest=render_starter_roads(world,DEFAULT_PALETTE,
                                 roads=roads,rail=rail,buildings=buildings)
assert manifest["old_road_pixels_removed"]>100
assert manifest["geometry_preserved"]
assert original.tobytes()==world.tobytes(),"Source was modified"
assert out.getpixel((132,75))==original.getpixel((132,75)), "Protected building changed"
assert out.getpixel((292,21))==original.getpixel((292,21)), "Vegetation outside roads changed"
assert out.getpixel((70,90))!=original.getpixel((70,90)), "Legacy road not recolored"
assert out.getpixel((15,170))!=original.getpixel((15,170)), "Rail not re-rendered"
mask=road_geometry_mask(world.size,roads,rail)
assert mask.getpixel((70,90))==255
assert mask.getpixel((300,40))==0
safe=building_protection_mask(world.size,buildings,margin=18)
assert safe.getpixel((132,75))==0
assert safe.getpixel((70,90))==255

edge=add_world_edge_feather(out,band=28)
assert edge.mode=="RGBA"
assert edge.getpixel((0,0))[3]==255
assert edge.getpixel((319,40))[3]==0
assert edge.getpixel((40,239))[3]==0
assert 0<edge.getpixel((300,100))[3]<255
assert 0<edge.getpixel((100,225))[3]<255

with tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    assets=root
    missing=select_world_image(str(assets),gfx07_enabled=True)
    assert missing.endswith("world.png")
    world_dir=assets/"forsaken_v1"/"gfx07"
    world_dir.mkdir(parents=True)
    Image.new("RGBA",(4800,3200),(0,0,0,255)).save(world_dir/"world_gfx07.png")
    assert select_world_image(str(assets),gfx07_enabled=True).endswith("world_gfx07.png")
    p=root/"palette.json"
    try:get_palette(p)
    except ValueError:pass
    else:raise AssertionError("Unverified source palette accepted")
    p.write_text(json.dumps({"schema_version":1,
            "art_source":"GFX-A02 approved 17-board master",
            "palette":dict(DEFAULT_PALETTE)}))
    assert get_palette(p)==DEFAULT_PALETTE

print("PASS: Starter-road junctions, rail, original artwork protection, edge alpha, fallback and palette")
