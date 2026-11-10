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
COASTLINE_SRC=((0,1086),(380,1010),(530,967),(650,895),(720,887),
               (820,904),(930,841),(1110,811),(1240,829),(1448,777))
COAST_POLYGON=tuple(P(*p) for p in COASTLINE_SRC)+((60000,40960),(0,40960))
# Red railroad routes and brown wagon trails: traced routes with intermediate bends.
RAILS_SRC=(
 ((441,392),(505,376),(569,366),(636,336),(694,293),(754,281),(823,293),(894,330),(960,338),(1033,321),(1057,306)),
 ((442,392),(478,410),(518,455),(566,482),(606,508),(648,515),(728,521),(799,523),(852,511),(883,506),(935,547),(991,574),(1049,607),(1123,628),(1175,681),(1209,746)),
 ((648,515),(596,550),(533,586),(472,643),(441,699),(415,746),(415,788),(488,802),(572,803),(647,812),(700,835),(774,851),(819,891)),
 ((883,506),(904,559),(901,607),(853,643),(811,662),(764,700),(744,761),(700,835)),
)
RAILS=tuple(path(p) for p in RAILS_SRC)
ROADS_SRC=(
 ((178,277),(256,309),(315,329),(370,356),(405,342),(442,352),(442,392)),
 ((549,232),(568,278),(600,324),(648,370),(614,419),(608,468),(648,515)),
 ((705,77),(707,157),(755,281)),
 ((1157,142),(1150,209),(1166,264),(1057,306)),
 ((1057,306),(1035,284),(1069,284),(1102,361),(1083,404),(1124,442),(1189,464),(1313,473)),
 ((1083,404),(1115,435),(1140,455),(1091,481),(1049,607)),
 ((442,392),(438,453),(449,484),(482,516),(470,564),(376,552),(344,613)),
 ((376,552),(328,599),(288,650),(288,759),(352,732),(410,758),(415,788)),
 ((648,515),(628,550),(657,565),(658,633),(705,653),(811,662)),
 ((1049,607),(1080,570),(1100,570),(1170,620),(1230,680),(1209,746)),
 ((1049,607),(1001,674),(1031,803)),
 ((700,835),(740,837),(760,809),(625,758),(562,726),(507,669)),
 ((1313,473),(1325,531),(1315,566),(1329,645),(1250,675),(1250,728),(1209,746)),
)
ROADS=tuple(path(p) for p in ROADS_SRC)

# v2.9-map: deliberately authored missing wagon connections. These preserve
# the 13 canonical atlas roads and supply visible secondary road approaches.
# All positions below are from original atlas pixels, except the Cinder Creek
# hand-painted parcel's outbound START_SPUR terminal (world coordinates).
SECONDARY_ROADS_SRC=(
 ("galloway_blackwater",((442,392),(519,386),(605,397),(580,352),(600,324))),
 ("blackwater_larkfield",((648,515),(680,485),(730,489),(810,479),(883,506))),
 ("larkfield_harpers",((883,506),(930,525),(980,550),(1030,560),(1065,573),(1049,607))),
 ("saints_hollow_roan",((755,281),(840,335),(930,352),(1057,306))),
 ("harpers_valleyford",((1049,607),(1070,574),(1025,575),(965,628),(908,674),(811,662))),
 ("valleyford_riversend",((811,662),(740,688),(716,745),(765,780),(748,806),(760,837),(700,835))),
 ("riversend_saint_brigids",((700,835),(755,855),(819,891))),
 ("iron_mesa_stonewall",((238,505),(260,524),(318,536),(376,552))),
 ("brimstone_iron_mesa",((69,587),(130,571),(180,532),(238,505))),
)
SECONDARY_ROADS=tuple((key,path(points)) for key,points in SECONDARY_ROADS_SRC)
SECONDARY_ROADS+=(("cinder_creek_approach",
 ((6000,4300),*path(((122,167),(145,215),(178,277))))),)

