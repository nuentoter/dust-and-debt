#!/usr/bin/env python3
"""GFX-05: verified source art -> review candidates -> opt-in terrain pilot.

Accepts the 17-board source ZIP directly. Boards are RGB presentation art;
this tool NEVER claims their grid cells are proven 16px autotiles or that
road-intersection sprites are production-ready. Runtime game needs no Pillow.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.build_forsaken_pilot import (
    seam_edges,seam_error,make_pilot,TILE_IDS,
)
from cinder_creek_gfx import ZONE_BOUNDS

SOURCE_ZIP_NAME="Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip"
STAGING=ROOT/"assets"/"forsaken_v1"/"gfx05"
WORLD=ROOT/"assets"/"world.png"
OUTPUT=STAGING/"world_gfx05.png"
EXPECTED_GROUPS=("GFX-A01","GFX-A02","GFX-A03","GFX-A04",
    "GFX-B01","GFX-B02","GFX-B03","GFX-B04",
    "GFX-C01_C04","GFX-C02","GFX-C03","GFX-D02","GFX-D03",
    "GFX-E01_E02","GFX-E03","GFX-E04_E05","GFX-F01_F02")
# Centred within eight explicitly illustrated samples in each category
# (left large grid), not on labels, borders, or the right-hand summary.
TERRAIN_ROWS=(
    ("dirt",313),("sand",371),("packed_earth",432),
    ("dry_grass",492),("dead_grass",551),("scrub",611),
    ("transition",663),
)
TERRAIN_X=(208,298,390,480,570,663,754,845)
# 12 conservative tiles for the existing optional soil-only renderer.
PILOT_PICK={
    "bleached_dirt":("sand",1),
    "cracked_soil":("packed_earth",0),
    "dusty_road_soil":("dirt",1),
    "faded_grass":("dry_grass",0),
    "dead_grass":("dead_grass",0),
    "gravel":("dirt",6),
    "mud":("packed_earth",2),
    "rocky_soil":("dirt",7),
    "ash_gray_earth":("dirt",0),
    "patchy_weeds":("scrub",1),
    "sparse_moss":("transition",2),
    "scorched_ground":("packed_earth",5),
}
# Real coordinates from the approved A02 *presentation* panel.
# Descriptive, not a road-connection or rail-direction guarantee.
ROAD_SAMPLES=(
    ("wagon_straight",76,244),("wagon_worn",149,243),
    ("wagon_curve",76,332),("wagon_corner",148,334),
    ("trail_straight",451,240),("trail_curve",507,332),
    ("trail_fork",729,240),("road_junction",962,243),
    ("road_cross",1207,245),("rail_ballast",650,455),
    ("track_component",948,455),("bridge_approach",715,775),
)

def _safe_name(member):
    p=Path(member)
    return (not p.is_absolute() and ".." not in p.parts
            and not member.startswith("/") and "\\" not in member)

def verify_source(archive):
    """Enforce provenance, completeness and actual exact SHA of every board."""
    archive=Path(archive)
    with zipfile.ZipFile(archive) as z:
        entries=set(z.namelist())
        if not all(_safe_name(n) for n in entries):
            raise ValueError("Unsafe zip archive member name")
        if "manifest.json" not in entries:
            raise ValueError("Source art archive is missing manifest.json")
        manifest=json.loads(z.read("manifest.json"))
        if manifest.get("asset_count")!=17 or manifest.get("pack_version")!="source-v1":
            raise ValueError("Unexpected source-art manifest")
        sheets=manifest.get("files",[])
        if len(sheets)!=17 or {v["id"] for v in sheets}!=set(EXPECTED_GROUPS):
            raise ValueError("Expected exactly the 17 approved asset groups")
        for row in sheets:
            path=row["relative_path"]
            if not _safe_name(path) or path not in entries:
                raise ValueError("Invalid or missing source board: "+path)
            raw=z.read(path)
            if hashlib.sha256(raw).hexdigest()!=row["sha256"]:
                raise ValueError("Source board checksum mismatch: "+path)
            from io import BytesIO
            with Image.open(BytesIO(raw)) as im:
                if list(im.size)!=row["dimensions"] or im.format!="PNG":
                    raise ValueError("Source board dimensions/format differ: "+path)
    return manifest

def _source_board(archive,name):
    from io import BytesIO
    with zipfile.ZipFile(archive) as z:
        with Image.open(BytesIO(z.read("boards/"+name+".png"))) as im:
            return im.convert("RGB")

def _crop_inside(board,x,y,side=48):
    box=(x-side//2,y-side//2,x+side//2,y+side//2)
    if min(box)<0 or box[2]>board.width or box[3]>board.height:
        raise ValueError("Sample would crop beyond artwork")
    return board.crop(box)

def stage(archive,out=STAGING):
    """Create all terrain/road candidates and visual QA, without world edits."""
    verify_source(archive)
    out=Path(out)
    terrain=out/"candidates"/"A01"
    roads=out/"candidates"/"A02"
    terrain.mkdir(parents=True,exist_ok=True)
    roads.mkdir(parents=True,exist_ok=True)
    ground_board=_source_board(archive,"GFX-A01")
    if ground_board.size!=(1448,1086):
        raise ValueError("Unrecognized A01 board layout")
    raw={}
    for group,y in TERRAIN_ROWS:
        for index,x in enumerate(TERRAIN_X):
            stem=f"{group}_{index:02d}"
            crop=_crop_inside(ground_board,x,y)
            crop.save(terrain/(stem+"_source.png"))
            raw[(group,index)]=crop
    # Fit actual source detail into the historical 64px optional-renderer
    # contract, then match opposite edges exactly (still a PILOT tile).
    palette={}
    for name in TILE_IDS:
        group,index=PILOT_PICK[name]
        crop=raw[(group,index)]
        sample=crop.resize((64,64),Image.Resampling.NEAREST)
        tile=seam_edges(sample)
        if seam_error(tile)!=(0,0):
            raise AssertionError("Terrain candidate seam mismatch: "+name)
        tile.save(terrain/(name+".png"))
        palette[name]=tile
    road_board=_source_board(archive,"GFX-A02")
    if road_board.size!=(1448,1086):
        raise ValueError("Unrecognized A02 board layout")
    for name,x,y in ROAD_SAMPLES:
        _crop_inside(road_board,x,y,48).save(roads/(name+".png"))

    # Explicitly visible proof of source extraction, NOT a production tilemap.
    sample=Image.new("RGB",(640,360),(27,24,23))
    pen=ImageDraw.Draw(sample)
    for i,name in enumerate(TILE_IDS):
        tile=palette[name]
        x=12+(i%6)*105;y=26+(i//6)*125
        tile.resize((88,88),Image.Resampling.NEAREST)
        sample.paste(tile,(x,y))
        pen.text((x,y+92),name[:14],fill="#e1c5a8")
    sample.save(out/"terrain_review.png")
    road_preview=Image.new("RGB",(640,400),(29,26,25))
    pen=ImageDraw.Draw(road_preview)
    for i,(name,x,y) in enumerate(ROAD_SAMPLES):
        patch=Image.open(roads/(name+".png")).convert("RGB")
        px=10+(i%6)*105;py=15+(i//6)*195
        road_preview.paste(patch.resize((88,88),Image.Resampling.NEAREST),(px,py))
        pen.text((px,py+92),name[:15],fill="#e1c5a8")
    road_preview.save(out/"roads_review.png")
    manifest={
        "schema_version":1,"source":"17-board Forsaken source-v1 ZIP",
        "source_archive_sha256":hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
        "a01":{"pilot_tiles":list(TILE_IDS),"tile_size":64,
               "seam_edges_match":True,"artist_verified":False,
               "production_autotile":False,"texture_source":"illustrated 48px board interiors"},
        "a02":{"candidates":[entry[0] for entry in ROAD_SAMPLES],
               "connected_tiles_validated":False,
               "route_replacement_enabled":False},
        "original_world_preserved":True,
        "runtime_status":"staged_no_game_mutation",
    }
    (out/"staging_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def bake(archive,out=STAGING,world_path=WORLD,output=OUTPUT):
    """Opt-in A01 soil-only pilot. Never recolor authored routes or buildings."""
    manifest=stage(archive,out)
    out=Path(out)
    with Image.open(world_path) as f:
        if f.size!=ZONE_BOUNDS[2:]:
            raise ValueError("World must be original 4800x3200")
        original=f.convert("RGB")
    tiles={name:Image.open(out/"candidates"/"A01"/(name+".png")).convert("RGB")
           for name in TILE_IDS}
    # Cinder Creek only. Original roads, buildings, water, actors, NPCs and
    # game-world collision are all managed by existing unchanged game data.
    regions=((0,0,1330,1090,"ash_gray_earth"),)
    result,changed,protected=make_pilot(
        original,tiles,regions=regions,draw_routes=True)
    if changed<=0:
        raise ValueError("No actual terrain pixels changed")
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    result.save(output)
    comparison=Image.new("RGB",(1920,600))
    area=(200,190,1160,790)
    comparison.paste(original.crop(area),(0,0))
    comparison.paste(result.crop(area),(960,0))
    comparison.save(out/"gfx05_before_after.png")
    manifest["runtime_status"]="opt_in_pilot_generated"
    manifest["edited_earth_pixels"]=changed
    manifest["world_output"]=str(output)
    manifest["roads_replaced"]=False
    manifest["terrain_collision_modified"]=False
    (out/"staging_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return changed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,required=True,
                        help="Original 17-board master ZIP, NOT a previous 9-board pack")
    parser.add_argument("--out",type=Path,default=STAGING)
    parser.add_argument("--world",type=Path,default=WORLD)
    parser.add_argument("--verify",action="store_true")
    parser.add_argument("--stage",action="store_true")
    parser.add_argument("--pilot",action="store_true")
    args=parser.parse_args()
    if not (args.verify or args.stage or args.pilot):
        parser.error("Choose --verify, --stage or --pilot")
    if args.verify:
        print("PASS: verified 17 sheets",verify_source(args.archive)["pack_version"])
    if args.pilot:
        # bake() stages once already; avoid redundant 47MB source checksum
        # and 56-swatch extraction work on older machines.
        output=args.out/"world_gfx05.png"
        count=bake(args.archive,args.out,args.world,output)
        print("PASS: staged A01/A02 concept candidates")
        print("PREVIEWS:",args.out/"terrain_review.png",args.out/"roads_review.png")
        print("PASS: changed",count,"original soil pixels, preserved authored roads")
        print("RUN: DUST_AND_DEBT_GFX05=1 ./Play_Dust_and_Debt.sh")
    elif args.stage:
        stage(args.archive,args.out)
        print("PASS: staged 12 A01 seam-matched PILOT textures and 12 unvalidated A02 samples")
        print("PREVIEWS:",args.out/"terrain_review.png",args.out/"roads_review.png")
if __name__=="__main__":
    main()
