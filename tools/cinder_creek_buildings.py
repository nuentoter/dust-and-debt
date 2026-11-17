"""GFX-02 procedural Western building art, baked offline with Pillow.

Renders richer roof, frontage, porch and signage surfaces into existing building
rectangles. No doors, collision rectangles or gameplay geometry are moved.
Source positions come from the game's preserved starter-area layout.
"""
import random
from PIL import Image, ImageDraw, ImageFont
from cinder_creek_gfx import STARTER_BUILDINGS

SCHEMES = {
    "Sheriff": ("#635b59", "#827a71", "#4a3d36", "#c4ae86"),
    "Saloon": ("#78473a", "#a5684b", "#57362f", "#edbc83"),
    "General Store": ("#77704f", "#a29968", "#514a37", "#d9c28c"),
    "Doctor": ("#8c8574", "#c1b7a0", "#61574e", "#ede0bb"),
    "Stable": ("#62513d", "#89704d", "#47392d", "#d3b57b"),
    "Hotel": ("#745c54", "#a08270", "#503a37", "#e7c48f"),
    "Station": ("#625448", "#947961", "#4d3c32", "#dec399"),
    "Cabin": ("#695743", "#987b5b", "#463a2e", "#d8ba82"),
    "Outpost": ("#694c3e", "#956950", "#48382d", "#d4b282"),
    "Ranch": ("#6c6048", "#9d8962", "#493c30", "#e0c38f"),
}

def _font(size):
    for font in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(font, size)
        except OSError:
            pass
    return ImageFont.load_default()

def _rect(d, xy, fill, outline=None, width=1):
    d.rectangle(tuple(map(int,xy)), fill=fill, outline=outline, width=width)

def _text_center(d, cx, y, message, max_width, color):
    size=min(16,max(9,int(max_width/max(1,len(message))*.95)))
    while size>9:
        f=_font(size)
        box=d.textbbox((0,0),message,font=f,stroke_width=0)
        if box[2]-box[0] <= max_width:break
        size-=1
    f=_font(size)
    box=d.textbbox((0,0),message,font=f)
    d.text((int(cx-(box[2]-box[0])/2),int(y)),message,font=f,fill=color,
           stroke_width=1,stroke_fill="#30251f")

def _window(d,x,y,scheme):
    dark,light,trim,accent=scheme
    _rect(d,(x-14,y-11,x+14,y+12),trim)
    _rect(d,(x-10,y-8,x+10,y+8),"#343d3d")
    _rect(d,(x-8,y-7,x-1,y+6),"#879b96")
    d.line((x+1,y-7,x+1,y+8),fill=accent,width=2)
    d.line((x-11,y+1,x+11,y+1),fill=trim,width=2)
    _rect(d,(x-17,y+11,x+17,y+15),light)

