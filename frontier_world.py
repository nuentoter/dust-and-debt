"""The finalized 10x Dust & Debt territory: deterministic, camera-local world data.

The original 4,800x3,200 hand-painted area and all existing buildings stay at
their original coordinates. This module adds no large image or runtime packages.
"""
import math

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
LANDMARKS = (
 ("rustwatch","Rustwatch Tower",17800,2700,"tower"),
 ("white_stag","White Stag Grove",27000,3800,"forest"),
 ("black_spire","Black Spire",36600,3300,"mesa"),
 ("salt_bells","Salt Bell Flats",47300,3900,"salt"),
 ("north_pass","North Pass",56100,3700,"pass"),
 ("dry_mill","Deadman's Mill",8700,13000,"ruin"),
 ("oxhead","Oxhead Fossil",24100,14900,"bones"),
 ("stillwater","Stillwater Falls",34800,14200,"water"),
 ("broken_dam","Broken Dam",43000,15000,"ruin"),
 ("lantern_post","Last Lantern Post",53800,14200,"tower"),
 ("mirage","Mirage Well",5200,24400,"water"),
 ("twin_pines","Twin Pines",15500,23700,"forest"),
 ("copper_gate","Copper Gate",25400,23900,"mine"),
 ("devils_stair","Devil's Stair",33800,25100,"canyon"),
 ("blueglass","Blueglass Shore",46800,24100,"water"),
 ("far_station","Far Station",55500,25100,"ruin"),
 ("coyote_cross","Coyote Crossing",6700,35500,"camp"),
 ("three_forks","Three Forks",17400,35000,"water"),
 ("timberfall","Timberfall",27000,35400,"forest"),
 ("red_obelisk","Red Obelisk",37000,35500,"mesa"),
 ("ash_garden","Ash Garden",48000,35100,"desert"),
 ("horizon_gates","Horizon Gates",57300,36400,"ruin"),
)
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
 r,c=sector_at(x,y)
 return SECTOR_NAMES[r][c]

def biome_at(x,y):
 r,c=sector_at(x,y)
 return BIOME_GRID[r][c]

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
 if any(abs(x-rx)<38 for rx in ROAD_X):return True
 if any(abs(y-ry)<39 for ry in ROAD_Y):return True
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
 """Paint only the 24 low-resolution geographic sectors and visible roads."""
 ox,oy,vw,vh=view;x,y,w,h=rect
 canvas.create_rectangle(x,y,x+w,y+h,fill='#ae9776',outline='')
 for row in range(4):
  for col in range(6):
   x0=col*SECTOR_W;y0=row*SECTOR_H
   x1=x0+SECTOR_W;y1=y0+SECTOR_H
   if x1<ox or x0>ox+vw or y1<oy or y0>oy+vh:continue
   ax=max(x,x+(x0-ox)*w/vw);ay=max(y,y+(y0-oy)*h/vh)
   bx=min(x+w,x+(x1-ox)*w/vw);by=min(y+h,y+(y1-oy)*h/vh)
   if bx<=ax or by<=ay:continue
   kind=BIOME_GRID[row][col]
   canvas.create_rectangle(ax,ay,bx,by,fill=BIOME_PALETTES[kind][0],outline='#99886f')
   if bx-ax>105 and by-ay>60:
    canvas.create_text((ax+bx)/2,(ay+by)/2,text=SECTOR_NAMES[row][col].upper(),
                       fill='#514737',font=('DejaVu Sans',8,'bold'))
 def pt(px,py):return (x+(px-ox)*w/vw,y+(py-oy)*h/vh)
 for rx in ROAD_X:
  if ox<=rx<=ox+vw:
   xx,_=pt(rx,0);canvas.create_line(xx,y,xx,y+h,fill='#d8c291',width=2)
 for ry in ROAD_Y:
  if oy<=ry<=oy+vh:
   _,yy=pt(0,ry);canvas.create_line(x,yy,x+w,yy,fill='#d8c291',width=2)
 (sx,sy),(ex,ey)=START_SPUR
 # Only draw connector when its endpoints fall into a view that might show it.
 if not(ex<ox or sx>ox+vw or ey<oy or sy>oy+vh):
  ax,ay=pt(sx,sy);bx,by=pt(ex,ey)
  canvas.create_line(ax,ay,bx,by,fill='#d8c291',width=2)
 # Indicate the original hand-crafted area without trying to stretch its old bitmap.
 ax,ay=pt(0,0);bx,by=pt(4800,3200)
 ax=max(x,ax);ay=max(y,ay);bx=min(x+w,bx);by=min(y+h,by)
 if bx>ax and by>ay:
  canvas.create_rectangle(ax,ay,bx,by,fill='#a88c62',outline='#5d4938',width=2)
  if bx-ax>80:canvas.create_text((ax+bx)/2,(ay+by)/2,text='ORIGINAL FRONTIER',
                              fill='#3c2e24',font=('DejaVu Sans',8,'bold'))
 canvas.create_rectangle(x,y,x+w,y+h,outline='#5e4830',width=3)