# Authored last-mile paths (source-map pixels): fishing banks and established
# camp clearings. These are narrow *foot/horse* trails, not wagon shortcuts.
TRAILS_SRC=(
 ("fish_frostvein_e","fishing","Frostvein East Bank",((549,232),(543,198),(557,148))),
 ("fish_frostvein_w","fishing","Frostvein West Bank",((549,232),(490,215),(446,155))),
 ("fish_northstar_w","fishing","Northstar West Shore",((930,352),(880,303),(893,244))),
 ("fish_northstar_e","fishing","Northstar East Shore",((1057,306),(1064,272),(1048,244))),
 ("fish_sable","fishing","Sable River Eddy",((376,552),(386,569),(392,575))),
 ("fish_blackwater","fishing","Blackwater North Bank",((980,550),(977,548),(970,549))),
 ("fish_roan","fishing","Roan Creek Pool",((1124,442),(1105,451),(1094,446))),
 ("fish_riversend","fishing","Riversend Channel West Bank",((811,662),(783,682),(788,714))),
 ("fish_dustwell","fishing","Dustwell Wash Bank",((562,726),(550,752),(525,760))),
 ("fish_cypress","fishing","Cypress Bayou Shore",((1209,746),(1166,776),(1120,784))),
 ("fish_harpers","fishing","Harper's Upstream Fishing",((980,550),(995,555),(1008,562))),
 ("fish_brigids","fishing","Saint Brigid's Pier",((819,891),(823,878))),
 ("camp_dustwell","camp","Dustwell Road Camp",((415,788),(403,767),(410,764))),
 ("camp_cinder","camp","Cinder Ridge Shelter",((178,277),(155,318),(150,340))),
 ("camp_graystone","camp","Graystone Mountain Camp",((370,356),(385,300),(385,240))),
 ("camp_everwood","camp","Everwood Hunter Camp",((1150,209),(1120,218),(1110,200))),
 ("camp_cedarheart","camp","Cedarheart Forest Camp",((1313,473),(1285,486),(1260,510))),
 ("camp_heartland","camp","Heartland Wagon Camp",((810,479),(785,452),(760,430))),
 ("camp_sable","camp","Sable River Camp",((470,564),(500,559))),
 ("camp_roan","camp","Roan Creek Camp",((1124,442),(1140,448),(1155,435))),
 ("camp_redthorn","camp","Red Thorn Canyon Camp",((328,599),(285,590),(260,605))),
 ("camp_sundown","camp","Sundown Plateau Camp",((288,759),(230,740),(160,730))),
 ("camp_redmesa","camp","Red Mesa Buttes Camp",((625,758),(610,745))),
 ("camp_cypress","camp","Cypress Bayou Camp",((1031,803),(1045,776),(1050,755))),
)
TRAILS=tuple((key,kind,name,path(points)) for key,kind,name,points in TRAILS_SRC)

def _crossing(a,b,c,d):
 """Intersection of two finite line segments; return the crossing and road heading."""
 ux,uy=b[0]-a[0],b[1]-a[1]
 vx,vy=d[0]-c[0],d[1]-c[1]
 determinant=ux*vy-uy*vx
 if abs(determinant)<1e-7:return None
 wx,wy=c[0]-a[0],c[1]-a[1]
 t=(wx*vy-wy*vx)/determinant
 u=(wx*uy-wy*ux)/determinant
 if not(0<=t<=1 and 0<=u<=1):return None
 length=math.hypot(ux,uy)
 return (a[0]+t*ux,a[1]+t*uy,ux/length,uy/length) if length else None

def build_bridges():
 """Find real road/rail/water intersections, not arbitrary walkable water strips."""
 crossings=[]
 for water_name,water,width in WATERWAYS:
  for route_type,routes in (('rail',RAILS),('road',ROADS),
                            ('road',tuple(points for _,points in SECONDARY_ROADS))):
   for route in routes:
    for a,b in zip(route,route[1:]):
     for c,d in zip(water,water[1:]):
      hit=_crossing(a,b,c,d)
      if hit and not any(math.hypot(hit[0]-p[0],hit[1]-p[1])<180
                         for p in crossings):
       crossings.append((*hit,water_name,route_type,width))
 return tuple(crossings)

# Additional explicitly authored wagon decks at known town river confluences.
# These are visible physical bridges, not invisible collision exemptions.
# The original intersection-derived rail/road bridges remain intact.
BRIDGES=build_bridges()+(
 (*P(648,510),1.,0.,"Blackwater Town Crossing","road",260),
 (*P(1051,600),0.32,-0.947,"Harper River Crossing","road",170),
 (*P(706,835),1.,0.,"Riversend East Bridge","road",210),
 (*P(1155,163),-.104,.995,"Pineheart Creek Bridge","road",170),
)

