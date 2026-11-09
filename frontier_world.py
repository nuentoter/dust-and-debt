"""The finalized 10x Dust & Debt territory: deterministic, camera-local world data.

The original 4,800x3,200 hand-painted area and all existing buildings stay at
their original coordinates. This module adds no large image or runtime packages.
"""
import math
from new_austellia import (TOWNS,TOWN_BY_ID,REGIONS,region_at as atlas_region,
 biome_at as atlas_biome,travel_road,draw_atlas)

WORLD_WIDTH = 60000
WORLD_HEIGHT = 40960
SECTOR_W = 10000
SECTOR_H = 10240
SECTOR_NAMES = (
 ("The Old Frontier","Rustbelt Plains","Thornwood","Black Mesa","Saltwind Basin","Northern Range"),
 ("The Borderlands","Broken Prairie","Oxhead Gulch","Whisper Hills","Deadwater Flats","Far Lanterns"),
 ("Sunbleached Trail","Prairie Sea","Copper Divide","Redstone Maze","Blueglass Country","Distant Run"),
 ("South Marches","Three Forks","Fallen Timber","Devil's Reach","Ashfall Desert","Last Horizon"),
)
BIOME_GRID = (
 ("prairie","scrub","forest","mesa","salt","mountain"),
 ("scrub","prairie","canyon","forest","salt","scrub"),
 ("desert","prairie","mountain","canyon","lake","prairie"),
 ("scrub","grass","forest","canyon","desert","mesa"),
)
BIOME_PALETTES = {
 "prairie":("#b6a477","#ac9b70","#afa078"),
 "grass":("#9a9a6a","#929c6b","#a1a272"),
 "scrub":("#b39b70","#aa956b","#b9a077"),
 "forest":("#798667","#7d8965","#889271"),
 "mesa":("#bd9170","#b58465","#c49772"),
 "canyon":("#ad7761","#b98064","#aa775f"),
 "desert":("#d2b487","#c9ac7c","#d7b789"),
 "salt":("#d5c8ac","#cac0a9","#ddd1b4"),
 "lake":("#9bb1a2","#8fa99c","#a4b4a4"),
 "mountain":("#8d867c","#968e83","#a49b8b"),
}
# ID, label, position, category. Sites are spaced throughout the new territory.
# Named discoveries now come directly from the illustrated New Austellia atlas.
LANDMARKS = tuple((key,name,x,y,{'mine':'mine','fort':'ruin','ranch':'camp',
  'island':'water','lake':'water','pass':'pass','waterfall':'water',
  'ruin':'ruin','spring':'water','tower':'tower'}.get(kind,'camp'))
  for key,name,x,y,kind in TOWNS if kind not in ('city','town','port','settlement'))
# Roads are linked to the current six towns; the starting world has a spur.
ROAD_X = tuple(range(6000,WORLD_WIDTH,4200))
ROAD_Y = tuple(range(4300,WORLD_HEIGHT,3600))
START_SPUR=((4650,2980),(6000,4300))
MAP_RECT=(150,110,658,394)

