#!/usr/bin/env python3
"""Forsaken art-pack staging/validation; keeps reference boards out of gameplay.

Install the ZIP into assets/forsaken_v1/ and run:
    python3 tools/forsaken_pack.py --validate
    python3 tools/forsaken_pack.py --preview

No runtime dependency is added to the game. Pillow is only needed for preview.
Do not call the raw art boards production tiles: labels/backgrounds are baked
into the review images and tile continuity is not established.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"assets"/"forsaken_v1"
EXPECTED=("GFX-D01","GFX-A01","GFX-A02","GFX-A03","GFX-A04",
          "GFX-B01","GFX-B02","GFX-B03","GFX-B04")
PNG_HEADER=b"\x89PNG\r\n\x1a\n"


def png_size(path):
    with open(path,"rb") as source:
        header=source.read(24)
    if len(header)!=24 or header[:8]!=PNG_HEADER or header[12:16]!=b"IHDR":
        raise ValueError("Not a readable PNG header: "+str(path))
    return struct.unpack(">II",header[16:24])


def validate_pack(pack=PACK):
    pack=Path(pack)
    errors=[]
    try:
        manifest=json.loads((pack/"manifest.json").read_text())
    except (OSError,ValueError) as exc:
        return ["Missing/invalid art manifest: "+str(exc)]
    if manifest.get("schema_version")!=1:
        errors.append("Unsupported manifest version")
    if manifest.get("base_tile_px")!=16:
        errors.append("Artwork must follow 16px base grid")
    if manifest.get("baked_lighting") is not False:
        errors.append("Lighting must be game controlled")
    if manifest.get("render_perspective")!="true_top_down":
        errors.append("Perspective must be true top down")
    if manifest.get("integration_state")!="staged_review_only":
        errors.append("Reference package must remain staged; no unvalidated runtime art")
    sheets=manifest.get("sheets",[])
    if [entry.get("id") for entry in sheets]!=list(EXPECTED):
        errors.append("Missing, duplicated or reordered approved sheet IDs")
    for entry in sheets:
        path=pack/entry.get("file","")
        if not path.resolve().is_relative_to(pack.resolve()):
            errors.append("Unsafe relative sheet path")
            continue
        if not path.is_file():
            errors.append("Missing board: "+str(path))
            continue
        try:
            size=png_size(path)
        except (OSError,ValueError) as exc:
            errors.append(str(exc))
            continue
        if list(size)!=entry.get("size"):
            errors.append("Size mismatch: "+entry["id"])
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        if sha!=entry.get("sha256"):
            errors.append("Source SHA mismatch: "+entry["id"])
        if entry.get("production_status")!="reference_board_not_sprite_atlas":
            errors.append("Source board mislabeled as production atlas: "+entry["id"])
    return errors


def preview(pack=PACK):
    problems=validate_pack(pack)
    if problems:
        raise ValueError("Cannot preview invalid pack: "+"; ".join(problems))
    try:
        from PIL import Image,ImageDraw
    except ImportError:
        raise SystemExit("Preview creation requires Pillow (offline tool only)")
    pack=Path(pack)
    manifest=json.loads((pack/"manifest.json").read_text())
    columns=3
    tw,th=400,310
    page=Image.new("RGB",(tw*columns,th*3),(21,18,18))
    pen=ImageDraw.Draw(page)
    for index,entry in enumerate(manifest["sheets"]):
        original=Image.open(pack/entry["file"]).convert("RGB")
        original.thumbnail((tw-20,th-45),Image.Resampling.LANCZOS)
        x=(index%columns)*tw+10
        y=(index//columns)*th+10
        page.paste(original,(x,y))
        pen.text((x,y+th-35),entry["id"]+" | "+entry["name"],fill="#ebc3a0")
    output=pack/"preview"/"integration_contact.png"
    output.parent.mkdir(parents=True,exist_ok=True)
    page.save(output)
    return output


# Authored centres from the 1448x1086 approved terrain review board.
# This sheet is an illustration, NOT an already seamless pixel atlas.
TERRAIN_SAMPLES = (
    ("bleached_dirt",143,270), ("cracked_soil",485,270),
    ("dusty_road_soil",819,270), ("faded_grass",1180,270),
    ("dead_grass",143,490), ("gravel",485,490),
    ("mud",819,490), ("rocky_soil",1180,490),
    ("ash_gray_earth",143,705), ("patchy_weeds",485,705),
    ("sparse_moss",819,705), ("scorched_ground",1180,705),
)


def extract_terrain_candidates(pack=PACK):
    """Extract clean visual swatches; intentionally DO NOT mark tiles seamless.

    Each central 110x110 crop avoids review-board labels, frames and captions.
    Scale to 64x64 by nearest-neighbour only for the staging atlas; further
    processing and edge-pixel QA are required before a world bake.
    """
    problems=validate_pack(pack)
    if problems:
        raise ValueError("Invalid pack: "+"; ".join(problems))
    try:
        from PIL import Image,ImageDraw
    except ImportError:
        raise SystemExit("Terrain candidate extraction requires Pillow")
    pack=Path(pack)
    board=Image.open(pack/"source_boards"/"GFX-A01.png").convert("RGB")
    if board.size!=(1448,1086):
        raise ValueError("Terrain board crop coordinates require 1448x1086 source")
    out=pack/"candidates"/"A01"
    out.mkdir(parents=True,exist_ok=True)
    atlas=Image.new("RGB",(64*4,64*3))
    records=[]
    for index,(name,x,y) in enumerate(TERRAIN_SAMPLES):
        crop=board.crop((x-55,y-55,x+55,y+55))
        # Use explicit integer nearest-neighbour pixel lookup. This avoids
        # native Pillow resize backend failures on some Linux CI images and
        # retains deterministic pixel-art source sampling.
        tile=Image.new("RGB",(64,64))
        source_pixels=crop.load()
        output_pixels=tile.load()
        for row in range(64):
            sy=min(109,(row*110)//64)
            for col in range(64):
                sx=min(109,(col*110)//64)
                output_pixels[col,row]=source_pixels[sx,sy]
        tile.save(out/(name+".png"))
        atlas.paste(tile,((index%4)*64,(index//4)*64))
        pix=tile.load()
        # Difference across opposite edges, averaged over all channels,
        # is informational only; these tiles are not auto-approved.
        edge=sum(abs(pix[0,i][c]-pix[63,i][c]) +
                 abs(pix[i,0][c]-pix[i,63][c])
                 for i in range(64) for c in range(3))/(64*3*2)
        records.append({"id":name,"file":name+".png","size":[64,64],
                        "horizontal_vertical_edge_delta":round(edge,2),
                        "seamless":False,"status":"candidate_only"})
    atlas.save(out/"candidate_atlas.png")
    (out/"candidate_manifest.json").write_text(
        json.dumps({"source_sheet":"GFX-A01","source_is_presentation_board":True,
                    "world_ready":False,"tiles":records},indent=2)+"\n")
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack",type=Path,default=PACK)
    parser.add_argument("--validate",action="store_true")
    parser.add_argument("--preview",action="store_true")
    parser.add_argument("--extract-candidates",action="store_true")
    args=parser.parse_args()
    problems=validate_pack(args.pack)
    if problems:
        for problem in problems: print("FAIL:",problem)
        raise SystemExit(1)
    print("PASS: 9 Forsaken reference boards, checksums, format and art policy")
    if args.extract_candidates:
        print("Extracted non-seamless terrain candidates:",extract_terrain_candidates(args.pack))
    if args.preview:
        print("Created staging gallery:",preview(args.pack))
        print("Reference boards only; gameplay atlas conversion is a later gate.")


if __name__=="__main__":
    main()