def bridge_at(x,y,margin=8):
 """Only the actual bridge deck across a river is passable."""
 for bx,by,dx,dy,name,kind,width in BRIDGES:
  along=(x-bx)*dx+(y-by)*dy
  across=abs(-(x-bx)*dy+(y-by)*dx)
  if abs(along)<width+120 and across<74+margin:return True
 return False


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
 return any(near_polyline(x,y,route,90) for route in ROADS+RAILS) or any(
  near_polyline(x,y,points,55) for _,points in SECONDARY_ROADS)

def travel_trail(x,y):
 return any(near_polyline(x,y,pts,36) for _,_,_,pts in TRAILS)

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
 for a,b in zip(COASTLINE_SRC,COASTLINE_SRC[1:]):
  if a[0]<=source_x<=b[0]:
   k=(source_x-a[0])/(b[0]-a[0])
   return source_y>a[1]+k*(b[1]-a[1])+8
 return False

def ford_at(x,y):
 # Bridge decks are restricted to actual line intersections.
 return bridge_at(x,y)

def is_water(x,y):
 if x<4800 and y<3200:return False  # inherited Cinder Creek parcel
 # Cheap water test comes first: most world positions are dry.
 coast=coastal_water(x,y)
 lake=lake_at(x,y)
 river=river_at(x,y)
 if not(coast or lake or river):return False
 if near_atlas_town(x,y,230) is not None:return False
 # Bridges can cross rivers, but no invisible roads across open Gulf water.
 if river and not coast and not lake and bridge_at(x,y):return False
 return True

SETTLEMENT_KINDS=frozenset(('city','town','port','post','settlement','fort','ranch','mine','camp','ruin','tower'))
def near_atlas_town(x,y,radius=420):
 for key,name,tx,ty,kind in TOWNS:
  if kind in SETTLEMENT_KINDS and math.hypot(tx-x,ty-y)<radius:return key
 return None

