"""Data-driven frontier settlements, handcrafted side jobs, and lightweight scene art.
Only Python/Tkinter; no extra media, packages, or engine dependencies.
"""
# Settlements sit along the existing procedural north/south and east/west roads.
# key, display name, center (world coordinates), wall/roof palette, local character
SETTLEMENTS=(
 ("drybone","Drybone Junction",6000,4300,"#866e50","#70513f","Ada Pike"),
 ("ironwell","Ironwell",10200,4300,"#817b68","#595958","Silas Flint"),
 ("painted","Painted Mesa",14400,4300,"#a07454","#784837","Rose Ortega"),
 ("saltwater","Saltwater Crossing",6000,7900,"#857f66","#536b62","Jonah Reed"),
 ("ember","Ember Gulch",10200,7900,"#956447","#663d35","Mara Ash"),
 ("sundown","Sundown Station",14400,7900,"#a1895e","#665943","Caleb West"),
)
# Each job is a named multi-stage expedition; E interacts with each objective.
# key, originating settlement, title, instruction, world targets, reward
SIDE_JOBS=(
 ("lost_mail","drybone","The Missing Mailbag","Recover two lost mailbags along the Drybone trail",
  ((6630,4680),(6820,5320)),75),
 ("ore_samples","ironwell","The Ironwell Survey","Retrieve two samples of ore from the old shaft",
  ((10960,4750),(11250,5250)),95),
 ("painted_marks","painted","Signs in the Dust","Follow the painted markers and find the scout's notebook",
  ((15220,4680),(15630,5130)),110),
 ("river_supplies","saltwater","Supplies Downriver","Find the lost medicine crate and the ferry manifest",
  ((6740,8450),(7100,8910)),90),
 ("ember_ledger","ember","The Smuggler's Account","Recover the stolen ledger and its missing seal",
  ((11000,8240),(11400,8730)),135),
 ("sundown_signal","sundown","Last Signal West","Collect the telegraph parts and repair notes",
  ((15150,8460),(15820,8960)),150),
)
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
