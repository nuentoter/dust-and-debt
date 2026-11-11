"""Unified world-space transport overlays for atlas and local minimap.

The source route positions come from new_austellia. Screen projection is
clipped to the requested world view, avoiding phantom straight-line grids.
Tkinter only; no large image textures or external graphics requirements.
"""
from new_austellia import ROADS,RAILS,SECONDARY_ROADS,TRAILS,START_SPUR

def clip_segment(a,b,view):
    """Liang-Barsky world-space clipping to (x,y,width,height)."""
    ox,oy,w,h=view
    xmin,ymin,xmax,ymax=ox,oy,ox+w,oy+h
    dx=b[0]-a[0];dy=b[1]-a[1]
    t0=0.;t1=1.
    for p,q in ((-dx,a[0]-xmin),(dx,xmax-a[0]),
                (-dy,a[1]-ymin),(dy,ymax-a[1])):
        if abs(p)<1e-10:
            if q<0:return None
            continue
        r=q/p
        if p<0:t0=max(t0,r)
        else:t1=min(t1,r)
        if t0>t1:return None
    return ((a[0]+t0*dx,a[1]+t0*dy),
            (a[0]+t1*dx,a[1]+t1*dy))

def draw_scaled_routes(canvas,view,rect,detail="normal",include_primary=True):
    """Draw real route polylines consistently over the full map and radar."""
    ox,oy,vw,vh=view
    rx,ry,rw,rh=rect
    def project(point):
        return (rx+(point[0]-ox)*rw/vw,ry+(point[1]-oy)*rh/vh)
    layers=[]
    if include_primary:
        layers.extend((points,"#9c7656",2,None,()) for points in ROADS)
    layers.extend((points,"#b48d61",1.5,None,()) for _,points in SECONDARY_ROADS)
    layers.extend((points,"#8b795c",1,(3,4),()) for _,_,_,points in TRAILS)
    if include_primary:
        layers.extend((points,"#8d5448",2,None,()) for points in RAILS)
    layers.append((START_SPUR,"#b48d61",1.5,None,('starter_spur',)))
    for points,color,width,dash,tags in layers:
        for a,b in zip(points,points[1:]):
            clipped=clip_segment(a,b,view)
            if clipped is None:continue
            pa,pb=map(project,clipped)
            opts={"fill":color,"width":width}
            if dash:opts["dash"]=dash
            if tags:opts["tags"]=tags
            canvas.create_line(*pa,*pb,**opts)


def draw_starter_spur(canvas,camx,camy,width,height):
    """Preserve world strokes and dash phase while sharing canonical vertices."""
    a,b=START_SPUR
    if (max(a[0],b[0])<camx-20 or min(a[0],b[0])>camx+width+20 or
        max(a[1],b[1])<camy-20 or min(a[1],b[1])>camy+height+20):return
    coords=(a[0]-camx,a[1]-camy,b[0]-camx,b[1]-camy)
    canvas.create_line(*coords,fill='#b9a276',width=38,tags=('starter_spur',))
    canvas.create_line(*coords,fill='#d3b789',width=2,dash=(12,16),tags=('starter_spur',))
