"""Data-driven frontier settlements, handcrafted side jobs, and lightweight scene art.
Only Python/Tkinter; no extra media, packages, or engine dependencies.
"""
# Settlements sit along the existing procedural north/south and east/west roads.
# key, display name, center (world coordinates), wall/roof palette, local character
from new_austellia import TOWN_BY_ID

# Existing six playable frontier towns are moved to illustrated New Austellia
# locations. Their guides and original six side quests remain playable.
_SETTLEMENT_IDS=(
 ('drybone','galloway','#866e50','#70513f','Ada Pike'),
 ('ironwell','iron_mesa','#817b68','#595958','Silas Flint'),
 ('painted','dustwell','#a07454','#784837','Rose Ortega'),
 ('saltwater','roan_creek','#857f66','#536b62','Jonah Reed'),
 ('ember','larkfield','#956447','#663d35','Mara Ash'),
 ('sundown','riversend','#a1895e','#665943','Caleb West'),
)
SETTLEMENTS=tuple((key,TOWN_BY_ID[place][1],TOWN_BY_ID[place][2],
                   TOWN_BY_ID[place][3],wall,roof,guide)
                  for key,place,wall,roof,guide in _SETTLEMENT_IDS)

# Each job remains a two-site expedition, now based on its real settlement.
_JOB_DEFS=(
 ('lost_mail','drybone','The Missing Mailbag','Recover two mailbags on Galloway trails',75),
 ('ore_samples','ironwell','The Iron Mesa Survey','Retrieve ore samples in the Iron Mesa badlands',95),
 ('painted_marks','painted','Signs in the Dust','Follow painted markers outside Dustwell',110),
 ('river_supplies','saltwater','Supplies Downriver','Retrieve medicine crates on Roan Creek',90),
 ('ember_ledger','ember','The Smuggler’s Account','Recover the missing Larkfield ledger',135),
 ('sundown_signal','sundown','Last Signal West','Retrieve railroad signal parts outside Riversend',150),
)
_TOWN_CENTER={k:(x,y) for k,_,x,y,*_ in SETTLEMENTS}
SIDE_JOBS=tuple((key,origin,title,instructions,
                 ((_TOWN_CENTER[origin][0]+650,_TOWN_CENTER[origin][1]+470),
                  (_TOWN_CENTER[origin][0]+1030,_TOWN_CENTER[origin][1]+920)),reward)
                for key,origin,title,instructions,reward in _JOB_DEFS)

# Buildings leave the old map untouched and keep the central road crossroads free.
def extra_buildings():
 out=[]
 for key,name,x,y,wall,roof,guide in SETTLEMENTS:
  out.extend((
   (name+" Trading Post",x-365,y-255,160,105,"store"),
   (name+" Boarding House",x+195,y-250,165,108,"hotel"),
   (name+" Clinic",x+205,y+145,145,95,"doctor"),
  ))
 return out

def extra_npcs():
 out=[]
 for key,name,x,y,wall,roof,guide in SETTLEMENTS:
  out.extend((
   (guide,x+55,y+35,"guide"),
   (name+" Merchant",x-120,y-90,"store"),
   (name+" Medic",x+275,y+275,"doctor"),
   (name+" Courier",x-145,y+135,"civilian"),
   (name+" Farmer",x+105,y-165,"civilian"),
   (name+" Watcher",x-65,y-170,"civilian"),
  ))
 return out

def resource_nodes():
 nodes=[]
 for key,name,x,y,*_ in SETTLEMENTS:
  nodes.append((key+"-herbs",x-480,y+90,"Wild herbs","tonic"))
  nodes.append((key+"-ore",x+460,y-95,"Loose ore","money"))
 return tuple(nodes)

def nearby_settlement(x,y,radius=550):
 for key,name,cx,cy,*_ in SETTLEMENTS:
  if (x-cx)**2+(y-cy)**2<radius**2:return key
 return None

def get_settlement(key):
 return next((item for item in SETTLEMENTS if item[0]==key),None)

def get_job(key):
 return next((job for job in SIDE_JOBS if job[0]==key),None)

