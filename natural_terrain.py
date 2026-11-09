"""Natural Terrain: deterministic, camera-local New Austellia landforms.

All coordinates use the existing illustrated atlas's 60,000 x 40,960 world.
No runtime images, third-party modules, dynamic RNG or terrain-sized arrays.
Named water and bridge collision stays in new_austellia.py.
"""
import math
from new_austellia import P,REGIONS,TOWNS,WATERWAYS,near_atlas_town,is_water
from frontier_world import biome_at,road_at,BIOME_PALETTES

SEED=1889
# Long, hand-placed ridges in atlas source pixels. Endpoints and bends follow
# uplands, NOT the historic town/rail/river sites.
RIDGES_SRC=(
 ("Graystone West",((210,190),(280,205),(339,238),(392,263))),
 ("Graystone East",((430,210),(476,236),(522,262),(560,303))),
 ("Cinder Uplands",((74,267),(119,301),(170,345),(201,373))),
 ("Iron Mesa Rim",((72,438),(110,469),(139,513),(186,544))),
 ("Red Thorn Escarpment",((222,533),(250,575),(297,606),(324,635))),
 ("Sundown Edge",((44,677),(91,711),(131,734),(179,757))),
 ("Copper Divide",((172,824),(221,851),(270,884),(317,905))),
 ("Red Mesa North",((506,701),(532,719),(574,739),(601,747))),
 ("Red Mesa South",((544,856),(585,871),(617,882),(658,894))),
 ("Northridge Spine",((834,78),(873,113),(921,131),(954,165))),
 ("Cedarheart Bluff",((1280,396),(1314,418),(1341,453),(1360,480))),
 ("Highfall Rise",((1190,170),(1245,201),(1284,238),(1321,266))),
)
RIDGES=tuple((name,tuple(P(*p) for p in pts)) for name,pts in RIDGES_SRC)
# Many small rock-fields near mapped uplands: anchors do not imply barriers.
BOULDER_FIELDS=tuple(
 (x,y,seed) for ri,(_,ridge) in enumerate(RIDGES)
 for j,(x,y) in enumerate(ridge[1:-1])
 for seed in (ri*13+j*7,ri*13+j*7+101)
)
# Three tributary / dry wash networks tie to existing waterways, with some
# extra dry gully features; no new unbridged impassable water is introduced.
WASHES_SRC=(
 ((190,160),(210,210),(229,262),(244,313)),
 ((517,295),(477,339),(432,409),(392,533)),
 ((930,390),(929,447),(929,513),(934,581)),
 ((1190,552),(1151,603),(1105,649),(1072,663)),
 ((548,712),(523,750),(501,778),(493,799)),
 ((345,678),(369,722),(385,759),(415,788)),
 ((736,715),(748,743),(750,784)),
 ((1352,680),(1305,711),(1260,744),(1197,731)),
)
WASHES=tuple(tuple(P(*v) for v in points) for points in WASHES_SRC)

def hash32(x,y):
    n=(int(x)*73856093 ^ int(y)*19349663 ^ SEED*83492791)&0xffffffff
    n=(n^(n>>13))*1274126177&0xffffffff
    return n^(n>>16)

def smooth(t):
    return t*t*(3-2*t)

def noise(x,y,scale=1300):
    """Value noise, coherent between samples without visible square jumps."""
    gx=int(math.floor(x/scale));gy=int(math.floor(y/scale))
    u=smooth(x/scale-gx);v=smooth(y/scale-gy)
    def val(a,b):return (hash32(a,b)%10000)/9999.0
    a=val(gx,gy)*(1-u)+val(gx+1,gy)*u
    b=val(gx,gy+1)*(1-u)+val(gx+1,gy+1)*u
    return a*(1-v)+b*v

def biome_blend(x,y):
    """Two nearby atlas biomes, with coherent irregular transitions."""
    wobble_x=(noise(x,y,3000)-.5)*1750
    wobble_y=(noise(x+9831,y-7401,3400)-.5)*1750
    scored=sorted(REGIONS,key=lambda r:((x+wobble_x-r[1])**2+
                   (y+wobble_y-r[2])**2)/max(.2,r[4]**2))
    first,second=scored[:2]
    d1=math.hypot(x+wobble_x-first[1],y+wobble_y-first[2])/first[4]
    d2=math.hypot(x+wobble_x-second[1],y+wobble_y-second[2])/second[4]
    return first[3],second[3],max(0.,min(.42,(d1/max(1,d1+d2))*.7))

def color_mix(a,b,t):
    aa=tuple(int(a[i:i+2],16) for i in (1,3,5))
    bb=tuple(int(b[i:i+2],16) for i in (1,3,5))
    return '#'+''.join('%02x'%round(x*(1-t)+y*t) for x,y in zip(aa,bb))

def ground_color(x,y):
    primary,secondary,mix=biome_blend(x,y)
    a=BIOME_PALETTES[primary][0];b=BIOME_PALETTES[secondary][0]
    return color_mix(a,b,mix)

