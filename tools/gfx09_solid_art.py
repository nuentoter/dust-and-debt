#!/usr/bin/env python3
"""GFX-09 approved B01 trees and boulders -> actual transparent game sprites.

The approved 1536x1024 GFX-B01 board has a high-contrast magenta matte.\nFor boulders, reuse the clean approved GFX08 rock asset: the B01 rock\npanel has overlapping objects, and slicing them would repeat prior crop bugs.
Dark-backed B02/B03 and presentation borders are NEVER auto-keyed.
A separate QA manifest contains lower-foot alpha collision CANDIDATES only.
No collision is activated by this build step.
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.gfx05_pipeline import verify_source,_source_board
from tools.gfx05_collision import collision_rows
from tools.gfx08_wilderness import is_matte

OUT=ROOT/"assets"/"forsaken_v1"/"gfx09"
# Hand-reviewed bounds from isolated motifs on the real B01 magenta sheet.
# Keep art away from neighboring motifs and ornamental panel borders.
SPECS={
 "pine": {"box":(500,158,576,333),"size":(54,92),"kind":"tree"},
 "dead_tree": {"box":(20,171,165,333),"size":(72,88),"kind":"dead_tree"},
}
SOURCE_SIZE=(1536,1024)

def convert_sprite(board,box,size):
    if board.mode!="RGB":
        raise ValueError("Source artwork must be RGB")
    left,top,right,bottom=box
    if not(0<=left<right<=board.width and 0<=top<bottom<=board.height):
        raise ValueError("Invalid art boundaries")
    region=board.crop(box)
    result=Image.new("RGBA",region.size)
    src=region.load();dst=result.load()
    for y in range(region.height):
        for x in range(region.width):
            rgb=src[x,y]
            dst[x,y]=(0,0,0,0) if is_matte(*rgb) else (*rgb,255)
    alpha=result.getchannel("A")
    bounds=alpha.getbbox()
    if not bounds:
        raise ValueError("Missing sprite silhouette")
    # Do not manufacture lost pixels by cropping away the lower/right
    # edge. Review requires the whole object and preserves actual edges.
    # Hard reject a contiguous band along any source cell boundary.
    w,h=region.size
    for direction in ("left","right","top","bottom"):
        if direction=="left":
            occupied=sum(alpha.getpixel((0,y))>0 for y in range(h))
            extent=h
        elif direction=="right":
            occupied=sum(alpha.getpixel((w-1,y))>0 for y in range(h))
            extent=h
        elif direction=="top":
            occupied=sum(alpha.getpixel((x,0))>0 for x in range(w))
            extent=w
        else:
            occupied=sum(alpha.getpixel((x,h-1))>0 for x in range(w))
            extent=w
        if occupied>max(3,int(extent*.08)):
            raise ValueError("Potentially clipped or framed "+direction+" source art")
    opaque=sum(v>0 for v in alpha.getdata())
    if opaque<150 or opaque>int(w*h*.83):
        raise ValueError("Suspicious B01 art occupancy")
    art=result.crop(bounds).resize(size,Image.Resampling.NEAREST)
    final=Image.new("RGBA",(size[0]+12,size[1]+12))
    final.alpha_composite(art,(6,6))
    if final.getpixel((0,0))[3]!=0 or final.getpixel((final.width-1,final.height-1))[3]!=0:
        raise ValueError("Missing transparent margin")
    return final,{"source_bounds":list(box),"source_opaque_pixels":opaque,
                  "size":list(final.size),"physical_collision_activated":False}

def stage(archive,out=OUT):
    verify_source(archive)
    board=_source_board(archive,"GFX-B01")
    if board.size!=SOURCE_SIZE:raise ValueError("Unexpected approved B01 dimensions")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    manifest={"schema_version":1,"source":"GFX-B01 approved magenta source board",
              "source_verified":True,"geometry_modified":False,
              "art_review_required":True,"items":{}}
    review=Image.new("RGB",(600,250),(136,116,99))
    painter=ImageDraw.Draw(review)
    for i,(name,record) in enumerate(SPECS.items()):
        image,metadata=convert_sprite(board,record["box"],record["size"])
        image.save(out/(name+".png"))
        mask=collision_rows(image,record["kind"])
        if not mask:raise ValueError("No physical-footprint alpha candidate: "+name)
        metadata["collision_class"]=record["kind"]
        metadata["mask_rows"]=len(mask)
        metadata["mask_bounds"]=[min(a for _,a,b in mask),min(y for y,a,b in mask),
                                   max(b for _,a,b in mask),max(y for y,a,b in mask)+1]
        manifest["items"][name]=metadata
        draw=image.resize((image.width*2,image.height*2),Image.Resampling.NEAREST)
        x=15+i*190
        review.paste(draw,(x,12),draw)
        painter.text((x,228),name,fill="#1a1717")
    review.save(out/"review.png")
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive",required=True,type=Path)
    p.add_argument("--out",type=Path,default=OUT)
    a=p.parse_args()
    data=stage(a.archive,a.out)
    print("PASS: B01 full-coverage RGBA objects",",".join(data["items"]))
    print("Review:",a.out/"review.png")
    print("RUN: DUST_AND_DEBT_GFX09=1 ./Play_Dust_and_Debt.sh")

if __name__=="__main__":main()
