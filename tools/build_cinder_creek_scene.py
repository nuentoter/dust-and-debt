#!/usr/bin/env python3
"""Bake the first Cinder Creek western-pixel-art terrain pass.

Run once on a development machine with Pillow installed. Runtime still needs
only Python and Tk. Never moves, resizes or invents gameplay collision.
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cinder_creek_gfx import STARTER_BUILDINGS, ZONE_BOUNDS
from tools.cinder_creek_buildings import paint_buildings
from tools.cinder_creek_sheet_art import paint_sheet_buildings, sprites_available, DEFAULT_SPRITES

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow is needed for asset baking: python3 -m pip install Pillow")

SOURCE = ROOT / "assets" / "world.png"
OUT = ROOT / "assets" / "gfx02" / "cinder_creek"
PALETTE = {
    "dirt_dark": "#a97d52",
    "dirt_light": "#d4ae79",
    "sand": "#e0b582",
    "sage_dark": "#536345",
    "sage_mid": "#718054",
    "sage_light": "#9eae6d",
    "wood": "#67432b",
    "wood_highlight": "#b78750",
    "stone": "#887668",
    "stone_highlight": "#bbab90",
    "clay": "#a95b3d",
    "shadow": "#644f3d",
}

def protected(x, y, radius=0):
    if not (0 <= x < ZONE_BOUNDS[2] and 0 <= y < ZONE_BOUNDS[3]):
        return True
    if any(bx-34-radius <= x <= bx+bw+34+radius and
           by-35-radius <= y <= by+bh+40+radius
           for _, bx, by, bw, bh in STARTER_BUILDINGS):
        return True
    # Existing route geometry is already in the source art. Leave the core
    # highway and town street legible, including the north-south main road.
    if abs(y-570) < 73+radius or abs(x-670) < 67+radius:
        return True
    return False

def grass(draw, x, y, seed):
    rng=random.Random(seed)
    dark=PALETTE["sage_dark"]
    mid=PALETTE["sage_mid"]
    for dx in (-6,-2,3,7):
        h=rng.randint(4,10)
        draw.line((x+dx,y+3,x+dx+rng.randint(-2,2),y-h),
                  fill=dark if dx%2 else mid,width=2)
    draw.point((x-4,y-3),fill=PALETTE["sage_light"])

def stones(draw,x,y,seed):
    rng=random.Random(seed)
    for _ in range(rng.randint(2,5)):
        dx=rng.randint(-12,12); dy=rng.randint(-6,6); r=rng.randint(2,5)
        draw.polygon([(x+dx-r,y+dy),(x+dx,y+dy-r),(x+dx+r,y+dy),
                      (x+dx+r-1,y+dy+3),(x+dx-r+1,y+dy+3)],
                     fill=PALETTE["stone"],outline=PALETTE["shadow"])
        draw.line((x+dx-r+1,y+dy,x+dx,y+dy-r+1),
                  fill=PALETTE["stone_highlight"],width=1)

def cactus(draw,x,y):
    dark=PALETTE["sage_dark"]
    mid=PALETTE["sage_mid"]
    draw.ellipse((x-10,y+1,x+11,y+6),fill=PALETTE["shadow"])
    draw.rectangle((x-3,y-22,x+4,y+2),fill=dark)
    draw.rectangle((x-1,y-21,x+1,y-1),fill=mid)
    draw.line((x-3,y-11,x-11,y-11,x-11,y-20),fill=dark,width=4)
    draw.line((x+3,y-8,x+11,y-8,x+11,y-18),fill=dark,width=4)
    draw.point((x,y-23),fill=PALETTE["sage_light"])

def flowers(draw,x,y,seed):
    rng=random.Random(seed)
    grass(draw,x,y,seed)
    for _ in range(4):
        dx=rng.randint(-9,9);dy=rng.randint(-11,1)
        draw.rectangle((x+dx,y+dy,x+dx+2,y+dy+2),
                       fill="#d7b865" if rng.randrange(3) else "#bb624a")

def texture(draw,width,height,rng):
    # Pixel-level, low-opacity-ish scattered tone marks. Because the source
    # is preserved under the marks, landmarks and building textures remain.
    colors=(PALETTE["dirt_dark"], PALETTE["dirt_light"],
            PALETTE["sand"])
    for _ in range(18000):
        x=rng.randrange(width); y=rng.randrange(height)
        if protected(x,y,3): continue
        n=rng.randint(1,3)
        draw.line((x,y,x+n,y),fill=colors[rng.randrange(len(colors))],width=1)

def bake(sprite_dir=DEFAULT_SPRITES, require_sheet=False):
    if require_sheet and not sprites_available(sprite_dir):
        raise SystemExit('Missing extracted sheet sprites at '+str(sprite_dir)+'; unpack the sprite ZIP at the repository root')
    image=Image.open(SOURCE).convert("RGB")
    width,height=image.size
    if (width,height)!=ZONE_BOUNDS[2:]:
        raise SystemExit(f"Unexpected source world.png dimensions: {(width,height)}")
    rng=random.Random(1889)
    draw=ImageDraw.Draw(image)
    texture(draw,width,height,rng)
    counts={"grass":0,"stone":0,"cactus":0,"flower":0}
    for i in range(1200):
        x=rng.randrange(20,width-20);y=rng.randrange(30,height-20)
        if protected(x,y,20):continue
        kind=rng.choices(("grass","stone","cactus","flower"),
                         weights=(7,4,1,2))[0]
        if kind=="grass":grass(draw,x,y,i+112)
        elif kind=="stone":stones(draw,x,y,i+221)
        elif kind=="cactus":cactus(draw,x,y)
        else:flowers(draw,x,y,i+337)
        counts[kind]+=1
    sheet_buildings=paint_sheet_buildings(image,sprite_dir)
    building_count=len(sheet_buildings) if sheet_buildings else paint_buildings(image)
    OUT.mkdir(parents=True,exist_ok=True)
    destination=OUT/"world_gfx02.png"
    image.save(destination,optimize=True)
    manifest={
        "milestone":"GFX-02 Cinder Creek first-pass",
        "source":"assets/world.png",
        "output":"assets/gfx02/cinder_creek/world_gfx02.png",
        "zone_bounds":list(ZONE_BOUNDS),
        "size":[width,height],
        "seed":1889,
        "decor_counts":counts,
        "redrawn_buildings":building_count,
        "art_source":"user_supplied_sheet" if sheet_buildings else "procedural_fallback",
        "sheet_sprite_buildings":sheet_buildings,
        "building_names":[row[0] for row in STARTER_BUILDINGS],
        "geometry_changes":False,
        "notes":"Deterministic coordinate-aligned Western building and terrain art. Further authored tileset work remains.",
    }
    (OUT/"build_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("Built",destination)
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprite-dir',type=Path,default=DEFAULT_SPRITES)
    parser.add_argument('--require-sheet',action='store_true',help='Fail rather than use procedural fallback')
    args=parser.parse_args()
    bake(args.sprite_dir,args.require_sheet)