def draw_frontier_towns(canvas,camx,camy,width,height):
 """Bounded Tk canvas vector drawings; no large map image required."""
 for key,name,x,y,wall,roof,guide in SETTLEMENTS:
  if not (camx-510<x<camx+width+510 and camy-460<y<camy+height+460):continue
  def pt(wx,wy):return wx-camx,wy-camy
  # Hard-packed town square and intersecting trail routes.
  sx,sy=pt(x,y)
  canvas.create_oval(sx-380,sy-265,sx+380,sy+275,fill="#bda37a",outline="#907654",width=3)
  canvas.create_rectangle(sx-42,sy-285,sx+42,sy+290,fill="#c7af87",outline="")
  canvas.create_rectangle(sx-390,sy-40,sx+390,sy+40,fill="#c7af87",outline="")
  # Sign at the southern crossing and a hitching rail.
  canvas.create_line(sx-165,sy+85,sx-165,sy+135,fill="#533f2e",width=6)
  canvas.create_line(sx-165,sy+92,sx-70,sy+92,fill="#533f2e",width=5)
  canvas.create_rectangle(sx-177,sy+138,sx+104,sy+166,fill="#624732",outline="#dbb67b",width=2)
  canvas.create_text(sx-35,sy+152,text=name.upper(),fill="#f6ddad",font=("DejaVu Sans",11,"bold"))
  # Decorative fencing and water trough.
  for ox in (-310,310):
   for oy in (-110,-55,0,55,110):
    canvas.create_line(sx+ox,sy+oy-8,sx+ox,sy+oy+8,fill="#7d5739",width=5)
  for ox in (-310,310):
   canvas.create_line(sx+ox,sy-118,sx+ox,sy+120,fill="#9d7654",width=2)
  canvas.create_oval(sx-285,sy+192,sx-235,sy+223,fill="#537b86",outline="#70563b",width=4)
  # Three building silhouettes use exactly the same rectangles as collisions.
  for building_name,bx,by,bw,bh,kind in extra_buildings():
   if not building_name.startswith(name+" "):continue
   ax,ay=pt(bx,by)
   canvas.create_rectangle(ax+6,ay+9,ax+bw+8,ay+bh+11,fill="#725c4a",outline="")
   canvas.create_rectangle(ax,ay,ax+bw,ay+bh,fill=wall,outline="#392b25",width=3)
   canvas.create_polygon(ax-12,ay+9,ax+bw/2,ay-29,ax+bw+12,ay+9,fill=roof,outline="#3e302a",width=3)
   canvas.create_rectangle(ax+bw/2-12,ay+bh-29,ax+bw/2+12,ay+bh,fill="#3a2f29",outline="#d0a671",width=2)
   short=building_name[len(name)+1:]
   canvas.create_text(ax+bw/2,ay+26,text=short.upper(),font=("DejaVu Sans",8,"bold"),fill="#f2d5a5")
  # Oil lamps for evening ambience (not physics obstacles).
  for ox in (-195,190):
   canvas.create_line(sx+ox,sy+62,sx+ox,sy+116,fill="#493b30",width=5)
   canvas.create_oval(sx+ox-7,sy+56,sx+ox+7,sy+74,fill="#e0b96b",outline="#4c3827",width=2)
  # Distinct regional monuments anchored to the actual illustrated city centers.
  # None are solid; gameplay collision stays bounded to authored buildings.
  if key=='drybone':  # Galloway railway gantry and signal
   canvas.create_line(sx+225,sy-100,sx+225,sy-195,fill='#6a5647',width=9)
   canvas.create_line(sx+225,sy-175,sx+330,sy-175,fill='#6a5647',width=8)
   canvas.create_oval(sx+316,sy-187,sx+344,sy-161,fill='#ca8d5a',outline='#4f3c2d',width=3)
   caption='RAILWAY DISPATCH'
  elif key=='ironwell':  # Iron Mesa derrick
   canvas.create_polygon(sx+245,sy-48,sx+292,sy-185,sx+333,sy-48,
                         fill='#8c694d',outline='#513d34',width=4)
   for height in (-80,-112,-144):
    canvas.create_line(sx+260,sy+height,sx+321,sy+height,fill='#d1a879',width=4)
   caption='IRON MESA SHAFT'
  elif key=='painted':  # Dustwell windpump
   canvas.create_line(sx+287,sy-50,sx+287,sy-179,fill='#6c624e',width=7)
   for i in range(8):
    import math
    angle=i*math.tau/8
    canvas.create_line(sx+287,sy-169,sx+287+math.cos(angle)*45,
                       sy-169+math.sin(angle)*45,fill='#b4a388',width=5)
   caption='DUSTWELL PUMP'
  elif key=='saltwater':  # Roan Creek skiff
   canvas.create_polygon(sx+223,sy+195,sx+333,sy+195,sx+310,sy+224,
                         sx+243,sy+224,fill='#74543a',outline='#473b30',width=4)
   canvas.create_line(sx+278,sy+197,sx+278,sy+142,fill='#71563d',width=5)
   canvas.create_polygon(sx+279,sy+142,sx+310,sy+185,sx+279,sy+185,fill='#ddd1aa')
   caption='CREEK LANDING'
  elif key=='ember':  # Larkfield market bell
   canvas.create_line(sx+275,sy-60,sx+275,sy-172,fill='#755743',width=9)
   canvas.create_polygon(sx+246,sy-150,sx+303,sy-150,sx+294,sy-117,
                         sx+253,sy-117,fill='#c8a15d',outline='#58432f',width=3)
   caption='LARKFIELD MARKET'
  else:  # Riversend river gauge
   for height in range(6):
    canvas.create_rectangle(sx+249,sy-146+height*17,sx+309,sy-130+height*17,
                            fill='#8b9c95' if height%2 else '#c8ad7a',
                            outline='#5e5846',width=2)
   caption='RIVERSEND GAUGE'
  canvas.create_text(sx+280,sy-207,text=caption,fill='#50382b',
                     font=('DejaVu Sans',9,'bold'))
