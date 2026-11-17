#!/usr/bin/env python3
"""Build the opt-in Cinder Creek world with the NEW magenta-background art.

Runs offline with Pillow, not in Tk's rendering loop. The old mission, roads,
building interactions and collision rectangles remain unchanged.
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"assets/forsaken_v1/redrawn/GFX-D01-redrawn.png"
SPRITES=ROOT/"assets/forsaken_v1/game_ready/buildings"
WORLD=ROOT/"assets/world.png"
DEST=ROOT/"assets/forsaken_v1/runtime/world_forsaken.png"
NAMES=("sheriff","saloon","general_store","inn","doctor","hotel",
       "stable","bank","cabin","station","ranch","undertaker")
# Authoritative gameplay geometry, cross-checked in regression tests.
BUILDINGS=(("Sheriff",320,300,196,130,"sheriff"),
 ("Saloon",565,315,238,160,"saloon"),
 ("General Store",854,318,204,144,"general_store"),
 ("Doctor",320,694,169,120,"doctor"),
 ("Stable",835,728,210,144,"stable"),
 ("Hotel",540,735,215,168,"hotel"),
 ("Station",1150,1321,240,115,"station"),
 ("Cabin",1670,320,140,110,"cabin"),
 ("Outpost",1960,1150,140,100,"cabin"),
 ("Ranch",1470,850,160,125,"ranch"))

def magenta(rgb):
    r,g,b=rgb
    return r>155 and b>150 and g<150 and (r+b)//2-g>75

def extract(sheet,output):
    """Four columns by three rows, including entire building bottom edges."""
    if sheet.size!=(1448,1086):
        raise ValueError("Need complete 1448x1086 new high-contrast sheet")
    output.mkdir(parents=True,exist_ok=True)
    gallery=Image.new("RGB",(1448,960),(30,27,28))
    draw=ImageDraw.Draw(gallery)
    records=[]
    for i,name in enumerate(NAMES):
        col,row=i%4,i//4
        cell=sheet.crop((col*362,row*362,col*362+362,row*362+362)).convert("RGB")
        pixels=cell.load()
        alpha=Image.new("L",cell.size,0)
        mask=alpha.load()
        for y in range(362):
            for x in range(362):
                mask[x,y]=0 if magenta(pixels[x,y]) else 255
        bounds=alpha.getbbox()
        if not bounds or bounds[2]-bounds[0]<75 or bounds[3]-bounds[1]<70:
            raise ValueError("Incomplete building crop: "+name)
        art=cell.crop(bounds).convert("RGBA")
        art.putalpha(alpha.crop(bounds))
        sprite=Image.new("RGBA",(art.width+16,art.height+16))
        sprite.alpha_composite(art,(8,8))
        if sprite.getchannel("A").getextrema()!=(0,255):
            raise ValueError("Expected full transparent background: "+name)
        for px in sprite.getdata():
            if px[3]>0 and magenta(px[:3]):
                raise ValueError("Magenta leaking into sprite: "+name)
        sprite.save(output/(name+".png"))
        # Review contact sheet only: magenta is NOT part of export.
        panel=Image.new("RGBA",(340,290),(255,0,255,255))
        factor=min(1,320/sprite.width,260/sprite.height)
        shown=sprite.resize((round(sprite.width*factor),round(sprite.height*factor)),
                            Image.Resampling.NEAREST)
        panel.alpha_composite(shown,((340-shown.width)//2,(290-shown.height)//2))
        gallery.paste(panel.convert("RGB"),(col*362+10,row*320+24))
        draw.text((col*362+12,row*320+6),name.replace("_"," ").title(),
                  fill="#f2ddc9")
        records.append({"id":name,"source_cell":[col,row],
                        "dimensions":list(sprite.size),"alpha_checked":True})
    gallery.save(output/"redrawn_review.png")
    return records

def soil_color(original,x,y,w,h):
    """Sample surrounding earth instead of tiling a gray panel."""
    pixels=original.load()
    sx,sy=original.size
    samples=[]
    def consider(px,py):
        if not (0<=px<sx and 0<=py<sy):return
        r,g,b=pixels[px,py]
        if 115<=r<=242 and 75<=g<=211 and 48<=b<=187 and r>=g+8 and g>=b-5:
            samples.append((r,g,b))
    for offset in (22,35,52):
        for xx in range(x-15,x+w+16,5):
            consider(xx,y-offset);consider(xx,y+h+offset)
        for yy in range(y-15,y+h+16,5):
            consider(x-offset,yy);consider(x+w+offset,yy)
    if len(samples)<10:
        raise ValueError("No safe surrounding soil near "+str((x,y)))
    return tuple(sorted(s[c] for s in samples)[len(samples)//2]
                 for c in range(3))

def bake_world(original,directory,locations=BUILDINGS):
    result=original.convert("RGB").copy()
    placed=[]
    for name,x,y,w,h,stem in locations:
        with Image.open(directory/(stem+".png")) as incoming:
            if incoming.mode!="RGBA":raise ValueError("Non-RGBA: "+stem)
            art=incoming.copy()
        dirt=soil_color(original,x,y,w,h)
        # Remove old graphics strictly inside original collider rectangle.
        # Existing roads/trails and physics outside remain untouched.
        box=Image.new("RGB",(w,h),dirt)
        p=box.load()
        for yy in range(h):
            for xx in range(w):
                grain=((xx+x)*37+(yy+y)*23)%9-4
                p[xx,yy]=tuple(max(0,min(255,c+grain)) for c in dirt)
        result.paste(box,(x,y))
        scale=min((w-8)/art.width,(h+8)/art.height)
        dims=(max(1,round(art.width*scale)),max(1,round(art.height*scale)))
        art=art.resize(dims,Image.Resampling.NEAREST)
        sx=x+(w-dims[0])//2; sy=y+h-dims[1]
        result.paste(art,(sx,sy),art)
        placed.append({"name":name,"image":stem,"south_anchor":[x+w//2,y+h],
                       "draw_bounds":[sx,sy,*dims]})
    return result,placed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=SOURCE)
    parser.add_argument("--world",type=Path,default=WORLD)
    parser.add_argument("--output",type=Path,default=DEST)
    parser.add_argument("--extract-only",action="store_true")
    args=parser.parse_args()
    with Image.open(args.source) as f:
        records=extract(f.convert("RGB"),SPRITES)
    print("PASS: 12 high-contrast redrawn RGBA sprite exports")
    if args.extract_only:return
    with Image.open(args.world) as f:
        if f.size!=(4800,3200):
            raise ValueError("Original world must be 4800x3200")
        original=f.convert("RGB")
    world,placed=bake_world(original,SPRITES)
    if len(placed)!=10:raise ValueError("Expected 10 Cinder Creek buildings")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    world.save(args.output)
    area=(218,310,1178,910)
    comparison=Image.new("RGB",(1920,600))
    comparison.paste(original.crop(area),(0,0))
    comparison.paste(world.crop(area),(960,0))
    comparison.save(args.output.parent/"redrawn_before_after_cinder_creek.png")
    manifest={"source":str(args.source),"world":str(args.output),
              "source_image_size":[1448,1086],"world_size":[4800,3200],
              "sprite_exports":records,"placements":placed,
              "collision_or_route_geometry_modified":False,
              "visual_acceptance":"pending"}
    (args.output.parent/"redrawn_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("PASS: opt-in Cinder Creek redraw",args.output)
    print("COMPARE:",args.output.parent/"redrawn_before_after_cinder_creek.png")

if __name__=="__main__":main()