def sector_at(x,y):
 col=max(0,min(5,int(x//SECTOR_W)))
 row=max(0,min(3,int(y//SECTOR_H)))
 return row,col

def region_at(x,y):
 return atlas_region(x,y)

def biome_at(x,y):
 return atlas_biome(x,y)

def hash32(x,y):
 z=((int(x)*73856093)^(int(y)*19349663)^0xB16B00B5)&0xffffffff
 z=((z^(z>>13))*1274126177)&0xffffffff
 return z^(z>>16)

def near_landmark(x,y,radius=370):
 for key,name,lx,ly,kind in LANDMARKS:
  if (x-lx)**2+(y-ly)**2<radius*radius:return key
 return None

def landmark_by_key(key):
 return next((item for item in LANDMARKS if item[0]==key),None)

def road_at(x,y):
 # Preserve the hand-authored original region; don't paint roads across it.
 if x<4800 and y<3200:return False
 if x<17000 and y<10300:
  if any(abs(x-rx)<38 for rx in ROAD_X):return True
  if any(abs(y-ry)<39 for ry in ROAD_Y):return True
 if travel_road(x,y):return True
 x1,y1=START_SPUR[0];x2,y2=START_SPUR[1]
 dx=x2-x1;dy=y2-y1
 t=max(0.,min(1.,((x-x1)*dx+(y-y1)*dy)/(dx*dx+dy*dy)))
 return (x-(x1+t*dx))**2+(y-(y1+t*dy))**2<65*65

def landmark_coords(key):
 lm=landmark_by_key(key)
 return (lm[2],lm[3]) if lm else None

def map_view(zoom,center_x,center_y):
 if not zoom:return (0.,0.,float(WORLD_WIDTH),float(WORLD_HEIGHT))
 width,height=15000.,10240.
 ox=max(0.,min(WORLD_WIDTH-width,center_x-width/2))
 oy=max(0.,min(WORLD_HEIGHT-height,center_y-height/2))
 return (ox,oy,width,height)

def point_on_map(x,y,view,rect=MAP_RECT):
 ox,oy,vw,vh=view;rx,ry,rw,rh=rect
 if not (ox<=x<=ox+vw and oy<=y<=oy+vh):return None
 return (rx+(x-ox)*rw/vw, ry+(y-oy)*rh/vh)

def world_from_map(px,py,view,rect=MAP_RECT):
 rx,ry,rw,rh=rect
 if not(rx<=px<=rx+rw and ry<=py<=ry+rh):return None
 ox,oy,vw,vh=view
 return (max(25.,min(WORLD_WIDTH-25.,ox+(px-rx)/rw*vw)),
         max(25.,min(WORLD_HEIGHT-25.,oy+(py-ry)/rh*vh)))

def draw_landmark(canvas,camx,camy,width,height):
 for key,name,x,y,kind in LANDMARKS:
  sx,sy=x-camx,y-camy
  if not(-250<sx<width+250 and -250<sy<height+250):continue
  canvas.create_oval(sx-75,sy-38,sx+75,sy+38,fill='#baa17c',outline='#877658',width=3)
  if kind in ('tower','ruin','pass'):
   canvas.create_rectangle(sx-27,sy-51,sx+27,sy+8,fill='#7e7060',outline='#4a453e',width=4)
   canvas.create_polygon(sx-37,sy-50,sx,sy-76,sx+37,sy-50,fill='#5b5145',outline='')
  elif kind in ('water','forest'):
   canvas.create_oval(sx-56,sy-32,sx+60,sy+23,fill='#6d9c9b',outline='#4d7976',width=3)
   if kind=='forest':
    for px in (-34,24):
     canvas.create_polygon(sx+px-23,sy+1,sx+px,sy-70,sx+px+23,sy+1,fill='#526b4c',outline='#344938')
  elif kind in ('mesa','canyon','mine'):
   canvas.create_polygon(sx-59,sy+14,sx-30,sy-56,sx+32,sy-61,sx+62,sy+14,fill='#925944',outline='#633c33',width=3)
  elif kind=='camp':
   canvas.create_polygon(sx-29,sy+15,sx,sy-52,sx+30,sy+15,fill='#c7a77b',outline='#725b48',width=3)
  else:
   for px,py in ((-28,6),(0,-28),(35,4)):
    canvas.create_oval(sx+px-13,sy+py-8,sx+px+13,sy+py+8,fill='#8f7765',outline='#594c43')
  canvas.create_rectangle(sx-77,sy+29,sx+77,sy+47,fill='#594a3a',outline='#ddbd8b',width=2)
  canvas.create_text(sx,sy+38,text=name.upper(),fill='#f2d7a3',font=('DejaVu Sans',8,'bold'))

def draw_map_background(canvas,view,rect=MAP_RECT):
 """Draw user-authored New Austellia geography, not a fabricated grid."""
 draw_atlas(canvas,view,rect)

# Safe, useful roadside stops make crossing 60,000 units practical.
# Each is a small rest-and-water stop, not a fully simulated town.
# Authoritative waystations coincide with New Austellia transport hubs.
_WAYSTATION_IDS=(
 ('galloway_depot','Galloway Depot','galloway'),
 ('saints_hollow_post','Saint Hollow Post','saints_hollow'),
 ('roan_creek_post','Roan Creek Post','roan_creek'),
 ('hollow_bend_post','Hollow Bend Post','hollow_bend'),
 ('blackwater_station','Blackwater Station','blackwater_crossing'),
 ('larkfield_depot','Larkfield Depot','larkfield'),
 ('harpers_ferry','Harper Ferry Post','harpers_landing'),
 ('valleyford_post','Valleyford Post','valleyford'),
 ('dustwell_camp','Dustwell Camp','dustwell'),
 ('riversend_post','Riversend Station','riversend'),
 ('saint_brigids_post','Saint Brigid Port','saint_brigids'),
 ('bayou_haven_post','Bayou Haven Post','bayou_haven'),
 ('pineheart_post','Pineheart Trading Post','pineheart'),
)
WAYSTATIONS=tuple((key,name,TOWN_BY_ID[site][2],TOWN_BY_ID[site][3])
                  for key,name,site in _WAYSTATION_IDS)

def near_waystation(x,y,radius=340):
 for key,name,wx,wy in WAYSTATIONS:
  if (x-wx)**2+(y-wy)**2<radius*radius:return key
 return None

def waystation_by_key(key):
 return next((item for item in WAYSTATIONS if item[0]==key),None)

def draw_waystations(canvas,camx,camy,width,height):
 for key,name,x,y in WAYSTATIONS:
  sx,sy=x-camx,y-camy
  if not(-220<sx<width+220 and -180<sy<height+180):continue
  canvas.create_oval(sx-120,sy-83,sx+120,sy+75,fill='#bba37b',outline='#8e7455',width=3)
  canvas.create_polygon(sx-68,sy+35,sx-10,sy-55,sx+42,sy+35,fill='#8b654c',outline='#4f3c33',width=3)
  canvas.create_rectangle(sx+50,sy-6,sx+93,sy+20,fill='#7d9a9e',outline='#5d533f',width=3)
  canvas.create_line(sx-84,sy+45,sx-84,sy-4,fill='#594731',width=5)
  canvas.create_rectangle(sx-98,sy-35,sx+104,sy-7,fill='#5e4936',outline='#d9b985',width=2)
  canvas.create_text(sx+3,sy-21,text=name.upper(),fill='#f7deb2',
                     font=('DejaVu Sans',9,'bold'))
  canvas.create_polygon(sx-12,sy+38,sx,sy+10,sx+12,sy+38,fill='#e5ad57',outline='#9d5631')
  canvas.create_line(sx-16,sy+48,sx+16,sy+40,fill='#76513b',width=5)
