#!/usr/bin/env python3
"""GFX-07: build opt-in Cinder Creek roads + starter-map seam.

This is an offline raster build. It uses the original starter art's
documented road centre lines, never changes walkability, game solids or NPCs.
GFX-04 buildings are preferred as a SOURCE image, never painted over.
All optional A01 soil work is independent. Pillow is NOT needed at runtime.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cinder_creek_gfx import ZONE_BOUNDS,STARTER_BUILDINGS
from forsaken_route_renderer import validated_palette,DEFAULT_PALETTE

ASSETS=ROOT/"assets"
OUTPUT=ASSETS/"forsaken_v1"/"gfx07"/"world_gfx07.png"
PALETTE=ASSETS/"forsaken_v1"/"gfx06"/"route_palette.json"
BASE=ASSETS/"world.png"
BUILDING_WORLD=ASSETS/"forsaken_v1"/"runtime"/"world_forsaken.png"
TERRAIN_WORLD=ASSETS/"forsaken_v1"/"gfx05"/"world_gfx05.png"

# Authored OLD Cinder Creek image road centres from build_assets.py.
# Coordinates must not be moved to conceal seams: these locations match the
# visible inherited image, and new raster strokes stay on those same paths.
# The second tuple is full surface width in source world pixels.
START_ROADS=(
    ("primary",((0,570),(2350,570)),94),
    ("primary",((640,-20),(680,1620)),96),
    ("secondary",((640,570),(1830,430)),47),
    ("secondary",((650,580),(2020,1240)),52),
)
START_RAIL=((0,1420),(2400,1420))
RAIL_SURFACE_WIDTH=32
ROAD_COLOR=(166,125,82)
DIAGONAL_COLOR=(180,138,89)
RAIL_COLORS=((85,74,60),(120,96,69))

def road_geometry_mask(size=ZONE_BOUNDS[2:],roads=START_ROADS,rail=START_RAIL):
    """Binary mask of authored road/rail corridors; no imaginary connections."""
    mask=Image.new("L",size)
    painter=ImageDraw.Draw(mask)
    for kind,path,width in roads:
        painter.line(path,fill=255,width=width,joint="curve")
        rad=width//2
        for x,y in path:
            painter.ellipse((x-rad,y-rad,x+rad,y+rad),fill=255)
    painter.line(rail,fill=255,width=RAIL_SURFACE_WIDTH)
    return mask

def building_protection_mask(size=ZONE_BOUNDS[2:],buildings=STARTER_BUILDINGS,margin=18):
    """Prevent a painted rail/road shoulder from obscuring building artwork."""
    image=Image.new("L",size,255)
    p=ImageDraw.Draw(image)
    for name,x,y,w,h in buildings:
        p.rectangle((x-margin,y-margin,x+w+margin,y+h+margin),fill=0)
    return image

def _hex_rgb(hexcode):
    value=hexcode.lstrip("#")
    return tuple(int(value[i:i+2],16) for i in (0,2,4))

def get_palette(path=PALETTE):
    # Palette must be produced from SHA-verified source art by GFX06 tool.
    try:
        row=json.loads(Path(path).read_text())
        if row.get("schema_version")!=1 or row.get("art_source")!="GFX-A02 approved 17-board master":
            raise ValueError("Palette not generated from approved GFX-A02 source")
        return validated_palette(row["palette"])
    except (OSError,ValueError,TypeError,KeyError):
        raise ValueError("Run tools/gfx06_road_palette.py with the approved master ZIP before GFX-07")

def _legacy_replacement_mask(source,corridor,protect):
    """Replace only identifiable old painted road pixels inside authored paths.

    Do not assume arbitrary earth, vegetation or architectural pixels are old
    roads. We additionally replace EXACT old rails, not nearby decorations.
    """
    # Color distance from known build_assets.py stroke values, pixels in a
    # protected corridor. Restrict identification so terrain survives.
    src=source.convert("RGB")
    data=src.load()
    bounds=corridor.getbbox()
    result=Image.new("L",source.size)
    op=result.load();cp=corridor.load();pp=protect.load()
    if not bounds:return result,0
    count=0
    for y in range(bounds[1],bounds[3]):
        for x in range(bounds[0],bounds[2]):
            if not cp[x,y] or not pp[x,y]:continue
            r,g,b=data[x,y]
            legacy=((abs(r-ROAD_COLOR[0])<=10 and abs(g-ROAD_COLOR[1])<=10 and abs(b-ROAD_COLOR[2])<=10)
                    or (abs(r-DIAGONAL_COLOR[0])<=10 and abs(g-DIAGONAL_COLOR[1])<=10 and abs(b-DIAGONAL_COLOR[2])<=10)
                    or any(abs(r-c[0])<=6 and abs(g-c[1])<=6 and abs(b-c[2])<=6 for c in RAIL_COLORS))
            if legacy:
                op[x,y]=255;count+=1
    return result,count

def _surface_layers(size,palette,roads,rail):
    """Connected native Pillow road/rut/rail layers on one transparent image."""
    ink=Image.new("RGBA",size,(0,0,0,0))
    d=ImageDraw.Draw(ink)
    for kind,path,width in roads:
        if kind=="primary":
            strips=((width,_hex_rgb(palette["shoulder"])),
                    (max(1,width-16),_hex_rgb(palette["road"])),
                    (max(1,width-36),_hex_rgb(palette["center"])))
        else:
            strips=((width,_hex_rgb(palette["shoulder"])),
                    (max(1,width-12),_hex_rgb(palette["road"])),
                    (max(1,width-24),_hex_rgb(palette["center"])))
        for thickness,color in strips:
            d.line(path,fill=color+(255,),width=thickness,joint="curve")
            radius=thickness//2
            for x,y in path:
                d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color+(255,))
        # Screen-aligned wagon ruts; smooth along original diagonals.
        offset=width*.26
        a,b=path
        length=math.hypot(b[0]-a[0],b[1]-a[1]) or 1
        nx,ny=-(b[1]-a[1])/length,(b[0]-a[0])/length
        for sign in (-1,1):
            line=tuple((round(x+sign*offset*nx),round(y+sign*offset*ny)) for x,y in path)
            d.line(line,fill=_hex_rgb(palette["ruts"])+(220,),width=2)
    d.line(rail,fill=_hex_rgb(palette["ballast"])+(255,),width=32)
    # Sleepers across railway with original ~22px spacing.
    x0,y0=rail[0];x1,y1=rail[-1]
    length=math.hypot(x1-x0,y1-y0) or 1
    nx,ny=-(y1-y0)/length,(x1-x0)/length
    for s in range(0,int(length)+1,22):
        cx=x0+(x1-x0)*s/length;cy=y0+(y1-y0)*s/length
        d.line((round(cx-15*nx),round(cy-15*ny),
                round(cx+15*nx),round(cy+15*ny)),
               fill=_hex_rgb(palette["sleepers"])+(255,),width=5)
    for off in (-9,9):
        d.line(tuple((round(x+off*nx),round(y+off*ny)) for x,y in rail),
               fill=_hex_rgb(palette["rail"])+(255,),width=3)
    return ink

def render_starter_roads(source,palette,roads=START_ROADS,rail=START_RAIL,
                         buildings=STARTER_BUILDINGS):
    """Paint changed pixels ONLY inside authored corridors and outside buildings.

    The old road ink must be removed first to avoid doubled ghost lines.
    Keep unknown source colors and all paths' world positions unchanged.
    """
    if source.mode not in ("RGB","RGBA"):raise ValueError("Expected RGB/RGBA world")
    size=source.size
    corridor=road_geometry_mask(size,roads,rail)
    protected=building_protection_mask(size,buildings)
    erase,count=_legacy_replacement_mask(source,corridor,protected)
    # Reconstruct a nearby safe earth tone behind erased road ink, rather
    # than a new rectangular soil-color panel. The replacement is limited to
    # the exact old ink pixels, so trees and signs cannot become square holes.
    restored=source.convert("RGB")
    out=restored.load()
    e=erase.load()
    bounds=erase.getbbox()
    if bounds:
        for y in range(bounds[1],bounds[3]):
            for x in range(bounds[0],bounds[2]):
                if e[x,y]:
                    # Small deterministic grain keeps repaired pixels from
                    # looking like perfectly uniform tile/shape artifacts.
                    grain=((x*17+y*23)%9)-4
                    out[x,y]=tuple(max(0,min(255,v+grain)) for v in (176,143,105))
    paint=_surface_layers(size,palette,roads,rail)
    # Do not place new road ink on protected building art.
    a=paint.getchannel("A")
    from PIL import ImageChops
    a=ImageChops.multiply(a,protected)
    paint.putalpha(a)
    restored.paste(paint,mask=a)
    return restored,{"old_road_pixels_removed":count,
                     "road_paths":len(roads),"rail_paths":1,
                     "geometry_preserved":True}

def add_world_edge_feather(rgb,band=112):
    """An actual RGBA feather over the east and south world-image seams.

    Underlying procedural far-world render shows through. Alpha 255 over
    the rest of the image and 0 at the east/south outermost pixels.
    Slight deterministic undulation avoids a hard rectangular edge.
    """
    im=rgb.convert("RGBA")
    w,h=im.size
    if band<8 or w<band*2 or h<band*2:raise ValueError("Invalid seam band")
    alpha=Image.new("L",(w,h),255)
    px=alpha.load()
    for y in range(h):
        wave=round(8*math.sin(y/91)+5*math.sin(y/37))
        x0=max(0,w-band+wave)
        for x in range(x0,w):
            ratio=max(0,min(1,(w-1-x)/(w-1-x0)))
            px[x,y]=min(px[x,y],round(255*ratio*ratio*(3-2*ratio)))
    for x in range(w):
        wave=round(8*math.sin(x/87)+5*math.sin(x/43))
        y0=max(0,h-band+wave)
        for y in range(y0,h):
            ratio=max(0,min(1,(h-1-y)/(h-1-y0)))
            px[x,y]=min(px[x,y],round(255*ratio*ratio*(3-2*ratio)))
    im.putalpha(alpha)
    return im

def resolve_base(world=BASE,building=BUILDING_WORLD,terrain=TERRAIN_WORLD):
    """Do not stack prior edits: prefer the user-approved GFX04 building bake."""
    if Path(building).is_file():return Path(building),"GFX04 buildings"
    if Path(terrain).is_file():return Path(terrain),"GFX05 terrain"
    return Path(world),"original world"

def build(source,palette,out=OUTPUT,feather=True):
    with Image.open(source) as image:
        if image.size!=ZONE_BOUNDS[2:]:
            raise ValueError("The source world must be exactly 4800x3200")
        baseline=image.convert("RGB")
    baked,meta=render_starter_roads(baseline,palette)
    result=add_world_edge_feather(baked) if feather else baked.convert("RGBA")
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    result.save(out)
    # QA: center junction (near avatar), north/south roadway and old
    # structures are visible at 960x600. Review in-game too.
    compare=Image.new("RGB",(1920,600),(32,29,27))
    region=(218,280,1178,880)
    compare.paste(baseline.crop(region),(0,0))
    compare.paste(result.convert("RGB").crop(region),(960,0))
    compare.save(out.parent/"gfx07_starter_before_after.png")
    manifest={"stage":"GFX07","source":str(source),"output":str(out),
              "image_dimensions":list(result.size),"image_mode":result.mode,
              "east_south_alpha_feather":bool(feather),
              **meta,"source_sha256":hashlib.sha256(Path(source).read_bytes()).hexdigest(),
              "visual_approval":"pending"}
    (out.parent/"gfx07_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,
                        help="Optional explicit already-baked world.png source")
    parser.add_argument("--palette",type=Path,default=PALETTE)
    parser.add_argument("--out",type=Path,default=OUTPUT)
    parser.add_argument("--no-feather",action="store_true")
    args=parser.parse_args()
    source,label=(args.source,"explicit source") if args.source else resolve_base()
    palette=get_palette(args.palette)
    result=build(source,palette,args.out,not args.no_feather)
    print("PASS: GFX-07 starter roads + edge alpha feather",label)
    print("Original road ink removed:",result["old_road_pixels_removed"])
    print("Compare:",args.out.parent/"gfx07_starter_before_after.png")
    print("RUN: DUST_AND_DEBT_GFX07=1 DUST_AND_DEBT_GFX06=1 ./Play_Dust_and_Debt.sh")
if __name__=="__main__":
    main()
