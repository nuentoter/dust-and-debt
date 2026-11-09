"""New Austellia cartography traced from the user's illustrated 1898 map.

Source image: 'Vintage Map of the Frontier Lands.png', 1448x1086.
Atlas landmarks use source-image pixel coordinates projected into the existing
60,000x40,960 world. Source image remains the authoritative geographic design.
This module uses only math and Tk canvas; no Pillow required at runtime.
"""
import math

MAP_WIDTH,MAP_HEIGHT=1448.,1086.
WORLD_WIDTH,WORLD_HEIGHT=60000.,40960.
def P(x,y):return (round(x*WORLD_WIDTH/MAP_WIDTH),round(y*WORLD_HEIGHT/MAP_HEIGHT))
def path(points):return tuple(P(*v) for v in points)

# id, label, atlas x,y, type. These are geographically keyed, not random sites.
TOWNS_SRC=(
 ("galloway","Galloway",442,393,"town"),
 ("saints_hollow","Saint's Hollow",755,281,"town"),
 ("roan_creek","Roan Creek",1057,306,"town"),
 ("hollow_bend","Hollow Bend",1083,404,"post"),
 ("blackwater_crossing","Blackwater Crossing",648,515,"city"),
 ("larkfield","Larkfield",883,506,"town"),
 ("harpers_landing","Harper's Landing",1049,607,"town"),
 ("valleyford","Valleyford",811,662,"town"),
 ("dustwell","Dustwell",415,788,"town"),
 ("riversend","Riversend",700,835,"town"),
 ("saint_brigids","Saint Brigid's Port",819,891,"port"),
 ("bayou_haven","Bayou Haven",1209,746,"town"),
 ("elmshade","Elmshade",1313,473,"settlement"),
 ("pineheart","Pineheart Trading Post",1157,142,"post"),
 ("cinder_ridge","Cinder Ridge Camp",175,276,"mine"),
 ("silvervein","Silvervein Mine",549,232,"mine"),
 ("iron_mesa","Iron Mesa Fort",226,493,"fort"),
 ("stonewall","Stonewall Fort",376,552,"fort"),
 ("brimstone","Brimstone Point",69,587,"post"),
 ("bearclaw","Bearclaw Lookout",1315,566,"tower"),
 ("mercy_flats","Mercy Flats Ranch",605,397,"ranch"),
 ("prairie_view","Prairie View Ranch",658,633,"ranch"),
 ("black_rock","Black Rock Ranch",507,669,"ranch"),
 ("rattlers_rest","Rattler's Rest",288,759,"ruin"),
 ("old_kestrel","Old Kestrel Mill",1031,803,"ruin"),
 ("widows_pass","Widow's Pass",705,76,"pass"),
 ("silver_mine","Lone Pine Mine",562,726,"mine"),
 ("frostvein_lake","Frostvein Lake",503,146,"lake"),
 ("northstar_lake","Northstar Lake",960,247,"lake"),
 ("highfalls","Highfalls",1203,282,"waterfall"),
 ("driftwood_springs","Driftwood Springs",449,484,"spring"),
 ("calhoun_island","Calhoun Island",1057,940,"island"),
 ("herons_key","Heron's Key",1143,965,"island"),
 ("drake_isles","Drake Isles",1327,928,"island"),
)
TOWNS=tuple((key,name,*P(x,y),kind) for key,name,x,y,kind in TOWNS_SRC)
TOWN_BY_ID={t[0]:t for t in TOWNS}
MAJOR_TOWNS=frozenset(("galloway","saints_hollow","roan_creek","blackwater_crossing",
  "larkfield","harpers_landing","valleyford","dustwell","riversend","saint_brigids",
  "bayou_haven","elmshade"))
