#!/usr/bin/env python3
"""Extract conservative GFX-A02 palette from the approved 17-board ZIP.

This is a COLOR integration from source art. It does not falsely interpret
presentation-board snippets as seamless curve/rail tilemaps.
"""
import argparse
import json
from pathlib import Path
import sys
from statistics import median

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.gfx05_pipeline import verify_source,_source_board,ROAD_SAMPLES
from forsaken_route_renderer import DEFAULT_PALETTE

DEFAULT_OUTPUT=ROOT/"assets"/"forsaken_v1"/"gfx06"/"route_palette.json"
MAP={
    "road":"wagon_straight",
    "center":"wagon_curve",
    "shoulder":"wagon_worn",
    "ruts":"wagon_corner",
    "trail":"trail_straight",
    "trail_edge":"trail_curve",
    "ballast":"rail_ballast",
    "sleepers":"track_component",
    "rail":"rail_ballast",
}

def _representative(image):
    # A02 presentation samples include magenta editor matte, black outlines
    # and cream/gold framing. Isolate mid-tones for material color reference.
    sample=[]
    for r,g,b in image.convert("RGB").getdata():
        if r>165 and b>150 and g<150:continue # magenta
        if max(r,g,b)<38 or min(r,g,b)>210:continue # text/ink
        if 54<=r<=205 and 42<=g<=191 and 35<=b<=175:
            sample.append((r,g,b))
    if len(sample)<24:
        raise ValueError("Not enough clean road material colors in source sample")
    return tuple(int(median(values)) for values in zip(*sample))

def build_palette(archive,output=DEFAULT_OUTPUT):
    verify_source(archive)
    art=_source_board(archive,"GFX-A02")
    if art.size!=(1448,1086):
        raise ValueError("Unsupported reviewed road sheet dimensions")
    coords={name:(x,y) for name,x,y in ROAD_SAMPLES}
    samples={}
    for name,(x,y) in coords.items():
        samples[name]=_representative(art.crop((x-16,y-16,x+16,y+16)))
    def hex_color(rgb):return "#{:02x}{:02x}{:02x}".format(*rgb)
    palette={}
    # Darker palette tones enhance the Forsaken Gothic readability, while
    # the relative source swatch hues remain visible in the middle bands.
    for key,source_name in MAP.items():
        rgb=samples[source_name]
        if key in ("ruts","trail_edge","sleepers"):
            value=tuple(max(0,round(v*.62)) for v in rgb)
        elif key=="shoulder":
            value=tuple(max(0,round(v*.83)) for v in rgb)
        elif key=="rail":
            value=tuple(min(255,round(v*1.16)) for v in rgb)
        else:value=rgb
        palette[key]=hex_color(value)
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({
        "schema_version":1,"art_source":"GFX-A02 approved 17-board master",
        "production_level":"opt_in_vector_route_pilot",
        "route_positions_modified":False,"connected_autotiles_claimed":False,
        "palette":palette,
        "source_samples":{k:hex_color(v) for k,v in samples.items()},
    },indent=2)+"\n")
    return palette

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,required=True)
    parser.add_argument("--out",type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    pal=build_palette(args.archive,args.out)
    print("PASS: derived",len(pal),"route colors; geometry unchanged")
    print("Palette:",args.out)
    print("Run: DUST_AND_DEBT_GFX06=1 ./Play_Dust_and_Debt.sh")
if __name__=="__main__":main()