def draw_local_geography(canvas,camx,camy,width,height):
 """Only draw river/coast/road segments intersecting the camera viewport."""
 def visible(a,b,pad=450):
  return (max(a[0],b[0])>=camx-pad and min(a[0],b[0])<=camx+width+pad and
          max(a[1],b[1])>=camy-pad and min(a[1],b[1])<=camy+height+pad)
 def xy(pt):return (pt[0]-camx,pt[1]-camy)
 # The lower coast is real water, not just an invisible collision wall.
 if any(coastal_water(px,py) for px,py in ((camx,camy),
     (camx+width,camy),(camx,camy+height),(camx+width,camy+height))):
  canvas.create_polygon(*[v for pt in COAST_POLYGON for v in xy(pt)],
                        fill='#71979c',outline='')
  for a,b in zip(COAST_POLYGON,COAST_POLYGON[1:]):
   if not visible(a,b,120):continue
   x1,y1=xy(a);x2,y2=xy(b)
   canvas.create_line(x1,y1,x2,y2,fill='#d6c6a3',width=15)
   canvas.create_line(x1,y1,x2,y2,fill='#adbdad',width=4,dash=(18,23))
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
   dx=x2-x1;dy=y2-y1
   length=math.hypot(dx,dy) or 1.
   nx,ny=-dy/length,dx/length
   # Soft road shoulder, compacted center, wheel wear.
   canvas.create_line(x1,y1,x2,y2,width=126,fill="#9f8c6f",capstyle='round')
   canvas.create_line(x1,y1,x2,y2,width=101,fill="#cbb18a",capstyle='round')
   canvas.create_line(x1,y1,x2,y2,width=76,fill="#d6bb92",capstyle='round')
   for sign in (-1,1):
    shift=sign*29
    canvas.create_line(x1+nx*shift,y1+ny*shift,x2+nx*shift,y2+ny*shift,
                       width=3,fill="#9d8566",dash=(20,18))
 for key,points in SECONDARY_ROADS:
  for a,b in zip(points,points[1:]):
   if not visible(a,b):continue
   x1,y1=xy(a);x2,y2=xy(b)
   canvas.create_line(x1,y1,x2,y2,width=84,fill='#8e7a5e',capstyle='round')
   canvas.create_line(x1,y1,x2,y2,width=60,fill='#b59a76',capstyle='round')
   canvas.create_line(x1,y1,x2,y2,width=31,fill='#c4a77d',capstyle='round')
   canvas.create_line(x1,y1,x2,y2,width=2,fill='#8e7457',dash=(18,26))
 for key,kind,name,points in TRAILS:
  for a,b in zip(points,points[1:]):
   if not visible(a,b):continue
   x1,y1=xy(a);x2,y2=xy(b)
   canvas.create_line(x1,y1,x2,y2,width=33,fill='#847358',capstyle='round')
   canvas.create_line(x1,y1,x2,y2,width=18,fill='#b9a47e',capstyle='round')
   canvas.create_line(x1,y1,x2,y2,width=2,fill='#dfcaa0',dash=(7,19))
 for points in RAILS:
  for a,b in zip(points,points[1:]):
   if not visible(a,b):continue
   x1,y1=xy(a);x2,y2=xy(b)
   canvas.create_line(x1,y1,x2,y2,width=25,fill="#745c48")
   canvas.create_line(x1,y1,x2,y2,width=4,fill="#3e3430",dash=(8,10))
 # Distinct planked bridges with rails and timber ties, at true intersections.
 for bx,by,dx,dy,river,kind,water_width in BRIDGES:
  if not(camx-450<bx<camx+width+450 and camy-450<by<camy+height+450):continue
  half=water_width+105
  cx,cy=bx-camx,by-camy
  ax,ay=cx-dx*half,cy-dy*half
  ex,ey=cx+dx*half,cy+dy*half
  canvas.create_line(ax,ay,ex,ey,fill='#594b39',width=122)
  canvas.create_line(ax,ay,ex,ey,fill='#bb9d70',width=106)
  nx,ny=-dy,dx
  for side in (-1,1):
   canvas.create_line(ax+nx*side*63,ay+ny*side*63,
                      ex+nx*side*63,ey+ny*side*63,fill='#6a4b33',width=7)
  for offset in range(-int(half)+12,int(half),28):
   px,py=cx+dx*offset,cy+dy*offset
   canvas.create_line(px-nx*45,py-ny*45,px+nx*45,py+ny*45,
                      fill='#786344',width=3)
  if kind=='rail':
   for side in (-1,1):
    canvas.create_line(ax+nx*side*14,ay+ny*side*14,
                       ex+nx*side*14,ey+ny*side*14,fill='#3e3831',width=5)
 # Coastal islands remain visible, but are not invisible pedestrian bridges.
 for key,name,ix,iy,kind in TOWNS:
  if kind!='island':continue
  sx,sy=ix-camx,iy-camy
  if -180<sx<width+180 and -150<sy<height+150:
   canvas.create_oval(sx-78,sy-42,sx+78,sy+42,
                      fill='#a69d72',outline='#d6c8a6',width=6)
   canvas.create_polygon(sx-30,sy+7,sx-7,sy-25,sx+10,sy+8,
                         fill='#678260',outline='')
 for key,name,tx,ty,kind in TOWNS:
  if kind in ('lake','waterfall','spring','island'):continue
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
  if kind=='port' or key in ('bayou_haven','harpers_landing'):
   # A raised wooden quay; the riverbank and Gulf remain obstacles elsewhere.
   side=1 if key=='saint_brigids' else -1
   canvas.create_rectangle(sx+side*108-26,sy-35,sx+side*108+26,sy+82,
                           fill='#856746',outline='#52432e',width=4)
   for plank in range(-17,78,19):
    canvas.create_line(sx+side*108-23,sy+plank,
                       sx+side*108+23,sy+plank,fill='#513c2d',width=2)