# Regions follow the geographic placement on the user's atlas, rather than
# the old rectangle names. Smooth nearest-center classification is cheap.
REGIONS_SRC=(
 ("Glacier Peaks",470,73,"mountain",1.05),
 ("Graystone Range",405,272,"mountain",1.00),
 ("Cinder Ridge Badlands",130,337,"canyon",1.03),
 ("Iron Mesa",164,487,"mesa",.74),
 ("Red Thorn Canyon",267,561,"canyon",.80),
 ("Northridge Territory",895,104,"scrub",1.1),
 ("Everwood Forest",1084,213,"forest",1.0),
 ("Cedarheart Woods",1230,479,"forest",.9),
 ("Heartland Plains",766,384,"grass",1.1),
 ("Sablestone Territory",318,613,"scrub",1.0),
 ("Sundown Plateau",152,698,"mesa",.76),
 ("Copper Sands Desert",250,822,"desert",1.1),
 ("Red Mesa Buttes",593,788,"mesa",.7),
 ("Cypress Bayou",1066,711,"lake",1.05),
 ("Auburn Gulf",919,970,"lake",1.1),
)
REGIONS=tuple((name,*P(x,y),biome,weight) for name,x,y,biome,weight in REGIONS_SRC)
BIOME_COLORS={"mountain":"#938a7b","forest":"#7e906e","scrub":"#b2a078",
              "canyon":"#ad7d65","mesa":"#bd8f6b","grass":"#acaa75",
              "desert":"#d1b07b","lake":"#85a8a6","prairie":"#b9a57c"}
# Hydrology: geographic rivers rather than the previous straight grid.
WATERWAYS_SRC=(
 ("Sable River",((244,313),(266,362),(300,396),(325,440),(315,478),(353,507),(392,533),(448,536),(494,514),(548,501),(607,508),(648,515)),180),
 ("Blackwater River",((640,22),(663,95),(657,156),(635,202),(651,267),(668,337),(664,408),(656,460),(648,515),(705,541),(759,550),(829,566),(880,568),(934,581),(986,588),(1048,608),(1072,663),(1115,696),(1197,731),(1270,779),(1391,834)),210),
 ("Roan Creek",((1180,26),(1145,93),(1156,158),(1196,227),(1210,287),(1181,353),(1124,398),(1084,404),(1066,466),(1043,533),(1048,608)),170),
 ("Riversend Channel",((866,566),(849,632),(825,684),(786,742),(750,784),(700,835),(680,902),(665,970)),210),
 ("Dustwell Wash",((295,790),(340,790),(415,788),(493,799),(561,807),(623,818),(700,835)),120),
)
WATERWAYS=tuple((name,path(points),width) for name,points,width in WATERWAYS_SRC)
LAKES_SRC=(("Frostvein Lake",505,148,45,23),("Northstar Lake",971,244,71,34))
LAKES=tuple((name,*P(x,y),round(rx*WORLD_WIDTH/MAP_WIDTH),round(ry*WORLD_HEIGHT/MAP_HEIGHT)) for name,x,y,rx,ry in LAKES_SRC)
# Red railroad routes and brown wagon trails: traced routes with intermediate bends.
RAILS_SRC=(
 ((441,392),(505,376),(569,366),(636,336),(694,293),(754,281),(823,293),(894,330),(960,338),(1033,321),(1057,306)),
 ((442,392),(478,410),(518,455),(566,482),(606,508),(648,515),(728,521),(799,523),(852,511),(883,506),(935,547),(991,574),(1049,607),(1123,628),(1175,681),(1209,746)),
 ((648,515),(596,550),(533,586),(472,643),(441,699),(415,746),(415,788),(488,802),(572,803),(647,812),(700,835),(774,851),(819,891)),
 ((883,506),(904,559),(901,607),(853,643),(811,662),(764,700),(744,761),(700,835)),
)
RAILS=tuple(path(p) for p in RAILS_SRC)
ROADS_SRC=(
 ((178,277),(256,309),(315,329),(370,356),(442,392)),
 ((549,232),(568,278),(600,324),(648,370),(648,515)),
 ((705,77),(707,157),(755,281)),
 ((1157,142),(1150,209),(1166,264),(1057,306)),
 ((1057,306),(1102,361),(1083,404),(1124,442),(1189,464),(1313,473)),
 ((1083,404),(1091,481),(1049,607)),
 ((442,392),(438,453),(449,484),(424,538),(376,552),(344,613)),
 ((376,552),(328,599),(288,650),(288,759),(415,788)),
 ((648,515),(657,565),(658,633),(705,653),(811,662)),
 ((1050,607),(1080,669),(1127,729),(1209,746)),
 ((1049,607),(1001,674),(1031,803)),
 ((700,835),(625,758),(562,726),(507,669)),
 ((1313,473),(1325,531),(1315,566),(1329,645),(1209,746)),
)
ROADS=tuple(path(p) for p in ROADS_SRC)

