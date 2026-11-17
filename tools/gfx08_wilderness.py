#!/usr/bin/env python3
"""GFX-08: approved B01 magenta matte -> verified RGBA wilderness sprites.

Only B01 has a truly separable high-contrast background. Never auto-key the
other dark-backed boards: dark pixels are part of their artwork. Source ZIP
is verified against the 17-entry manifest before extraction.
"""
import argparse
import json
from pathlib import Path
import sys
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.gfx05_pipeline import verify_source,_source_board

OUT=ROOT/"assets"/"forsaken_v1"/"gfx08"
# Curated single-object crops from the 1536x1024 user-approved B01 board.
# The sheet contains text and neighboring sprites; avoid entire panel crops.
CROPS={
    "bush":(133,519,233,594),
    "fern":(22,777,107,852),
    "stump":(644,519,715,586),
    "rock":(664,789,730,845),
}
SIZES={"bush":(36,26),"fern":(30,24),"stump":(32,30),"rock":(34,28)}
CLASS={"bush":"shrub","fern":"grass","stump":"stump","rock":"boulder"}

def is_matte(r,g,b):
    """Strict magenta key; do not erase brown/red weathering or near-black ink."""
    return r>=193 and b>=182 and g<=90 and r>=g+115 and b>=g+110

def extract_one(board,box,dest,size):
    cell=board.crop(box).convert("RGB")
    w,h=cell.size
    image=Image.new("RGBA",(w,h))
    src=cell.load();dst=image.load()
    nonzero=0
    for y in range(h):
        for x in range(w):
            r,g,b=src[x,y]
            if is_matte(r,g,b):
                dst[x,y]=(0,0,0,0)
            else:
                dst[x,y]=(r,g,b,255)
                nonzero+=1
    bbox=image.getchannel("A").getbbox()
    if bbox is None or nonzero<w*h*.03:
        raise ValueError("No object pixels in B01 crop "+str(box))
    # Bad-crop protection: no opaque art can touch the cell border, which
    # would mean part of the silhouette was cut off or text contaminated it.
    if bbox[0]<2 or bbox[1]<2 or bbox[2]>w-2 or bbox[3]>h-2:
        raise ValueError("Incomplete or contaminated sprite crop "+str(box)+" bounds "+str(bbox))
    core=image.crop(bbox)
    fitted=core.resize(size,Image.Resampling.NEAREST)
    framed=Image.new("RGBA",(size[0]+8,size[1]+8))
    framed.alpha_composite(fitted,(4,4))
    framed.save(dest)
    if framed.getpixel((0,0))[3]!=0:
        raise AssertionError("Transparent sprite margin missing")
    return {"file":dest.name,"pixels":list(framed.size),"opaque_pixels":nonzero,
            "source_bounds":list(box),"alpha_corners_transparent":True}

def stage(archive,out=OUT):
    verify_source(archive)
    board=_source_board(archive,"GFX-B01")
    if board.size!=(1536,1024):
        raise ValueError("Unexpected B01 sheet; do not guess crop coordinates")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    metadata={}
    for name,box in CROPS.items():
        metadata[name]=extract_one(board,box,out/(name+".png"),SIZES[name])
        metadata[name]["collision_class"]=CLASS[name]
        metadata[name]["physical_collision_activated"]=False
    manifest={"schema_version":1,"source":"GFX-B01 approved magenta source board",
              "source_verified":True,"mattes_keyed_to_alpha":True,
              "artwork_review_pending":True,"geometry_modified":False,
              "items":metadata}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    # Production-style preview on neutral earth, not a fake magenta source.
    preview=Image.new("RGB",(420,140),(143,123,104))
    pen=ImageDraw.Draw(preview)
    for i,name in enumerate(CROPS):
        sprite=Image.open(out/(name+".png")).convert("RGBA")
        enlarged=sprite.resize((sprite.width*2,sprite.height*2),Image.Resampling.NEAREST)
        x=i*104+10;y=12
        preview.paste(enlarged,(x,y),enlarged)
        pen.text((x,108),name,fill=(32,27,24))
    preview.save(out/"review.png")
    return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,required=True)
    parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args()
    meta=stage(args.archive,args.out)
    print("PASS: verified",len(meta["items"]),"B01 RGBA objects")
    print("REVIEW:",args.out/"review.png")
    print("RUN: DUST_AND_DEBT_GFX08=1 ./Play_Dust_and_Debt.sh")

if __name__=="__main__":main()
