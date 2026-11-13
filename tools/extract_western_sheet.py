#!/usr/bin/env python3
"""Extract usable Cinder Creek building PNGs from the supplied style sheet.

Usage:
    python3 tools/extract_western_sheet.py 'A Western Tale_ Village Tileset.png'
    python3 tools/build_cinder_creek_scene.py --require-sheet

The crop rectangles are authored for the 1312x1199 supplied image. A
border-connected dark matte is made transparent, retaining dark interior
windows and roof lines that are not connected to the sheet backdrop.
"""
import argparse
from collections import deque
from pathlib import Path

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets"/"gfx02"/"cinder_creek"/"sprites"
SOURCE_SIZE=(1312,1199)
CROPS={
    "saloon":(554,151,734,286),
    "store":(758,151,914,284),
    "smithy":(919,151,1087,282),
    "house":(1115,149,1249,284),
    "stable":(557,320,692,455),
    "church":(706,307,815,453),
    "sheriff":(826,323,947,455),
    "inn":(967,319,1094,452),
}


def _matte(pixel):
    r,g,b,a=pixel
    return a==0 or (r<44 and g<52 and b<62 and b>=r-7 and g>=r-9)


def remove_sheet_background(image):
    """Flood-fill the contiguous dark backdrop, never windows inside a roof."""
    image=image.convert("RGBA")
    width,height=image.size
    pixels=image.load()
    visited=bytearray(width*height)
    queue=deque()
    for x in range(width):
        queue.append((x,0))
        queue.append((x,height-1))
    for y in range(height):
        queue.append((0,y))
        queue.append((width-1,y))
    while queue:
        x,y=queue.popleft()
        index=y*width+x
        if visited[index] or not _matte(pixels[x,y]):
            continue
        visited[index]=1
        pixels[x,y]=(0,0,0,0)
        if x>0: queue.append((x-1,y))
        if x+1<width: queue.append((x+1,y))
        if y>0: queue.append((x,y-1))
        if y+1<height: queue.append((x,y+1))
    bounds=image.getbbox()
    if not bounds:
        raise ValueError("Sprite crop was entirely empty")
    return image.crop(bounds)


def extract(source,output=OUT):
    with Image.open(source) as original:
        if original.size!=SOURCE_SIZE:
            raise ValueError("Expected supplied sheet %s; got %s"%
                             (SOURCE_SIZE,original.size))
        original=original.convert("RGBA")
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    for name,rect in CROPS.items():
        sprite=remove_sheet_background(original.crop(rect))
        sprite.save(output/(name+".png"),optimize=True)
        print("%s: %sx%s"%(name,*sprite.size))
    return tuple(output/(name+".png") for name in CROPS)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet",type=Path,help="Original 1312x1199 Western village sheet PNG")
    parser.add_argument("--output",type=Path,default=OUT)
    args=parser.parse_args()
    extract(args.sheet,args.output)
