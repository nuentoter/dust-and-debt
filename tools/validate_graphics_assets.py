#!/usr/bin/env python3
"""Validate GFX asset handoff before shipping or merging art changes.

No additional runtime dependencies: Pillow is used by offline build tooling.
Examples:
  python3 tools/validate_graphics_assets.py
  python3 tools/validate_graphics_assets.py --require-sheet
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image
from cinder_creek_gfx import STARTER_BUILDINGS,ZONE_BOUNDS
from tools.cinder_creek_sheet_art import (
    DEFAULT_SPRITES, REQUIRED_SPRITES, validate_sprite_pack,
    sprites_available,
)

RULES=ROOT/"assets/gfx02/asset_rules.json"
MANIFEST=ROOT/"assets/gfx02/cinder_creek/build_manifest.json"


def validate_rules(path=RULES):
    errors=[]
    try:
        data=json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        return ["Graphics rules unreadable: "+str(exc)]
    if data.get("schema_version")!=1:
        errors.append("Unsupported graphics rules version")
    if data.get("base_tile_pixels")!=16:
        errors.append("Tile baseline must remain 16 pixels")
    if data.get("pixel_sampling")!="nearest":
        errors.append("Pixel sprites must use nearest-neighbour sampling")
    if data.get("world",{}).get("starter_dimensions")!=list(ZONE_BOUNDS[2:]):
        errors.append("Source-image geometry disagrees with game coordinates")
    if data.get("world",{}).get("geometry_may_change_with_art") is not False:
        errors.append("Graphics are not permitted to change gameplay geometry")
    if data.get("building",{}).get("shadow")!="source_alpha_mask":
        errors.append("Building shadows must use sprite alpha")
    directions=data.get("characters",{}).get("direction_order",[])
    if len(directions)!=8 or len(set(directions))!=8:
        errors.append("Eight unique character directions required")
    if not data.get("acceptance",{}).get("requires_rights_review_before_distribution"):
        errors.append("Asset rights review must remain part of acceptance")
    return errors


def validate_pack(directory=DEFAULT_SPRITES,require=False):
    directory=Path(directory)
    present=[directory/(stem+".png") for stem in REQUIRED_SPRITES
             if (directory/(stem+".png")).is_file()]
    if not present:
        return (["Required sheet sprites missing: "+str(directory)]
                if require else [])
    # A partially installed pack is a build error, not an automatic fallback.
    if len(present)!=len(REQUIRED_SPRITES):
        missing=set(REQUIRED_SPRITES)-{p.stem for p in present}
        return ["Incomplete sprite pack; missing: "+", ".join(sorted(missing))]
    errors=validate_sprite_pack(directory)
    for p in present:
        if not re.fullmatch(r"[a-z0-9_]+\.png",p.name):
            errors.append("Sprite filename must be lowercase_snake_case: "+p.name)
        with Image.open(p) as im:
            if im.mode not in ("RGBA","P","LA"):
                errors.append(p.name+": alpha-capable PNG mode required")
    return errors


def validate_manifest(path=MANIFEST):
    path=Path(path)
    if not path.is_file():
        return []  # Asset building may not have run locally yet.
    try:
        manifest=json.loads(path.read_text())
        target=ROOT/manifest["output"]
    except (OSError,KeyError,ValueError) as exc:
        return ["Bad graphics build manifest: "+str(exc)]
    errors=[]
    if manifest.get("size")!=list(ZONE_BOUNDS[2:]):
        errors.append("Baked world dimensions mismatch")
    if manifest.get("geometry_changes") is not False:
        errors.append("Graphics bake may not move collision geometry")
    if manifest.get("redrawn_buildings")!=len(STARTER_BUILDINGS):
        errors.append("Missing buildings from Cinder Creek art bake")
    source=manifest.get("art_source")
    if source not in ("user_supplied_sheet","procedural_fallback"):
        errors.append("Unrecognized building art source")
    if source=="user_supplied_sheet" and not sprites_available():
        errors.append("Manifest claims sheet art but sprites are missing")
    if not target.is_file():
        errors.append("Baked world image missing: "+str(target))
    else:
        try:
            with Image.open(target) as im:
                if im.size!=ZONE_BOUNDS[2:]:
                    errors.append("Baked PNG image is not 4800x3200")
        except OSError as exc:
            errors.append("Baked PNG cannot be opened: "+str(exc))
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprite-dir",type=Path,default=DEFAULT_SPRITES)
    parser.add_argument("--require-sheet",action="store_true",
                        help="Reject absent sprites and any procedural fallback")
    parser.add_argument("--manifest",type=Path,default=MANIFEST)
    args=parser.parse_args()
    errors=validate_rules()+validate_pack(args.sprite_dir,args.require_sheet)
    errors+=validate_manifest(args.manifest)
    if args.require_sheet and args.manifest.is_file():
        data=json.loads(args.manifest.read_text())
        if data.get("art_source")!="user_supplied_sheet":
            errors.append("Expected user-supplied sprite sheet, got procedural art")
    if errors:
        for error in errors:
            print("ERROR:",error)
        raise SystemExit(1)
    print("PASS: GFX asset rules, sprite pack and baked image")


if __name__=="__main__":
    main()
