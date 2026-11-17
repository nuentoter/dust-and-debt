"""GFX-06: camera-local route paint on AUTHORED New Austellia polylines.

The approved A02 review board supplies color/style references, not validated
16px connected tiles. This renderer paints connected road shoulders, paired
wheel ruts, footpaths and railway sleepers without touching route positions
or collision. Pure Tk; no Pillow required during game launch.
"""
import math
from frontier_route_art import clip_segment
from new_austellia import ROADS, SECONDARY_ROADS, TRAILS, RAILS

DEFAULT_PALETTE={
    "shoulder":"#655a50",
    "road":"#8e7965",
    "center":"#a58e74",
    "ruts":"#4c433d",
    "trail":"#81725c",
    "trail_edge":"#565048",
    "ballast":"#655c58",
    "sleepers":"#433b39",
    "rail":"#b2a69a",
}

def validated_palette(raw):
    result=dict(DEFAULT_PALETTE)
    if not isinstance(raw,dict):
        return result
    for key in result:
        value=raw.get(key)
        if (isinstance(value,str) and len(value)==7 and value[0]=="#"
                and all(c in "0123456789abcdefABCDEF" for c in value[1:])):
            result[key]=value
    return result

def _visible_segments(points,viewport):
    # Expand clip boundary by enough to avoid abrupt wide-stroke cut-offs.
    cx,cy,w,h=viewport
    expanded=(cx-90,cy-90,w+180,h+180)
    for a,b in zip(points,points[1:]):
        segment=clip_segment(a,b,expanded)
        if segment:
            yield segment

def _segment(canvas,a,b,viewport,color,width,offset=0,dash=None):
    camx,camy,_,_=viewport
    x1,y1=a[0]-camx,a[1]-camy
    x2,y2=b[0]-camx,b[1]-camy
    if offset:
        length=math.hypot(x2-x1,y2-y1)
        if length<=1e-7:return
        ox=-(y2-y1)*offset/length
        oy=(x2-x1)*offset/length
        x1+=ox;x2+=ox;y1+=oy;y2+=oy
    opts={"fill":color,"width":width,"capstyle":"round","tags":("gfx06_route",)}
    if dash:opts["dash"]=dash
    canvas.create_line(x1,y1,x2,y2,**opts)

def _paint_polyline(canvas,points,view,palette,kind):
    for a,b in _visible_segments(points,view):
        if kind=="primary":
            layers=((126,"shoulder"),(102,"road"),(76,"center"))
            for width,key in layers:
                _segment(canvas,a,b,view,palette[key],width)
            # Two thin wheel ruts; these do not become physical barriers.
            for offset in (-27,27):
                _segment(canvas,a,b,view,palette["ruts"],3,offset,(13,16))
        elif kind=="secondary":
            for width,key in ((84,"shoulder"),(60,"road"),(36,"center")):
                _segment(canvas,a,b,view,palette[key],width)
            for offset in (-14,14):
                _segment(canvas,a,b,view,palette["ruts"],2,offset,(12,18))
        elif kind=="trail":
            for width,key in ((35,"trail_edge"),(19,"trail")):
                _segment(canvas,a,b,view,palette[key],width)
            _segment(canvas,a,b,view,palette["ruts"],2,0,(8,16))
        elif kind=="rail":
            # Sleeper dashes are drawn BEFORE continuous steel rails.
            # A single path source prevents disconnected tracks, and round
            # endpoint strokes prevent cosmetic breaks at authored vertices.
            _segment(canvas,a,b,view,palette["ballast"],34)
            _segment(canvas,a,b,view,palette["sleepers"],34,0,(4,15))
            for offset in (-9,9):
                _segment(canvas,a,b,view,palette["rail"],3,offset)

def draw_forsaken_routes(canvas,camx,camy,width,height,palette=None):
    """Replace legacy route strokes exactly once, before bridge decks/towns."""
    view=(camx,camy,width,height)
    pal=validated_palette(palette)
    for points in ROADS:
        _paint_polyline(canvas,points,view,pal,"primary")
    for _,points in SECONDARY_ROADS:
        _paint_polyline(canvas,points,view,pal,"secondary")
    for _,_,_,points in TRAILS:
        _paint_polyline(canvas,points,view,pal,"trail")
    for points in RAILS:
        _paint_polyline(canvas,points,view,pal,"rail")