def place(key):
 return TOWN_BY_ID.get(key)

def region_at(x,y):
 # Keep geographic boundaries at least loosely shaped, not a chessboard.
 return min(REGIONS,key=lambda r:((x-r[1])**2+(y-r[2])**2)/(r[4]**2))[0]

def biome_at(x,y):
 return min(REGIONS,key=lambda r:((x-r[1])**2+(y-r[2])**2)/(r[4]**2))[3]

def distance_to_segment(px,py,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1]
 if not dx and not dy:return math.hypot(px-a[0],py-a[1])
 t=max(0.,min(1.,((px-a[0])*dx+(py-a[1])*dy)/(dx*dx+dy*dy)))
 return math.hypot(px-a[0]-dx*t,py-a[1]-dy*t)

def near_polyline(x,y,points,radius):
 for i in range(len(points)-1):
  a,b=points[i:i+2]
  if min(a[0],b[0])-radius<=x<=max(a[0],b[0])+radius and min(a[1],b[1])-radius<=y<=max(a[1],b[1])+radius:
   if distance_to_segment(x,y,a,b)<=radius:return True
 return False

def travel_road(x,y):
 return any(near_polyline(x,y,route,90) for route in ROADS+RAILS)

def river_at(x,y):
 # Primary named waterways. Additional narrow streams remain purely decorative.
 for name,points,width in WATERWAYS:
  if near_polyline(x,y,points,width):return name
 return None

def lake_at(x,y):
 for name,lx,ly,rx,ry in LAKES:
  if ((x-lx)/rx)**2+((y-ly)/ry)**2<=1:return name
 return None

def coastal_water(x,y):
 # Illustrated gulf boundary bends up along the eastern bayou coast.
 source_x=x*MAP_WIDTH/WORLD_WIDTH
 source_y=y*MAP_HEIGHT/WORLD_HEIGHT
 coast=((0,1086),(380,1010),(530,967),(650,895),(720,887),
        (820,904),(930,841),(1110,811),(1240,829),(1448,777))
 for a,b in zip(coast,coast[1:]):
  if a[0]<=source_x<=b[0]:
   k=(source_x-a[0])/(b[0]-a[0])
   return source_y>a[1]+k*(b[1]-a[1])+8
 return False

def ford_at(x,y):
 # Caravans cross mapped waterways at roads/railroad bridge positions.
 return travel_road(x,y)

def is_water(x,y):
 if x<4800 and y<3200:return False  # old authored Cinder Creek parcel
 # Settlement platforms and station approaches are raised above floodwater.
 if near_atlas_town(x,y,230) is not None:return False
 if ford_at(x,y):return False
 return coastal_water(x,y) or bool(lake_at(x,y)) or bool(river_at(x,y))

def near_atlas_town(x,y,radius=420):
 for key,name,tx,ty,kind in TOWNS:
  if math.hypot(tx-x,ty-y)<radius:return key
 return None

