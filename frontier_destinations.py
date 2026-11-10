"""Authored walkable fishing banks and established camp pads (v2.9-map).

Source positions live in New Austellia TRAILS_SRC. World positions here
derive from their final trail vertex; no random or screen-space placement.
"""
from dataclasses import dataclass
from new_austellia import TRAILS, is_water

@dataclass(frozen=True)
class Destination:
    id:str
    kind:str
    name:str
    x:float
    y:float
    trailhead:tuple
    route:tuple

DESTINATIONS=tuple(
    Destination(key,kind,name,pts[-1][0],pts[-1][1],pts[0],pts)
    for key,kind,name,pts in TRAILS
)
DESTINATION_BY_ID={p.id:p for p in DESTINATIONS}

def fishing_spots():
    return tuple(d for d in DESTINATIONS if d.kind=="fishing")

def campsites():
    return tuple(d for d in DESTINATIONS if d.kind=="camp")

def destinations_in_view(camx,camy,width,height,pad=170):
    return (d for d in DESTINATIONS
            if camx-pad<d.x<camx+width+pad
            and camy-pad<d.y<camy+height+pad)

def draw_destinations(canvas,camx,camy,width,height,detail="normal"):
    """Camera-cull decorative pads. Never create invisible collision shapes."""
    for site in destinations_in_view(camx,camy,width,height):
        x,y=site.x-camx,site.y-camy
        if site.kind=="camp":
            canvas.create_oval(x-69,y-35,x+69,y+37,fill="#a58c68",outline="#786449",width=3)
            canvas.create_polygon(x-44,y+15,x-11,y-33,x+19,y+15,
                                  fill="#bfa77e",outline="#64503a",width=3)
            canvas.create_line(x-11,y-33,x-11,y+15,fill="#e2c99b",width=2)
            canvas.create_oval(x+28,y-5,x+47,y+14,fill="#665644",outline="#32291e",width=2)
            canvas.create_polygon(x+31,y+5,x+37,y-13,x+44,y+5,fill="#efae59",outline="")
            if detail=="normal":
                canvas.create_line(x-64,y+23,x-37,y+20,fill="#63513c",width=5)
                canvas.create_oval(x-54,y+9,x-42,y+15,fill="#7b765c",outline="")
            label="CAMP"
            tint="#f1d49c"
        else:
            canvas.create_oval(x-46,y-18,x+46,y+22,fill="#b4a17f",outline="#83765e",width=2)
            for offset in (-23,-2,17):
                canvas.create_line(x+offset,y+12,x+offset-5,y-5,fill="#768462",width=3)
            canvas.create_line(x-26,y-2,x+28,y-2,fill="#62513f",width=3)
            label="FISHING"
            tint="#b7e2d6"
        if detail=="normal":
            canvas.create_text(x,y-64,text=label+"  "+site.name.upper(),
                               fill=tint,font=("DejaVu Sans",8,"bold"))

def draw_destination_map(canvas,project,view_all=True):
    """Draw small markers using caller's world->screen projection."""
    for site in DESTINATIONS:
        p=project(site.x,site.y)
        if not p:continue
        x,y=p
        if site.kind=="camp":
            canvas.create_polygon(x-3,y+3,x,y-4,x+3,y+3,fill="#a66b3e",outline="#593f2e")
        else:
            canvas.create_oval(x-3,y-3,x+3,y+3,fill="#548f9d",outline="#28515d")