def _roof(d,x,y,w,h,scheme,seed):
    dark,light,trim,accent=scheme
    rng=random.Random(seed)
    # Heavy eave, shadow and highlighted roof edge.
    _rect(d,(x+4,y+7,x+w-2,y+h-3),"#342e2a")
    _rect(d,(x+4,y+3,x+w-6,y+h-11),trim)
    _rect(d,(x+10,y+8,x+w-12,y+h-17),dark)
    # Pixelated roof courses, staggered shingle edges and sparse worn patches.
    roof_bottom=y+h-18
    for yy in range(y+13,roof_bottom,10):
        offset=0 if ((yy-y)//10)%2 else 11
        d.line((x+11,yy,x+w-13,yy),fill=light,width=2)
        for xx in range(x+13+offset,x+w-17,22):
            d.line((xx,yy,xx,yy+7),fill=trim,width=2)
        for _ in range(max(1,w//28)):
            xx=rng.randrange(x+12,x+w-12)
            d.line((xx,yy+4,xx+rng.randint(2,7),yy+4),fill=light,width=1)
    d.line((x+9,y+11,x+w-14,y+11),fill=accent,width=3)
    d.line((x+10,roof_bottom,x+w-12,roof_bottom),fill="#302820",width=5)

def _porch(d,x,y,w,h,scheme):
    dark,light,trim,accent=scheme
    # A narrow overhang remains inside the existing collision footprint.
    top=y+h-43
    _rect(d,(x+10,top,x+w-11,y+h-4),trim)
    _rect(d,(x+14,top+4,x+w-15,y+h-9),light)
    for py in range(top+5,y+h-11,8):
        d.line((x+15,py,x+w-16,py),fill=dark,width=2)
    # Porch rail posts / wooden support columns.
    for xx in (x+17,x+w-19):
        _rect(d,(xx-4,top-9,xx+3,y+h-7),trim)
        d.line((xx-2,top-9,xx-2,y+h-8),fill=accent,width=2)
    d.line((x+12,y+h-9,x+w-12,y+h-9),fill="#403329",width=4)

def _front(d,x,y,w,h,name,scheme):
    dark,light,trim,accent=scheme
    front_y=y+h-55
    _rect(d,(x+12,front_y,x+w-13,y+h-14),trim)
    _rect(d,(x+18,front_y+5,x+w-19,y+h-18),light)
    # Vertical clapboards on an otherwise horizontal roof, so the façade
    # reads as a front-facing Western shop rather than a flat rectangle.
    for xx in range(x+22,x+w-20,13):
        d.line((xx,front_y+7,xx,y+h-18),fill=dark,width=2)
    cx=x+w//2
    door_w=23 if name not in ("Stable","Station") else 35
    _rect(d,(cx-door_w,front_y+13,cx+door_w,y+h-11),trim)
    _rect(d,(cx-door_w+4,front_y+17,cx+door_w-4,y+h-11),"#292823")
    d.line((cx+door_w-8,front_y+20,cx+door_w-8,y+h-14),fill=accent,width=2)
    if w>=160:
        for wx in (x+43,x+w-43):
            if abs(wx-cx)>door_w+21:
                _window(d,wx,front_y+24,scheme)
    # Top-down false-front sign above the actual lower-facing entrance.
    sign_top=front_y-23
    _rect(d,(x+16,sign_top,x+w-17,front_y+2),trim)
    _rect(d,(x+20,sign_top+3,x+w-21,front_y-2),dark)
    _text_center(d,cx,sign_top+5,name.upper(),w-54,accent)

def _stable_details(d,x,y,w,h,scheme):
    _,light,trim,accent=scheme
    for xx in range(x+32,x+w-18,36):
        d.line((xx,y+22,xx+11,y+42),fill=trim,width=3)
        d.line((xx+11,y+22,xx,y+42),fill=accent,width=2)
    _rect(d,(x+14,y+h-63,x+41,y+h-48),accent,outline=trim,width=2)

def _station_details(d,x,y,w,h,scheme):
    dark,light,trim,accent=scheme
    for xx in range(x+22,x+w-20,22):
        d.line((xx,y+h-17,xx+5,y+h-10),fill=accent,width=2)
    d.line((x+8,y+h-10,x+w-8,y+h-10),fill="#3a3029",width=4)
    _rect(d,(x+w-63,y+21,x+w-25,y+40),trim)
    _rect(d,(x+w-59,y+25,x+w-29,y+36),light)

def _special(d,x,y,w,h,name,scheme):
    if name=="Stable":_stable_details(d,x,y,w,h,scheme)
    if name=="Station":_station_details(d,x,y,w,h,scheme)
    if name=="Sheriff":
        _text_center(d,x+w//2,y+18,"★",w-48,scheme[3])
    if name=="Doctor":
        cx=x+w//2
        _rect(d,(cx-5,y+16,cx+5,y+45),"#9e4437")
        _rect(d,(cx-16,y+25,cx+16,y+35),"#9e4437")

def paint_buildings(image, buildings=STARTER_BUILDINGS):
    """Return count of landmark buildings redrawn; paint within old footprints."""
    if image.mode != "RGB":
        raise ValueError("Baked world artwork must be RGB")
    draw=ImageDraw.Draw(image)
    count=0
    for index,(name,x,y,w,h) in enumerate(buildings):
        if name not in SCHEMES:
            raise ValueError("No building art scheme for "+name)
        if x<0 or y<0 or x+w>image.width or y+h>image.height:
            raise ValueError("Building extends beyond source map: "+name)
        scheme=SCHEMES[name]
        _roof(draw,x,y,w,h,scheme,1889+index*101)
        _porch(draw,x,y,w,h,scheme)
        _front(draw,x,y,w,h,name,scheme)
        _special(draw,x,y,w,h,name,scheme)
        count+=1
    return count