def near_protected(x,y,margin=150):
    """No ridges or major rocks on roads, rails, bridges, plazas, old map."""
    if x<4950 and y<3350:return True
    if near_atlas_town(x,y,450+margin):return True
    # The vintage regional road grid survives temporarily near Cinder Creek.
    if road_at(x,y):return True
    if is_water(x,y):return True
    return False

def rock_positions():
    """Fixed clusters in broad uplands; stable across sessions and camera pans."""
    for cx,cy,seed in BOULDER_FIELDS:
        for n in range(7):
            h=hash32(seed,n)
            angle=(h%6283)/1000
            radius=65+(h//43%270)
            x=cx+math.cos(angle)*radius
            y=cy+math.sin(angle)*radius
            size=13+(h//97%27)
            yield (x,y,size,n==0 or n==3)

# Cache modest number of deterministic rocks once, not a world-size grid.
ROCKS=tuple((x,y,r,solid) for x,y,r,solid in rock_positions()
            if not near_protected(x,y,r+135))

def landform_solid(x,y,radius=11):
    # Broad cliff contours are currently traversable; major rocks alone
    # collide. Only check expensive road/water protections near actual rocks.
    for rx,ry,rr,solid in ROCKS:
        if solid and abs(x-rx)<=rr+radius and abs(y-ry)<=rr+radius:
            if (x-rx)**2+(y-ry)**2<(rr+radius)**2:
                return not near_protected(x,y,radius+24)
    return False

def _visible(x,y,camx,camy,w,h,pad=120):
    return camx-pad<x<camx+w+pad and camy-pad<y<camy+h+pad

def draw_ground(canvas,camx,camy,width,height):
    """Overlapping low-frequency color fields, not square biome tiles."""
    canvas.create_rectangle(0,0,width,height,fill='#af9c77',outline='')
    # Large, staggered elliptical swaths bleed across every underlying cell.
    cell=440
    ix0=int(camx//cell)-2;ix1=int((camx+width)//cell)+3
    iy0=int(camy//cell)-2;iy1=int((camy+height)//cell)+3
    for gy in range(iy0,iy1):
        for gx in range(ix0,ix1):
            h=hash32(gx,gy)
            wx=(gx+.5+(gy%2)*.5)*cell+(h%61-30)
            wy=(gy+.5)*cell+((h//61)%67-33)
            sx=wx-camx;sy=wy-camy
            rx=370+(h%90);ry=320+(h//17%100)
            color=ground_color(wx,wy)
            canvas.create_oval(sx-rx,sy-ry,sx+rx,sy+ry,fill=color,outline='')
            # Loose stippled hills/scrub contours avoid repeating square motifs.
            if h%3==0:
                canvas.create_arc(sx-rx*.55,sy-ry*.46,sx+rx*.7,sy+ry*.5,
                                  start=30,extent=110,style='arc',outline='#9a886a',width=2)

def draw_landforms(canvas,camx,camy,width,height):
    """Contour bands, gravel fields, dry wash traces, and boulders."""
    for name,pts in RIDGES:
        # Draw only a ridge segment near the camera.
        for a,b in zip(pts,pts[1:]):
            if max(a[0],b[0])<camx-400 or min(a[0],b[0])>camx+width+400:continue
            if max(a[1],b[1])<camy-400 or min(a[1],b[1])>camy+height+400:continue
            ax,ay=a[0]-camx,a[1]-camy;bx,by=b[0]-camx,b[1]-camy
            canvas.create_line(ax,ay,bx,by,fill='#776b5a',width=230,capstyle='round')
            canvas.create_line(ax,ay,bx,by,fill='#a78967',width=194,capstyle='round')
            canvas.create_line(ax-12,ay-28,bx-12,by-28,fill='#c0a27e',width=135,capstyle='round')
            canvas.create_line(ax-10,ay-31,bx-10,by-31,fill='#d0b38c',width=4)
    for pts in WASHES:
        for a,b in zip(pts,pts[1:]):
            if max(a[0],b[0])<camx-80 or min(a[0],b[0])>camx+width+80:continue
            if max(a[1],b[1])<camy-80 or min(a[1],b[1])>camy+height+80:continue
            ax,ay=a[0]-camx,a[1]-camy;bx,by=b[0]-camx,b[1]-camy
            canvas.create_line(ax,ay,bx,by,width=36,fill='#987b61',capstyle='round')
            canvas.create_line(ax,ay,bx,by,width=17,fill='#c2a583',capstyle='round')
    for rx,ry,rad,solid in ROCKS:
        if not _visible(rx,ry,camx,camy,width,height,rad+15):continue
        x=rx-camx;y=ry-camy
        canvas.create_oval(x-rad*.95,y-rad*.25,x+rad*1.1,y+rad*.52,
                           fill='#73695b',outline='')
        canvas.create_polygon(x-rad,y,x-rad*.6,y-rad*.62,x+rad*.38,y-rad*.81,
                              x+rad,y-rad*.11,x+rad*.65,y+rad*.38,
                              x-rad*.63,y+rad*.32,fill='#918778',outline='#5f5b51',width=2)
        canvas.create_line(x-rad*.61,y-rad*.52,x+rad*.29,y-rad*.7,
                           fill='#c2b39b',width=2)
