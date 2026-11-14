#!/usr/bin/env python3
"""GFX-03 pilot: seam-matched Forsaken ground with protected authored routes.

Offline only (Pillow). Never relocates roads, buildings, water or collision.
Review-board crops are evaluated as *texture candidates*, not production
autotiles. The exported 4800x3200 pilot is opt-in.
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cinder_creek_gfx import ZONE_BOUNDS, STARTER_BUILDINGS
from tools.forsaken_pack import PACK, validate_pack

TILE_SIZE = 64
EDGE_BAND = 8
# Terrain-only pilot areas near the starter zone; deliberately avoid town core.
PILOT_REGIONS = (
    # The first viewport is centred near (698,610). The original pilot
    # started south of the visible screen, leaving gameplay unchanged to
    # the player. V2 covers the complete Cinder Creek settlement and the
    # immediate approaches, with route/building and soil masks applied below.
    (0, 0, 1350, 1100, "ash_gray_earth"),
    (0, 1100, 1350, 2150, "bleached_dirt"),
    (1350, 0, 2400, 1700, "patchy_weeds"),
    (2400, 0, 3600, 1700, "rocky_soil"),
)
TILE_IDS = (
    "bleached_dirt", "cracked_soil", "dusty_road_soil",
    "faded_grass", "dead_grass", "gravel", "mud",
    "rocky_soil", "ash_gray_earth", "patchy_weeds",
    "sparse_moss", "scorched_ground",
)


def seam_edges(tile, band=EDGE_BAND):
    """Bring opposite outer rows/columns into exact pixel alignment.

    Original pixels are retained outside the blending band. Blend gradually
    towards the average of opposite boundary pixels; no blurry resizing or
    altered sprite dimensions. Returns a *new* RGB tile.
    """
    if tile.mode != "RGB" or tile.width != tile.height or tile.width < 2*band+2:
        raise ValueError("Expected square RGB tile larger than twice seam band")
    n = tile.width
    result = tile.copy()
    px = result.load()
    for y in range(n):
        left, right = px[0,y], px[n-1,y]
        midpoint = tuple((left[c]+right[c]+1)//2 for c in range(3))
        for d in range(band+1):
            strength = 1.0 - d / band
            strength = strength*strength*(3-2*strength)
            for x in (d,n-1-d):
                raw=px[x,y]
                px[x,y]=tuple(round(raw[c]*(1-strength)+midpoint[c]*strength)
                               for c in range(3))
    for x in range(n):
        top,bottom=px[x,0],px[x,n-1]
        midpoint=tuple((top[c]+bottom[c]+1)//2 for c in range(3))
        for d in range(band+1):
            strength=1.0-d/band
            strength=strength*strength*(3-2*strength)
            for y in (d,n-1-d):
                raw=px[x,y]
                px[x,y]=tuple(round(raw[c]*(1-strength)+midpoint[c]*strength)
                               for c in range(3))
    return result


def seam_error(tile):
    p=tile.convert("RGB").load()
    return max(max(abs(p[0,y][c]-p[tile.width-1,y][c]) for c in range(3))
               for y in range(tile.height)), max(
               max(abs(p[x,0][c]-p[x,tile.height-1][c]) for c in range(3))
               for x in range(tile.width))


def build_seamless(pack=PACK):
    """Build 12 deterministic tile previews and require exact edge matching."""
    pack=Path(pack)
    errors=validate_pack(pack)
    if errors:
        raise ValueError("Invalid source art pack: "+"; ".join(errors))
    source=pack/"candidates"/"A01"
    dest=pack/"prepared"/"A01"
    dest.mkdir(parents=True,exist_ok=True)
    atlas=Image.new("RGB",(4*TILE_SIZE,3*TILE_SIZE))
    records=[]
    for i,name in enumerate(TILE_IDS):
        path=source/(name+".png")
        if not path.is_file():
            raise ValueError("Run tools/forsaken_pack.py --extract-candidates first: "+str(path))
        with Image.open(path) as original:
            if original.size!=(TILE_SIZE,TILE_SIZE):
                raise ValueError("Wrong terrain sample dimensions: "+name)
            tile=seam_edges(original.convert("RGB"))
        h,v=seam_error(tile)
        if (h,v)!=(0,0):
            raise AssertionError("Tile seam failed: "+name)
        tile.save(dest/(name+".png"))
        atlas.paste(tile,((i%4)*TILE_SIZE,(i//4)*TILE_SIZE))
        records.append({"id":name,"file":name+".png",
                        "tile_pixels":TILE_SIZE,
                        "boundary_error_horizontal":h,
                        "boundary_error_vertical":v,
                        "pixel_edges_match":True,
                        "autotile_ready":False,
                        "visual_acceptance":"pending"})
    atlas.save(dest/"seam_checked_atlas.png")
    (dest/"tile_manifest.json").write_text(
        json.dumps({"schema_version":1,"source":"GFX-A01","tile_size":TILE_SIZE,
                    "pixel_seam_test_passed":True,"road_connections_validated":False,
                    "production_autotiles_complete":False,"tiles":records},indent=2)+"\n")
    return dest


# Crops in the reviewed GFX-A02 board. Still not modular game tiles.
A02_SAMPLES = (
    ("wagon_straight",76,245), ("wagon_curve",76,335),
    ("wagon_rough",220,246), ("trail_straight",485,245),
    ("trail_fork",749,245), ("rail_ballast",670,505),
    ("wagon_junction",1230,248), ("road_edge",1240,835),
)


def extract_road_candidates(pack=PACK):
    """Stage illustrative A02 road parts, not yet validated transparent tiles."""
    pack=Path(pack)
    errors=validate_pack(pack)
    if errors:
        raise ValueError("Invalid source art pack: "+"; ".join(errors))
    with Image.open(pack/"source_boards"/"GFX-A02.png") as image_file:
        if image_file.size!=(1448,1086):
            raise ValueError("Expected A02 board 1448x1086")
        image=image_file.convert("RGB")
    directory=pack/"candidates"/"A02"
    directory.mkdir(parents=True,exist_ok=True)
    atlas=Image.new("RGB",(56*4,56*2))
    records=[]
    for i,(name,x,y) in enumerate(A02_SAMPLES):
        crop=image.crop((x-28,y-28,x+28,y+28))
        crop.save(directory/(name+".png"))
        atlas.paste(crop,((i%4)*56,(i//4)*56))
        records.append({"id":name,"file":name+".png",
                        "crop_size":[56,56],"orientation":"as_reviewed",
                        "production_status":"concept_crop_only",
                        "connection_validated":False,"alpha_validated":False,
                        "route_geometry_unchanged":True})
    atlas.save(directory/"road_candidates.png")
    (directory/"candidate_manifest.json").write_text(json.dumps({
        "source":"GFX-A02","schema_version":1,
        "production_ready":False,"requires_transparency_cleanup":True,
        "requires_connections_test":True,"tiles":records},indent=2)+"\n")
    return directory


def route_exclusion_mask(size, buildings=STARTER_BUILDINGS,
                         draw_routes=True):
    """White = editable terrain, black = keep original source world pixels.

    Protect authored routes using the actual world-space route geometry,
    plus generous starter-town road corridors and all collision rectangles.
    Extra exclusion margin ensures grass edges don't overwrite wagon tracks.
    """
    mask=Image.new("L",size,255)
    d=ImageDraw.Draw(mask)
    if draw_routes:
        from new_austellia import ROADS, RAILS, SECONDARY_ROADS, TRAILS, START_SPUR
        from frontier_route_art import clip_segment
        view=(0,0,size[0],size[1])
        layers=[(route,110) for route in ROADS]
        layers += [(route,66) for _,route in SECONDARY_ROADS]
        layers += [(route,42) for _,_,_,route in TRAILS]
        layers += [(route,75) for route in RAILS]
        layers += [(START_SPUR,94)]
        for points,width in layers:
            for a,b in zip(points,points[1:]):
                clipped=clip_segment(a,b,view)
                if clipped:
                    p,q=clipped
                    d.line((*p,*q),fill=0,width=width)
                    rad=width//2
                    for ex,ey in (p,q):
                        d.ellipse((ex-rad,ey-rad,ex+rad,ey+rad),fill=0)
    # Starter legacy illustration contains roads that predate the authored
    # atlas. Protect them even if not represented by the atlas geometry.
    d.rectangle((0,490,size[0],650),fill=0)
    d.rectangle((595,0,745,size[1]),fill=0)
    for _,x,y,w,h in buildings:
        d.rectangle((x-55,y-55,x+w+55,y+h+55),fill=0)
    return mask


def terrain_color_mask(source):
    """Block dark art, grass, water and UI; only tint existing dusty earth.

    A conservative original-pixel classification, used in addition to the
    vector-route and authored-building exclusion mask.
    """
    image=source.convert("RGB")
    result=Image.new("L",image.size,0)
    src=image.load()
    dst=result.load()
    for y in range(image.height):
        for x in range(image.width):
            r,g,b=src[x,y]
            if 125<=r<=235 and 85<=g<=210 and 55<=b<=175 and r>=g+8 and g>=b-5:
                dst[x,y]=70  # subtle alpha; original world remains readable
    return result


def make_pilot(source, tiles, regions=PILOT_REGIONS, draw_routes=True,
               buildings=STARTER_BUILDINGS):
    """Render visible Forsaken textures on soil only; preserve world features.

    Compared with the former +/- 28 luminance adjustment this is a genuine
    material replacement (65-80% source texture). Only earth-like pixels are
    changed, source roads/rails/buildings are excluded using world-space masks,
    and an 80px feather at each region boundary prevents rectangular patches.
    """
    if source.mode!="RGB":
        raise ValueError("World source must be RGB")
    size=source.size
    protected=route_exclusion_mask(size,buildings,draw_routes)
    image=source.copy()
    mask_px=protected.load()
    source_px=source.load()
    changed=0
    significant=0
    preview_regions=[]
    for left,top,right,bottom,name in regions:
        left=max(0,left);top=max(0,top)
        right=min(size[0],right);bottom=min(size[1],bottom)
        if right<=left or bottom<=top:
            continue
        tile=tiles[name].convert("RGB")
        if tile.size!=(TILE_SIZE,TILE_SIZE) or seam_error(tile)!=(0,0):
            raise ValueError("Unverified seamless tile: "+name)
        base=image.crop((left,top,right,bottom))
        base_pixels=base.load()
        texture=tile.load()
        from PIL import ImageStat
        tile_mean=tuple(ImageStat.Stat(tile).mean)
        local_changed=0
        for yy in range(bottom-top):
            y=top+yy
            # Each region has a feathered mask rather than a boxed edge.
            margin_y=min(y-top,bottom-1-y)
            for xx in range(right-left):
                x=left+xx
                if mask_px[x,y]==0:
                    continue
                r,g,b=source_px[x,y]
                # Keep water, grass, buildings, signboards and dark objects.
                if not (115<=r<=242 and 75<=g<=210 and 48<=b<=185
                        and r>=g+8 and g>=b-5):
                    continue
                distance=min(margin_y,x-left,right-1-x)
                feather=max(0.0,min(1.0,distance/80.0))
                feather=feather*feather*(3.0-2.0*feather)
                if feather<=0:
                    continue
                tint=texture[x%TILE_SIZE,y%TILE_SIZE]
                # Use approved texture DETAIL, not its average grayscale/
                # muddy color. Direct blending painted a huge gray square
                # over the town; subtract the tile mean to preserve the
                # original ground material and road-adjacent hue.
                alpha=0.92*feather
                output=tuple(max(0,min(255,round(
                    original + alpha*(tint[i]-tile_mean[i]))))
                    for i,original in enumerate((r,g,b)))
                if output!=(r,g,b):
                    base_pixels[xx,yy]=output
                    changed+=1
                    local_changed+=1
                    if max(abs(output[i]-(r,g,b)[i]) for i in range(3))>=20:
                        significant+=1
        image.paste(base,(left,top))
        preview_regions.append({"terrain":name,"bounds":[left,top,right,bottom],
                                "changed_pixels":local_changed})
    return image,changed,protected



def bake_pilot(pack=PACK,source=None):
    pack=Path(pack)
    tiles_dir=build_seamless(pack)
    world_source=Path(source or ROOT/"assets"/"world.png")
    with Image.open(world_source) as orig:
        if orig.size!=ZONE_BOUNDS[2:]:
            raise ValueError("Original world must be 4800x3200")
        world=orig.convert("RGB")
    tiles={name:Image.open(tiles_dir/(name+".png")).convert("RGB")
           for name in TILE_IDS}
    pilot,changed,protected=make_pilot(world,tiles)
    from tools.forsaken_buildings import paint_forsaken_buildings
    gothic_buildings=paint_forsaken_buildings(pilot,pack,protected_mask=protected)
    if len(gothic_buildings)!=len(STARTER_BUILDINGS):
        raise RuntimeError("Forsaken building art incomplete: "+str(len(gothic_buildings)))
    # Mandatory human-visible proof: this is the real 960x600 starting
    # viewport, not a distant test region. Refuse to ship a blank visual
    # change and save a side-by-side image for inspection.
    view=(218,310,1178,910)
    old_frame=world.crop(view)
    new_frame=pilot.crop(view)
    old_px=old_frame.load()
    new_px=new_frame.load()
    visibly_changed=0
    max_delta=0
    for sy in range(600):
        for sx in range(960):
            old=old_px[sx,sy]
            new=new_px[sx,sy]
            delta=max(abs(new[i]-old[i]) for i in range(3))
            max_delta=max(max_delta,delta)
            if delta>=18:
                visibly_changed+=1
    if visibly_changed<2500 or max_delta<25:
        raise RuntimeError(
            "Forsaken pilot would look unchanged at the actual starting "
            "camera: only %s pixels visibly changed (max delta %s). "
            "Check base image, exclusion masks and source pack."
            % (visibly_changed,max_delta))
    comparison=Image.new("RGB",(1920,600))
    comparison.paste(old_frame,(0,0))
    comparison.paste(new_frame,(960,0))
    output=pack/"runtime"/"world_forsaken.png"
    output.parent.mkdir(parents=True,exist_ok=True)
    pilot.save(output,optimize=True)
    comparison.save(pack/"runtime"/"before_after_starter.png")
    protected.save(pack/"runtime"/"route_protection_mask.png")
    (pack/"runtime"/"pilot_manifest.json").write_text(json.dumps({
        "milestone":"GFX-03 terrain pilot only","source":str(world_source),
        "output":str(output),"world_size":list(pilot.size),
        "changed_terrain_pixels":changed,
        "gothic_buildings_painted":gothic_buildings,
        "building_count":len(gothic_buildings),
        "pilot_regions":[list(region) for region in PILOT_REGIONS],
        "texture_strength":0.92,
        "texture_method":"mean-centred detail, no rectangular palette replacement",
        "visibly_repaints_starter_camera":True,
        "visible_starter_pixels":visibly_changed,
        "starter_max_channel_delta":max_delta,
        "roads_and_buildings_preserved":True,
        "roads_illustration_replaced":False,
        "gameplay_geometry_modified":False,
        "needs_in_game_visual_acceptance":True,
        "needs_autotiles_and_road_art":True
    },indent=2)+"\n")
    return output,changed


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack",type=Path,default=PACK)
    parser.add_argument("--seam-tiles",action="store_true")
    parser.add_argument("--pilot",action="store_true")
    parser.add_argument("--road-candidates",action="store_true")
    parser.add_argument("--world",type=Path,default=None)
    args=parser.parse_args()
    if args.seam_tiles or args.pilot:
        directory=build_seamless(args.pack)
        print("Created twelve seam-checked tiles:",directory)
    if args.road_candidates:
        print("Extracted A02 road/rail candidates:",extract_road_candidates(args.pack))
    if args.pilot:
        output,changed=bake_pilot(args.pack,args.world)
        print("Created optional Forsaken ground pilot:",output,
              "(changed pixels:",changed,")")
        print("Roads and collision preserved; in-game artwork requires visual acceptance.")


if __name__=="__main__":
    main()