def draw_local_geography(canvas,camx,camy,width,height):
 """Only draw river/coast/road segments intersecting the camera viewport."""
 def visible(a,b,pad=450):
  return (max(a[0],b[0])>=camx-pad and min(a[0],b[0])<=camx+width+pad and
          max(a[1],b[1])>=camy-pad and min(a[1],b[1])<=camy+height+pad)
 def xy(pt):return (pt[0]-camx,pt[1]-camy)
 for name,points,w in WATERWAYS:
  for a,b in zip(points,points[1:]):
   if not visible(a,b):continue
   x1,y1=xy(a);x2,y2=xy(b)
   canvas.create_line(x1,y1,x2,y2,width=w*2.2,fill="#748e87")
   canvas.create_line(x1,y1,x2,y2,width=w*1.65,fill="#729da0")
 for name,lx,ly,rx,ry in LAKES:
  if camx-rx<lx<camx+width+rx and camy-ry<ly<camy+height+ry:
   canvas.create_oval(lx-rx-camx,ly-ry-camy,lx+rx-camx,ly+ry-camy,
                      fill="#789e9f",outline="#c9c1a3",width=8)
 for points in ROADS:
  for a,b in zip(points,points[1:]):
   if not visible(a,b):continue
   x1,y1=xy(a);x2,y2=xy(b)
   canvas.create_line(x1,y1,x2,y2,width=100,fill="#cbb18a")
   canvas.create_line(x1,y1,x2,y2,width=2,fill="#e4c99d",dash=(14,20))
 for points in RAILS:
  for a,b in zip(points,points[1:]):
   if not visible(a,b):continue
   x1,y1=xy(a);x2,y2=xy(b)
   canvas.create_line(x1,y1,x2,y2,width=25,fill="#745c48")
   canvas.create_line(x1,y1,x2,y2,width=4,fill="#3e3430",dash=(8,10))
 for key,name,tx,ty,kind in TOWNS:
  sx,sy=tx-camx,ty-camy
  if not(-420<sx<width+420 and -420<sy<height+420):continue
  size=165 if kind in ("city","town","port") else 90
  canvas.create_oval(sx-size,sy-size*.64,sx+size,sy+size*.64,
                     fill="#bda680",outline="#907354",width=3)
  for ox in (-70,30,95):
   canvas.create_rectangle(sx+ox-28,sy-42,sx+ox+12,sy-2,
                           fill="#886e50",outline="#5b4734",width=2)
   canvas.create_polygon(sx+ox-36,sy-42,sx+ox-8,sy-59,sx+ox+20,sy-42,
                         fill="#684d37",outline="")
  canvas.create_rectangle(sx-105,sy+27,sx+105,sy+49,fill="#574633",outline="#d5b78a")
  canvas.create_text(sx,sy+38,text=name.upper(),fill="#eed5a7",font=("DejaVu Sans",8,"bold"))

def draw_atlas(canvas,view,rect):
 """Vector parchment atlas with authored waterways, railway, towns and regions."""
 ox,oy,vw,vh=view;rx,ry,rw,rh=rect
 canvas.create_rectangle(rx,ry,rx+rw,ry+rh,fill="#d1b58b",outline="")
 def scr(pt):
  return (rx+(pt[0]-ox)*rw/vw,ry+(pt[1]-oy)*rh/vh)
 def vis(pt):
  return ox<=pt[0]<=ox+vw and oy<=pt[1]<=oy+vh
 for i,(name,x,y,biome,_) in enumerate(REGIONS):
  sx,sy=scr((x,y))
  if not(rx-40<sx<rx+rw+40 and ry-25<sy<ry+rh+25):continue
  color=BIOME_COLORS.get(biome,"#c8ae85")
  radius=6500*rw/vw
  radius=max(20,min(220,radius))
  canvas.create_oval(sx-radius,sy-radius*.64,sx+radius,sy+radius*.64,
                     fill=color,outline="",stipple="gray75")
  if rx+22<sx<rx+rw-22 and ry+14<sy<ry+rh-14:
   canvas.create_text(sx,sy,text=name.upper(),fill="#473b2d",
                      font=("DejaVu Sans",8,"bold"))
 for name,points,w in WATERWAYS:
  coords=[scr(p) for p in points]
  canvas.create_line(*[v for p in coords for v in p],fill="#678f98",
                     width=3 if vw>22000 else 7,smooth=True)
 for name,lx,ly,rwx,rhy in LAKES:
  sx,sy=scr((lx,ly))
  canvas.create_oval(sx-rwx*rw/vw,sy-rhy*rh/vh,sx+rwx*rw/vw,sy+rhy*rh/vh,
                     fill="#7ba2a8",outline="#536f75",width=2)
 for points in ROADS:
  canvas.create_line(*[v for p in points for v in scr(p)],fill="#9c7656",width=2,dash=(5,6))
 for points in RAILS:
  canvas.create_line(*[v for p in points for v in scr(p)],fill="#a45546",width=3,dash=(4,3))
 for key,name,tx,ty,kind in TOWNS:
  if not vis((tx,ty)):continue
  sx,sy=scr((tx,ty))
  canvas.create_oval(sx-3,sy-3,sx+3,sy+3,fill="#28251f",outline="#efdec0",width=1)
  if vw<32000 or key in ("blackwater_crossing","saint_brigids","galloway",
                         "saints_hollow","harpers_landing","dustwell","bayou_haven"):
   canvas.create_text(sx+6,sy-8,text=name,fill="#2c261f",
                      anchor="w",font=("DejaVu Sans",9,"bold"))
 canvas.create_rectangle(rx,ry,rx+rw,ry+rh,outline="#6d5136",width=3)