def draw_starting_transition(canvas,camx,camy,width,height,old_width,old_height):
 """Dusty feather over the inherited square's hard seam; no image allocations."""
 if camx>old_width+100 or camy>old_height+100:return
 # Draw only on top of the original map image at its vertical/eastern edges.
 for x1,y1,x2,y2 in ((old_width-16,0,old_width+17,old_height),
                      (0,old_height-16,old_width,old_height+17)):
  sx1,sy1=x1-camx,y1-camy;sx2,sy2=x2-camx,y2-camy
  if sx2<0 or sy2<0 or sx1>width or sy1>height:continue
  canvas.create_rectangle(sx1,sy1,sx2,sy2,fill='#bcaa85',outline='',stipple='gray50')
 # Winding dust and small stones soften a straight rectangular border.
 for n in range(0,old_height,91):
  x=old_width+((n*23)%41)-20-camx;y=n-camy
  if -30<x<width+30 and -30<y<height+30:
   canvas.create_oval(x-8,y-3,x+9,y+3,fill='#b5a07a',outline='')
 for n in range(0,old_width,93):
  x=n-camx;y=old_height+((n*13)%41)-20-camy
  if -30<x<width+30 and -30<y<height+30:
   canvas.create_oval(x-7,y-4,x+8,y+4,fill='#b5a07a',outline='')

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
  x1=max(rx,sx-radius);y1=max(ry,sy-radius*.64)
  x2=min(rx+rw,sx+radius);y2=min(ry+rh,sy+radius*.64)
  if x2>x1 and y2>y1:
   canvas.create_oval(x1,y1,x2,y2,fill=color,outline='',stipple='gray75')
  if rx+22<sx<rx+rw-22 and ry+14<sy<ry+rh-14:
   canvas.create_text(sx,sy,text=name.upper(),fill="#473b2d",
                      font=("DejaVu Sans",8,"bold"))
 # Gulf coastline is drawn before navigational lines and town labels.
 def clip_polygon(points):
  # Sutherland-Hodgman polygon clipping to this atlas view.
  poly=list(points)
  for axis,bound,greater in ((0,ox,True),(0,ox+vw,False),(1,oy,True),(1,oy+vh,False)):
   if not poly:break
   result=[]
   def valid(p):return p[axis]>=bound if greater else p[axis]<=bound
   for prev,cur in zip(poly[-1:]+poly[:-1],poly):
    start=valid(prev);end=valid(cur)
    if start!=end:
     delta=cur[axis]-prev[axis]
     t=(bound-prev[axis])/delta if delta else 0
     result.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
    if end:result.append(cur)
   poly=result
  return poly
 ocean=clip_polygon(COAST_POLYGON)
 if len(ocean)>=3:
  canvas.create_polygon(*[v for p in ocean for v in scr(p)],fill='#779ba1',outline='')
 def clipped(a,b):
  # Liang-Barsky clips each rail/river segment to the atlas rectangle.
  dx=b[0]-a[0];dy=b[1]-a[1];low=0.;high=1.
  for p,q in ((-dx,a[0]-rx),(dx,rx+rw-a[0]),
              (-dy,a[1]-ry),(dy,ry+rh-a[1])):
   if abs(p)<1e-9:
    if q<0:return None
    continue
   ratio=q/p
   if p<0:low=max(low,ratio)
   else:high=min(high,ratio)
   if low>high:return None
  return (a[0]+low*dx,a[1]+low*dy,a[0]+high*dx,a[1]+high*dy)
 def draw_route(points,color,width=2,dash=None):
  for a,b in zip(points,points[1:]):
   segment=clipped(scr(a),scr(b))
   if segment:
    args={'fill':color,'width':width}
    if dash:args['dash']=dash
    canvas.create_line(*segment,**args)
 for name,points,w in WATERWAYS:
  draw_route(points,'#678f98',3 if vw>22000 else 7)
 for name,lx,ly,rwx,rhy in LAKES:
  sx,sy=scr((lx,ly))
  x1=max(rx,sx-rwx*rw/vw);y1=max(ry,sy-rhy*rh/vh)
  x2=min(rx+rw,sx+rwx*rw/vw);y2=min(ry+rh,sy+rhy*rh/vh)
  if x2>x1 and y2>y1:
   canvas.create_oval(x1,y1,x2,y2,fill='#7ba2a8',outline='#536f75',width=2)
 for points in ROADS:draw_route(points,'#9c7656',2,(5,6))
 for _,points in SECONDARY_ROADS:draw_route(points,'#b48d61',1.5,(4,7))
 for _,_,_,pts in TRAILS:draw_route(pts,'#8d7156',1,(2,6))
 for points in RAILS:draw_route(points,'#a45546',3,(4,3))
 for key,name,tx,ty,kind in TOWNS:
  if not vis((tx,ty)):continue
  sx,sy=scr((tx,ty))
  canvas.create_oval(sx-3,sy-3,sx+3,sy+3,fill="#28251f",outline="#efdec0",width=1)
  if vw<32000 or key in ("blackwater_crossing","saint_brigids","galloway",
                         "saints_hollow","harpers_landing","dustwell","bayou_haven"):
   canvas.create_text(sx+6,sy-8,text=name,fill="#2c261f",
                      anchor="w",font=("DejaVu Sans",9,"bold"))
 canvas.create_rectangle(rx,ry,rx+rw,ry+rh,outline="#6d5136",width=3)
