#!/usr/bin/env python3
"""DUST & DEBT — an original, single-player, top-down Western adventure.
Runtime: Python 3 and Tk 8.6 (tkinter), no pip modules required.
"""
import tkinter as tk
from tkinter import messagebox
import os, math, random, json, time, textwrap, sys
from dataclasses import dataclass

ROOT=os.path.dirname(os.path.abspath(__file__))
ASSETS=os.path.join(ROOT,'assets')
SAVE=os.path.join(os.path.expanduser('~'),'.local','share','dust-and-debt','save.json')
VW,VH=960,600
WW,WH=4800,3200
FPS=33
random.seed()

BUILDINGS=[('Sheriff',320,300,196,130),('Saloon',565,315,238,160),('General Store',854,318,204,144),('Doctor',320,694,169,120),('Stable',835,728,210,144),('Hotel',540,735,215,168),('Station',1150,1321,240,115),('Cabin',1670,320,140,110),('Outpost',1960,1150,140,100),('Ranch',1470,850,160,125),
 ('Trading Post',3250,1650,200,145),('Sagebrush Saloon',3530,1650,220,150),
 ('Sheriff Annex',3250,1910,185,120),('Livery',3510,1905,205,140),
 ('Fishing Shack',910,2445,140,105),('Lake Cabin',1150,2440,150,110),
 ('Watchtower',3770,1060,128,120),('Mesa Camp',4050,1320,125,110),
 ('Copper Mine',4090,2450,225,155),('Assay Office',4420,2440,165,120),
 ('Bunkhouse',4060,2700,200,120),('Ghost Chapel',2900,2690,170,145),
 ('South Ranch',710,2040,190,140),('Windmill',940,2140,90,90),
 ('Riverside Camp',2320,2550,140,100),('Old Mission',4550,1870,185,150),
 ('Smuggler Shed',3500,2900,160,110)]
NPCS=[('Sheriff Bell',418,463,'sheriff'),('Mae the barkeep',682,501,'saloon'),('Silas the trader',956,492,'store'),('Doc Harper',406,845,'doctor'),('Ezra the stablehand',935,904,'stable'),('Nell the stationmaster',1270,1465,'station'),('Martha',750,550,'civilian'),('Old Pete',557,625,'civilian'),('Clay',882,665,'civilian'),('Vera',1050,690,'civilian'),('Ruth',366,600,'civilian'),('Otis',1095,530,'civilian'),
 ('Rowan the trader',3340,1815,'store'),('Pearl the barkeep',3630,1820,'saloon'),
 ('Frank the stablehand',3610,2065,'stable'),('Deputy Grace',3340,2050,'sheriff'),
 ('Lakekeeper Ada',1090,2600,'civilian'),('Prospector Finn',4320,2615,'civilian'),
 ('Mina the miner',4480,2590,'civilian'),('Rancher Amos',810,2220,'civilian'),
 ('Riverboat Eli',2490,2700,'civilian'),('Brother Thomas',3000,2860,'civilian')]
MISSIONS=[
 ('The Sheriff\'s Offer','Visit Sheriff Bell outside the jail in Cinder Creek.'),
 ('Dust Hollow','Ride northeast to Dust Hollow and eliminate the five Red Mesa riders.'),
 ('Blood Money','Return to Sheriff Bell for your payment.'),
 ('A Missing Manifest','Talk to Nell at the railroad station to the southeast.'),
 ('The Blackspur Ledger','Ride to Blackspur Outpost, eliminate its guards, and retrieve the ledger.'),
 ('Paper Trail','Bring the stolen ledger to Nell at the railroad station.'),
 ('High Noon at the Ranch','Find outlaw leader Crow and his gang at the southern ranch.'),
 ('A Debt Settled','Return to Sheriff Bell to collect the final reward.'),
 ('Free Roam','The story is complete. Explore, hunt outlaws, and live another day.')]

@dataclass
class Actor:
 x:float
 y:float
 kind:str
 name:str=''
 hp:float=100
 maxhp:float=100
 speed:float=70
 shoot:float=0
 wander:float=0
 dx:float=0
 dy:float=0
 dead:bool=False
 loot:bool=False

class Game:
 def __init__(self,root):
  self.root=root;root.title('DUST & DEBT | A Western Adventure')
  root.resizable(False,False)
  self.canvas=tk.Canvas(root,width=VW,height=VH,bg='#19140f',highlightthickness=0,cursor='crosshair')
  self.canvas.pack()
  self.world=tk.PhotoImage(file=os.path.join(ASSETS,'world.png'))
  self.titleimg=tk.PhotoImage(file=os.path.join(ASSETS,'title.png'))
  self.mapimg=tk.PhotoImage(file=os.path.join(ASSETS,'map.png'))
  self.keys=set();self.mouse=(VW//2,VH//2);self.mouse_down=False
  self.screen='title';self.fullscreen=False
  self.font='DejaVu Sans';self.last=time.monotonic();self.frame=0
  self.reset()
  root.bind('<KeyPress>',self.key_down);root.bind('<KeyRelease>',self.key_up)
  root.bind('<Motion>',lambda e:setattr(self,'mouse',(e.x,e.y)))
  root.bind('<ButtonPress-1>',self.click);root.bind('<ButtonRelease-1>',lambda e:setattr(self,'mouse_down',False))
  root.protocol('WM_DELETE_WINDOW',self.quit)
  root.after(FPS,self.loop)

 def reset(self):
  self.x,self.y=698.,610.;self.hp=100.;self.maxhp=100;self.money=35;self.ammo=6;self.reserve=42;self.tonics=2
  self.stage=0;self.kills=0;self.wanted=0.;self.law_timer=0.;self.clock=8.0;self.mounted=False
  self.horse_x,self.horse_y=764.,646.;self.horse_hp=100
  self.facing=(0.,-1.);self.shot_timer=0;self.reload_timer=0;self.invuln=0
  self.actors=[];self.bullets=[];self.effects=[];self.dialog=None;self.dialog_from='';self.toast=[]
  self.camx=0;self.camy=0;self.map_open=False;self.journal_open=False;self.show_help=False
  self.wins=0;self.mission_activated=set();self.ledger=False;self.quest_total=0;self.death_count=0;self.last_region='Cinder Creek'
  for n,x,y,kind in NPCS: self.actors.append(Actor(x,y,kind,n,100,100,42))
  self.spawn_roamers()

 def spawn_roamers(self):
  for i in range(23):
   x,y=random.choice([(1260,320),(1550,310),(1850,680),(2180,930),(1610,1350),(300,1120),(850,1160),(2150,1460),(3060,1100),(4150,1130),(4300,2000),(3690,2840),(2880,2950),(1750,2190),(750,2960)])
   self.actors.append(Actor(x+random.randint(-65,65),y+random.randint(-70,70),'bandit','Drifter',70,70,75))
  for i in range(38):
   x=random.randint(120,WW-150);y=random.randint(100,WH-120)
   if self.in_town(x,y):continue
   self.actors.append(Actor(x,y,'animal',random.choice(['Coyote','Jackrabbit']),24,24,85))

 def in_town(self,x,y):return 245<x<1150 and 230<y<960
 def solid(self,x,y,r=11):
  if x<23 or y<23 or x>WW-23 or y>WH-23:return True
  for n,bx,by,bw,bh in BUILDINGS:
   if bx-r<x<bx+bw+r and by-r<y<by+bh+r:return True
  return False
 def can_move(self,x,y,r=11):return not self.solid(x,y,r)
 def move_actor(self,a,dx,dy):
  if self.can_move(a.x+dx,a.y,9):a.x+=dx
  if self.can_move(a.x,a.y+dy,9):a.y+=dy

 def notify(self,s,t=3.5):self.toast.append([s,t]);self.toast=self.toast[-5:]
 def say(self,speaker,lines):
  if isinstance(lines,str):lines=[lines]
  self.dialog=[speaker,lines,0]
 def quest(self,stage):
  self.stage=stage;self.notify('NEW OBJECTIVE: '+MISSIONS[stage][0].upper(),5)
  self.save()
  if stage==1:self.spawn_mission('hollow',[(1780,420),(1840,390),(1888,440),(1840,537),(1778,528)],95)
  if stage==4:self.spawn_mission('blackspur',[(1975,1290),(2080,1280),(2030,1340)],105)
  if stage==6:self.spawn_mission('crow',[(1370,1030),(1430,1100),(1510,1080),(1580,1030)],115,boss=(1480,1030))
 def spawn_mission(self,tag,positions,hp,boss=None):
  if tag in self.mission_activated:return
  self.mission_activated.add(tag)
  for i,(x,y) in enumerate(positions):
   self.actors.append(Actor(x,y,'mission_'+tag,tag.title()+' rider',hp,hp,91))
  if boss:self.actors.append(Actor(boss[0],boss[1],'mission_'+tag,'Crow',240,240,105))
 def enemies_remaining(self,tag):return sum(not a.dead and a.kind=='mission_'+tag for a in self.actors)

 def key_down(self,e):
  key=e.keysym.lower();first=key not in self.keys;self.keys.add(key)
  if not first:return
  if key=='f11':
   self.fullscreen=not self.fullscreen;self.root.attributes('-fullscreen',self.fullscreen);return
  if self.screen=='title':
   if key in ('return','space','n'):self.new_game()
   elif key in ('l','c') and os.path.exists(SAVE):self.continue_game()
   elif key=='escape':self.quit()
   return
  if self.screen=='death':
   if key in ('return','space'):self.respawn()
   elif key=='escape':self.screen='title'
   return
  if self.screen=='ending':
   if key in ('return','space','escape'):self.screen='playing';self.save()
   return
  if self.dialog:
   if key in ('return','space','e'):self.advance_dialog()
   return
  if key=='escape':self.screen='playing' if self.screen=='paused' else 'paused';return
  if self.screen=='paused':return
  if key=='f1':self.show_help=not self.show_help
  elif key=='m':self.map_open=not self.map_open;self.journal_open=False
  elif key=='j':self.journal_open=not self.journal_open;self.map_open=False
  elif key=='e':self.interact()
  elif key=='h':self.toggle_horse()
  elif key=='r':self.reload()
  elif key=='1':self.tonic()
  elif key=='space':self.fire()
  elif key=='f5':self.save();self.notify('Game saved.')

 def key_up(self,e):self.keys.discard(e.keysym.lower())
 def click(self,e):
  if self.screen=='title':
   if 397<e.y<458:self.new_game()
   elif 467<e.y<515 and os.path.exists(SAVE):self.continue_game()
  elif self.screen=='playing' and not self.dialog and not self.map_open and not self.journal_open:
   self.mouse_down=True;self.mouse=(e.x,e.y);self.fire()
  elif self.screen in ('death','ending'):self.key_down(type('E',(),{'keysym':'Return'})())
 def new_game(self):self.reset();self.screen='playing';self.say('NARRATOR',['1889. The borderlands have no patience for saints.','Your name is Jesse Vale. You have $35, six rounds, and a horse named Whiskey.','Sheriff Bell is looking for someone with nothing left to lose. Find him at the jail.']);self.save()
 def continue_game(self):
  self.reset()
  try:
   with open(SAVE) as f:s=json.load(f)
   for k in ('x','y','hp','money','ammo','reserve','tonics','stage','kills','wanted','clock','mounted','horse_x','horse_y','ledger','death_count'):
    if k in s:setattr(self,k,s[k])
   self.mission_activated=set(s.get('mission_activated',[]))
   # Quest combat must regenerate after loading (kill progress is persisted).
   tag={1:'hollow',4:'blackspur',6:'crow'}.get(self.stage)
   if tag:
    self.mission_activated.discard(tag)
    positions={'hollow':[(1780,420),(1840,390),(1888,440),(1840,537),(1778,528)],'blackspur':[(1975,1290),(2080,1280),(2030,1340)],'crow':[(1370,1030),(1430,1100),(1510,1080),(1580,1030)]}[tag]
    self.spawn_mission(tag,positions,{'hollow':95,'blackspur':105,'crow':115}[tag],boss=(1480,1030) if tag=='crow' else None)
    eliminated=int(s.get('stage_kills',0))
    for a in [a for a in self.actors if a.kind=='mission_'+tag][:eliminated]:a.dead=True
   self.screen='playing';self.notify('Welcome back to Cinder Creek.')
  except (OSError,ValueError,TypeError,KeyError) as ex:
   self.new_game();self.notify('Save unavailable. New game started.')
 def save(self):
  if self.screen not in ('playing','paused','ending'):return
  d={k:getattr(self,k) for k in ('x','y','hp','money','ammo','reserve','tonics','stage','kills','wanted','clock','mounted','horse_x','horse_y','ledger','death_count')}
  d['mission_activated']=list(self.mission_activated)
  tag={1:'hollow',4:'blackspur',6:'crow'}.get(self.stage)
  if tag:
   d['stage_kills']=sum(a.dead for a in self.actors if a.kind=='mission_'+tag)
  try:
   os.makedirs(os.path.dirname(SAVE),exist_ok=True)
   tmp=SAVE+'.tmp'
   with open(tmp,'w') as f:json.dump(d,f)
   os.replace(tmp,SAVE)
  except OSError:pass

 def quest_target(self):
  return [(418,463),(1840,470),(418,463),(1270,1465),(2040,1280),(1270,1465),(1480,1030),(418,463),None][self.stage]
 def advance_dialog(self):
  if not self.dialog:return
  self.dialog[2]+=1
  if self.dialog[2]>=len(self.dialog[1]):self.dialog=None
 def interact(self):
  nearest=None;best=64
  for a in self.actors:
   if a.dead or a.kind.startswith('mission_') or a.kind in ('bandit','animal','deputy'):continue
   dist=math.hypot(a.x-self.x,a.y-self.y)
   if dist<best:nearest=a;best=dist
  if nearest is None:
   if self.stage==4 and math.hypot(self.x-2040,self.y-1280)<95 and self.enemies_remaining('blackspur')==0:
    self.ledger=True;self.quest(5);self.say('JESSE',['Under a loose floorboard: the stolen manifest.','The pages name Crow as the man who bought the railroad robbery. Nell needs to see this.'])
   else:self.notify('Nobody nearby to talk to. Walk up to a character and press E.',2)
   return
  k=nearest.kind
  if k=='sheriff':
   if self.stage==0:
    self.quest(1);self.say('SHERIFF BELL',['We have five Red Mesa riders camped northeast at Dust Hollow.','They hit the stagecoach and left the passengers in the dirt. I need someone who can shoot.','Bring me the news they are gone. Eighty dollars. No questions about your past.'])
   elif self.stage==2:
    self.money+=80;self.reserve+=18;self.wanted=0;self.quest(3)
    self.say('SHERIFF BELL',['Five fewer devils in the territory. Here is your $80 and some cartridges.','The gang stole railroad papers too. Nell at the southeastern station can tell you more.'])
   elif self.stage==7:
    self.money+=250;self.wanted=0;self.stage=8;self.wins+=1;self.save();self.screen='ending'
   elif self.wanted>0:
    self.say('SHERIFF BELL',['You are carrying heat. The law does not overlook trouble in Cinder Creek.','Keep your hands clean and stay out of sight until your wanted level cools.'])
   else:self.say('SHERIFF BELL',['Crow left friends scattered across the territory. They may still be worth a bounty.','Watch your ammunition and keep your horse watered.'])
  elif k=='station':
   if self.stage==3:
    self.quest(4);self.say('NELL',['They took our manifest. The black leather ledger. Names, freight orders, payoffs.','The thieves are holed up at Blackspur Outpost in the southeast.','Bring back the ledger and I will pay you $125.'])
   elif self.stage==5:
    self.money+=125;self.ledger=False;self.quest(6)
    self.say('NELL',['Here is your $125. The proof is all here: railroad robberies, bought guards, and Crow.','The gang boss is waiting at the ranch south of town. End this before he flees.'])
   else:self.say('NELL',['These rails run east. Trouble travels both ways.','There are still bandits along the desert roads.'])
  elif k=='store':
   if self.money>=18:self.money-=18;self.reserve+=30;self.notify('Bought 30 revolver rounds for $18.')
   else:self.notify('Trader: Ammo costs $18. Not enough money.')
   self.save()
  elif k=='doctor':
   if self.hp>=self.maxhp:self.say('DOC HARPER',['You look healthy enough. Try to keep it that way.'])
   elif self.money>=15:self.money-=15;self.hp=self.maxhp;self.say('DOC HARPER',['Fifteen dollars. Clean bandages and a steady hand. You will live.']);self.save()
   else:self.say('DOC HARPER',['Treatment costs $15. I cannot feed my family on promises.'])
  elif k=='stable':
   self.horse_hp=100;self.horse_x,self.horse_y=nearest.x+45,nearest.y+25
   self.say('EZRA',['Whiskey is fed, watered, and ready to ride.','Press H while near your horse to mount or dismount.'])
  elif k=='saloon':
   if self.money>=5:self.money-=5;self.hp=min(100,self.hp+20);self.say('MAE',['Five dollars for a drink and a quiet chair.','Your wounds sting a little less now.']);self.save()
   else:self.say('MAE',['Whiskey costs $5. Stories are free.'])
  else:self.say(nearest.name.upper(),[random.choice(['A storm is coming off the mesa.','Best stay out of Blackspur country.','Folks say the railroad has been paying bandits.','Cinder Creek was never a peaceful town.'])])

 def toggle_horse(self):
  if self.mounted:
   self.mounted=False;self.horse_x=self.x+28;self.horse_y=self.y+10;self.notify('Dismounted Whiskey.')
  elif math.hypot(self.x-self.horse_x,self.y-self.horse_y)<75:
   self.mounted=True;self.notify('Mounted Whiskey. Hold Shift to gallop.')
  else:self.notify('Get closer to Whiskey to mount (H).')
 def tonic(self):
  if self.tonics<=0:self.notify('No tonics left.');return
  if self.hp>=100:self.notify('Already at full health.');return
  self.tonics-=1;self.hp=min(100,self.hp+55);self.notify('Used a tonic: +55 health.');self.save()
 def reload(self):
  if self.reload_timer>0 or self.ammo==6:return
  if self.reserve<=0:self.notify('Out of ammunition. Visit the general store.');return
  self.reload_timer=1.15;self.notify('Reloading...',1.2)
 def fire(self):
  if self.screen!='playing' or self.dialog or self.shot_timer>0 or self.reload_timer>0 or self.map_open or self.journal_open:return
  if self.ammo<=0:self.reload();return
  self.ammo-=1;self.shot_timer=.25
  mx,my=self.mouse;dx=(mx+self.camx)-self.x;dy=(my+self.camy)-self.y
  if abs(dx)+abs(dy)<15:dx,dy=self.facing
  mag=max(.001,math.hypot(dx,dy));dx/=mag;dy/=mag
  self.facing=(dx,dy)
  self.bullets.append([self.x+dx*19,self.y+dy*19,dx*710,dy*710,1.0,True])
  self.effects.append([self.x+dx*22,self.y+dy*22,.14,'flash'])
  if self.in_town(self.x,self.y):
   self.wanted=min(5.,self.wanted+.55);self.law_timer=3.
  if self.ammo==0:self.notify('Cylinder empty — R to reload.',1.5)

 def respawn(self):
  self.death_count+=1;self.hp=100;self.x,self.y=700,620;self.money=max(0,self.money-25);self.wanted=0
  self.ammo=6;self.reserve=max(24,self.reserve);self.tonics=max(1,self.tonics);self.mounted=False
  self.horse_x,self.horse_y=764,646;self.screen='playing';self.notify('You woke up at the doctor. Lost up to $25.');self.save()

 def loop(self):
  now=time.monotonic();dt=min(.06,now-self.last);self.last=now
  try:
   if self.screen=='playing' and not self.dialog:
    self.update(dt)
   self.render()
  except Exception as ex:
   import traceback;traceback.print_exc()
   self.screen='paused';self.notify('Unexpected error — see terminal.')
  self.root.after(FPS,self.loop)

 def update(self,dt):
  self.frame+=1;self.clock=(self.clock+dt*.032)%24
  self.shot_timer=max(0,self.shot_timer-dt);self.invuln=max(0,self.invuln-dt)
  if self.reload_timer>0:
   self.reload_timer-=dt
   if self.reload_timer<=0:
    n=min(6-self.ammo,self.reserve);self.ammo+=n;self.reserve-=n;self.notify('Revolver reloaded.',1.1)
  for toast in self.toast:toast[1]-=dt
  self.toast=[t for t in self.toast if t[1]>0]
  for fx in self.effects:fx[2]-=dt
  self.effects=[a for a in self.effects if a[2]>0]
  vx=(int('d' in self.keys or 'right' in self.keys)-int('a' in self.keys or 'left' in self.keys))
  vy=(int('s' in self.keys or 'down' in self.keys)-int('w' in self.keys or 'up' in self.keys))
  if vx or vy:
   mag=math.hypot(vx,vy);vx/=mag;vy/=mag
   speed=(260 if 'shift_l' in self.keys or 'shift_r' in self.keys else 205) if self.mounted else (175 if 'shift_l' in self.keys or 'shift_r' in self.keys else 125)
   if self.can_move(self.x+vx*speed*dt,self.y,16 if self.mounted else 10):self.x+=vx*speed*dt
   if self.can_move(self.x,self.y+vy*speed*dt,16 if self.mounted else 10):self.y+=vy*speed*dt
   self.facing=(vx,vy)
  if self.frame%40==0:
   region=self.region_name(self.x,self.y)
   if region!=self.last_region:
    self.last_region=region;self.notify('NOW ENTERING: '+region.upper(),3.4)
  if self.mouse_down:self.fire()
  self.camx=max(0,min(WW-VW,int(self.x-VW/2)));self.camy=max(0,min(WH-VH,int(self.y-VH/2)))
  if self.wanted>0:
   self.law_timer=max(0,self.law_timer-dt)
   if self.law_timer==0 and not self.in_town(self.x,self.y):self.wanted=max(0,self.wanted-dt*.027)
   if self.law_timer==0 and self.in_town(self.x,self.y):self.wanted=max(0,self.wanted-dt*.008)
  self.update_ai(dt)
  self.update_bullets(dt)
  if self.stage==1 and self.enemies_remaining('hollow')==0:self.quest(2);self.say('JESSE',['Dust Hollow is quiet. Five more graves for the desert.','Bell promised eighty dollars. Time to collect.'])
  if self.stage==6 and self.enemies_remaining('crow')==0:self.quest(7);self.say('JESSE',['Crow is down. His reign ends here, on a patch of dirt nobody will remember.','Bell deserves to hear it from me.'])
  if self.hp<=0:self.screen='death';self.mounted=False
  if self.frame%300==0:self.save()

 def update_ai(self,dt):
  for a in self.actors:
   if a.dead:continue
   if a.kind in ('sheriff','store','doctor','stable','saloon','station'):continue
   a.shoot=max(0,a.shoot-dt);a.wander-=dt
   dist=math.hypot(a.x-self.x,a.y-self.y)
   ishostile=a.kind in ('bandit','deputy') or a.kind.startswith('mission_')
   if a.kind=='civilian':
    if self.wanted>1 and dist<220:dx,dy=a.x-self.x,a.y-self.y
    else:
     if a.wander<0:
      a.wander=random.uniform(1,4);a.dx=random.uniform(-1,1);a.dy=random.uniform(-1,1)
     dx,dy=a.dx,a.dy
    mag=max(1,math.hypot(dx,dy));self.move_actor(a,dx/mag*a.speed*dt,dy/mag*a.speed*dt)
   elif a.kind=='animal':
    if dist<130:dx,dy=a.x-self.x,a.y-self.y
    else:
     if a.wander<0:a.wander=random.uniform(1,3);a.dx=random.uniform(-1,1);a.dy=random.uniform(-1,1)
     dx,dy=a.dx,a.dy
    mag=max(1,math.hypot(dx,dy));self.move_actor(a,dx/mag*a.speed*dt,dy/mag*a.speed*dt)
   elif ishostile and dist<480:
    if a.kind=='deputy' and self.wanted<.5:a.dead=True;continue
    dx=self.x-a.x;dy=self.y-a.y;mag=max(.001,dist)
    if dist>155:self.move_actor(a,dx/mag*a.speed*dt,dy/mag*a.speed*dt)
    if dist<340 and a.shoot<=0:
     a.shoot=random.uniform(1.3,2.5) if a.name!='Crow' else .65
     scatter=random.uniform(-.14,.14)
     angle=math.atan2(dy,dx)+scatter
     self.bullets.append([a.x,a.y,math.cos(angle)*340,math.sin(angle)*340,1.3,False])
  if self.wanted>=1.2 and self.law_timer<=0:
   deputies=sum(not a.dead and a.kind=='deputy' for a in self.actors)
   if deputies<min(4,1+int(self.wanted)) and self.frame%180==0:
    ang=random.random()*math.tau;x=self.x+math.cos(ang)*370;y=self.y+math.sin(ang)*320
    if self.can_move(x,y):self.actors.append(Actor(x,y,'deputy','Deputy',95,95,94))

 def update_bullets(self,dt):
  kept=[]
  for b in self.bullets:
   ox,oy=b[0],b[1];b[0]+=b[2]*dt;b[1]+=b[3]*dt;b[4]-=dt
   collided=False
   # Segment sampled every 15 px to prevent tunneling.
   steps=max(1,int(math.hypot(b[0]-ox,b[1]-oy)/12))
   for i in range(1,steps+1):
    px=ox+(b[0]-ox)*i/steps;py=oy+(b[1]-oy)*i/steps
    if self.solid(px,py,2):collided=True;self.effects.append([px,py,.20,'dust']);break
    if b[5]:
     for a in self.actors:
      if a.dead or a.kind=='animal' and a.name=='Jackrabbit' and random.random()<.12:continue
      if math.hypot(a.x-px,a.y-py)<(17 if a.name=='Crow' else 13):
       if a.kind in ('sheriff','store','doctor','stable','saloon','station'):
        self.wanted=min(5,self.wanted+2);self.law_timer=6
        self.notify('LAW ALERT: You attacked an innocent!')
        a.hp-=32
       elif a.kind=='civilian':
        self.wanted=min(5,self.wanted+2);self.law_timer=6;a.hp-=55
       else:a.hp-=52
       self.effects.append([px,py,.30,'hit']);collided=True
       if a.hp<=0:
        a.dead=True
        if a.kind in ('bandit','deputy') or a.kind.startswith('mission_'):
         if a.kind=='deputy':self.wanted=min(5,self.wanted+1.5)
         else:
          reward=8 if a.kind=='bandit' else 5
          self.money+=reward;self.kills+=1;self.notify('Outlaw down! +$'+str(reward),1.7)
        elif a.kind in ('civilian','sheriff','store','doctor','stable','saloon','station'):self.wanted=5.;self.notify('MURDER! Wanted level maximum.')
       break
    else:
     if math.hypot(self.x-px,self.y-py)<(17 if self.mounted else 11):
      collided=True
      if self.invuln<=0:
       self.hp-=random.randrange(9,18);self.invuln=.35;self.effects.append([px,py,.35,'hit'])
      break
    if collided:break
   if not collided and b[4]>0:kept.append(b)
  self.bullets=kept

 def draw_text(self,x,y,s,size=13,color='#ead8b3',bold=False,anchor='nw',shadow=True,width=None):
  font=(self.font,size,'bold' if bold else 'normal')
  if shadow:self.canvas.create_text(x+1,y+2,text=s,fill='#211912',font=font,anchor=anchor,width=width)
  self.canvas.create_text(x,y,text=s,fill=color,font=font,anchor=anchor,width=width)
 def panel(self,x,y,w,h,fill='#221c18',edge='#b68b54'):
  self.canvas.create_rectangle(x+3,y+4,x+w+3,y+h+4,fill='#140f0d',outline='')
  self.canvas.create_rectangle(x,y,x+w,y+h,fill=fill,outline=edge,width=2)
 def pos(self,x,y):return int(x-self.camx),int(y-self.camy)
 def draw_actor(self,a):
  sx,sy=self.pos(a.x,a.y)
  if sx< -40 or sy< -45 or sx>VW+40 or sy>VH+40:return
  if a.dead:
   self.canvas.create_oval(sx-12,sy-3,sx+13,sy+6,fill='#6e4b3c',outline='')
   self.canvas.create_line(sx-9,sy-4,sx+9,sy+5,fill='#44352e',width=5)
   return
  if a.kind=='animal':
   co='#aa8963' if a.name=='Coyote' else '#c4ae87'
   self.canvas.create_oval(sx-12,sy-6,sx+13,sy+6,fill=co,outline='#65523e')
   self.canvas.create_oval(sx+7,sy-9,sx+16,sy,fill=co,outline='#65523e')
   return
  villain=a.kind in ('bandit','deputy') or a.kind.startswith('mission_')
  clothes=('#3e4b59' if a.kind=='deputy' else '#694332') if villain else {'sheriff':'#384a4f','saloon':'#973f50','store':'#747143','doctor':'#e0d0a4','stable':'#55644a','station':'#526783'}.get(a.kind,'#73654f')
  # Lower shadow, boots, poncho, head and hat: tiny expressive pixel figure.
  self.canvas.create_oval(sx-13,sy+8,sx+15,sy+15,fill='#6d563f',outline='')
  self.canvas.create_rectangle(sx-9,sy+4,sx-2,sy+13,fill='#312c2a',outline='')
  self.canvas.create_rectangle(sx+2,sy+4,sx+9,sy+13,fill='#312c2a',outline='')
  self.canvas.create_rectangle(sx-11,sy-10,sx+11,sy+8,fill=clothes,outline='#362f2c',width=2)
  self.canvas.create_oval(sx-7,sy-21,sx+7,sy-5,fill='#c9956d',outline='#5b3c2a')
  hat='#342824' if villain else '#684732'
  self.canvas.create_rectangle(sx-9,sy-24,sx+9,sy-14,fill=hat,outline='')
  self.canvas.create_rectangle(sx-15,sy-17,sx+15,sy-13,fill=hat,outline='')
  if a.name=='Crow':
   self.canvas.create_rectangle(sx-11,sy-12,sx+11,sy+7,fill='#341e21',outline='#b44538',width=2)
  if a.kind=='sheriff':self.canvas.create_polygon(sx,sy-3,sx+5,sy,sx+2,sy+5,sx-2,sy+5,sx-5,sy,fill='#ecc46b')
  if villain and a.hp<a.maxhp:
   self.canvas.create_rectangle(sx-16,sy-34,sx+16,sy-30,fill='#3d201c',outline='')
   self.canvas.create_rectangle(sx-16,sy-34,sx-16+32*max(0,a.hp)/a.maxhp,sy-30,fill='#b84f40',outline='')
  if math.hypot(a.x-self.x,a.y-self.y)<125 and not villain:
   self.draw_text(sx,sy-43,a.name,11,'#f3db9e',True,anchor='center')

 def draw_player(self):
  sx,sy=self.pos(self.x,self.y)
  if not self.mounted:
   hx,hy=self.pos(self.horse_x,self.horse_y)
   if -60<hx<VW+60 and -60<hy<VH+60:self.draw_horse(hx,hy)
  else:self.draw_horse(sx,sy+9)
  self.canvas.create_oval(sx-12,sy+8,sx+14,sy+16,fill='#836845',outline='')
  offset=-7 if self.mounted else 0
  self.canvas.create_rectangle(sx-9,sy-7+offset,sx+9,sy+10+offset,fill='#344e50',outline='#1c292b',width=2)
  self.canvas.create_rectangle(sx-10,sy+3+offset,sx+10,sy+7+offset,fill='#95673a',outline='')
  self.canvas.create_oval(sx-7,sy-20+offset,sx+7,sy-5+offset,fill='#d3a27a',outline='#533b2a')
  self.canvas.create_rectangle(sx-9,sy-24+offset,sx+9,sy-14+offset,fill='#5d3e2c',outline='')
  self.canvas.create_rectangle(sx-17,sy-17+offset,sx+17,sy-13+offset,fill='#5d3e2c',outline='')
  dx,dy=self.facing
  self.canvas.create_line(sx+dx*6,sy+dy*6+offset,sx+dx*25,sy+dy*25+offset,fill='#3a3530',width=7)
  self.canvas.create_line(sx+dx*9,sy+dy*9+offset,sx+dx*25,sy+dy*25+offset,fill='#beb4a2',width=3)
  if self.invuln>0:self.canvas.create_oval(sx-23,sy-30,sx+23,sy+20,outline='#eead90',width=2)
 def draw_horse(self,sx,sy):
  self.canvas.create_oval(sx-19,sy-18,sx+22,sy+24,fill='#5b3d2d',outline='#31291f',width=2)
  self.canvas.create_oval(sx-12,sy-24,sx+11,sy-4,fill='#7b5338',outline='#34271f',width=2)
  for x in (-12,11):
   self.canvas.create_rectangle(sx+x-3,sy+15,sx+x+4,sy+29,fill='#493128',outline='')
  self.canvas.create_rectangle(sx-12,sy-1,sx+13,sy+9,fill='#372b29',outline='#b59260')
  self.canvas.create_line(sx-4,sy+18,sx-18,sy+35,fill='#342823',width=3)

 def draw_world(self):
  self.canvas.create_image(-self.camx,-self.camy,image=self.world,anchor='nw')
  for a in sorted(self.actors,key=lambda a:a.y):self.draw_actor(a)
  if self.stage==4 and self.enemies_remaining('blackspur')==0 and not self.ledger:
   x,y=self.pos(2040,1280)
   self.canvas.create_rectangle(x-9,y-12,x+9,y+12,fill='#e5c283',outline='#423628',width=2)
   self.draw_text(x,y-32,'E: TAKE LEDGER',12,'#fff2b6',True,anchor='center')
  self.draw_player()
  for b in self.bullets:
   bx,by=self.pos(b[0],b[1]);self.canvas.create_oval(bx-3,by-3,bx+3,by+3,fill='#ffe1a4' if b[5] else '#f18f61',outline='')
  for x,y,t,kind in self.effects:
   sx,sy=self.pos(x,y);radius=int(4+t*25)
   col={'dust':'#d2b388','hit':'#b7523b','flash':'#ffe4ac'}.get(kind,'white')
   self.canvas.create_oval(sx-radius,sy-radius,sx+radius,sy+radius,outline=col,width=3)
  # Nightfall through stippled dark field, with a warmer lantern-light ellipse around the player.
  if self.clock>=20 or self.clock<5:
   self.canvas.create_rectangle(0,0,VW,VH,fill='#11192b',stipple='gray50',outline='')
  elif self.clock>=18 or self.clock<7:
   self.canvas.create_rectangle(0,0,VW,VH,fill='#342e37',stipple='gray75',outline='')

 def draw_hud(self):
  self.panel(13,13,307,86)
  self.draw_text(25,21,'JESSE VALE',15,'#f0d39b',True)
  self.canvas.create_rectangle(25,49,209,66,fill='#3b2222',outline='#91684b')
  self.canvas.create_rectangle(27,51,27+180*max(0,self.hp)/100,64,fill='#a74c40',outline='')
  self.draw_text(218,50,f'{max(0,int(self.hp))} HP',11,'#e7d3b5',True)
  self.draw_text(26,73,f'$ {self.money}    TONICS {self.tonics}    KILLS {self.kills}',10,'#edc995',True)
  self.panel(333,13,285,66)
  self.draw_text(345,21,'COLT PEACEMAKER',11,'#e3c18c',True)
  self.draw_text(345,42,f'{self.ammo} / {self.reserve}',22,'#f2e0bd',True)
  if self.reload_timer>0:self.draw_text(445,46,'RELOADING',12,'#e9a268',True)
  self.panel(631,13,315,86)
  hours=int(self.clock);mins=int((self.clock-hours)*60)
  self.draw_text(642,20,f'{hours%12 or 12}:{mins:02d} {"AM" if hours<12 else "PM"}  |  {self.region_name(self.x,self.y).upper()}',11,'#e2c48f',True)
  stars='★'*min(5,math.ceil(self.wanted))
  self.draw_text(642,43,'WANTED '+(stars if stars else '—'),15,'#e7a16b' if stars else '#b9a78b',True)
  self.draw_text(642,69,'H: HORSE    E: TALK    F1: HELP',10,'#e9d6b2')
  self.panel(13,505,550,83)
  self.draw_text(25,514,'CHAPTER '+ ('EPILOGUE' if self.stage==8 else str(1+self.stage//2))+'  ·  '+MISSIONS[self.stage][0].upper(),12,'#e6bc79',True)
  self.draw_text(25,539,MISSIONS[self.stage][1],12,'#f4e5ce',width=510)
  target=self.quest_target()
  if target:
   dx=target[0]-self.x;dy=target[1]-self.y;distance=int(math.hypot(dx,dy))
   angle=math.atan2(dy,dx)
   self.draw_text(25,566,f'TARGET: {distance} m    DIRECTION: {self.cardinal(angle)}',10,'#bbac89',True)
  else:self.draw_text(25,566,'The frontier is yours now.',10,'#bbac89')
  self.draw_minimap(758,396,187,190)
  for i,(s,t) in enumerate(self.toast[-3:]):
   self.draw_text(480,114+i*23,s,13,'#ffe7a8',True,anchor='center')
  nearest=None;dist=65
  for a in self.actors:
   if a.dead or a.kind.startswith('mission_') or a.kind in ('bandit','deputy','animal'):continue
   q=math.hypot(a.x-self.x,a.y-self.y)
   if q<dist:nearest=a;dist=q
  if nearest and not self.dialog:self.draw_text(480,474,'[ E ]  TALK TO '+nearest.name.upper(),14,'#fff0c4',True,anchor='center')
  if not self.mounted and math.hypot(self.x-self.horse_x,self.y-self.horse_y)<75:self.draw_text(480,448,'[ H ]  MOUNT WHISKEY',13,'#e3d29e',True,anchor='center')

 def region_name(self,x,y):
  if 2800<x<3900 and 1460<y<2220:return 'Sagebrush Crossing'
  if x>3890 and y>2210:return 'Copper Ridge'
  if 1300<x<2400 and y>2160:return 'Silverwater Lake'
  if x>3400 and y<1470:return 'The High Mesa'
  if x>2750 and y>2570:return 'Southern Badlands'
  if x<1350 and y>1780:return 'South Ranchland'
  if x>2750 and y<1470:return 'Red Rock Wilds'
  if x<1200 and y<1000:return 'Cinder Creek'
  if 1580<x<2350 and y<880:return 'Dust Hollow'
  if x>1780 and y<1750:return 'Blackspur Country'
  return 'Open Frontier'

 def cardinal(self,a):return ['E','SE','S','SW','W','NW','N','NE'][round((a%(2*math.pi))/(math.pi/4))%8]
 def draw_minimap(self,x,y,w,h):
  self.panel(x,y,w,h,'#3d3328','#987b54')
  self.draw_text(x+12,y+8,'FRONTIER OVERVIEW',11,'#edd3a5',True)
  sx=(w-20)/WW;sy=(h-37)/WH
  for n,bx,by,bw,bh in BUILDINGS:
   self.canvas.create_rectangle(x+10+bx*sx,y+27+by*sy,x+10+(bx+bw)*sx,y+27+(by+bh)*sy,fill='#a28a62',outline='')
  for a in self.actors:
   if not a.dead and (a.kind=='bandit' or a.kind.startswith('mission_')):
    ax=x+10+a.x*sx;ay=y+27+a.y*sy
    self.canvas.create_oval(ax-2,ay-2,ax+2,ay+2,fill='#d77b56',outline='')
  target=self.quest_target()
  if target:
   tx=x+10+target[0]*sx;ty=y+27+target[1]*sy
   self.canvas.create_oval(tx-5,ty-5,tx+5,ty+5,outline='#f5df91',width=2)
  px=x+10+self.x*sx;py=y+27+self.y*sy
  self.canvas.create_oval(px-4,py-4,px+4,py+4,fill='#f1e8c6',outline='#2d322b')

 def draw_dialog(self):
  if not self.dialog:return
  self.panel(91,397,778,173,'#241d18','#c8a06a')
  name,lines,n=self.dialog
  self.draw_text(113,411,name,17,'#f4ca85',True)
  line=lines[n]
  self.draw_text(113,447,line,16,'#f2e2c9',width=727)
  self.draw_text(837,545,'ENTER / E  ▶',11,'#e2b477',True,anchor='e')

 def draw_map(self):
  self.panel(120,48,720,506,'#26211b')
  self.draw_text(145,66,'TERRITORY MAP',24,'#ebca95',True)
  x,y,w,h=150,110,658,394
  # marker
  self.canvas.create_image(x,y,image=self.mapimg,anchor='nw')
  self.canvas.create_rectangle(x,y,x+w,y+h,outline='#ca9b61',width=3)
  for n,bx,by,bw,bh in BUILDINGS:
   rx=x+(bx/WW)*w;ry=y+(by/WH)*h
   self.canvas.create_rectangle(rx,ry,rx+bw/WW*w,ry+bh/WH*h,fill='#685b43',outline='#362d25')
  for name,tx,ty in [('CINDER CREEK',660,240),('DUST HOLLOW',1840,580),('BLACKSPUR',2020,1120),('RANCH',1490,850),('STATION',1210,1310),('SAGEBRUSH',3330,1560),('SILVERWATER',1530,2850),('COPPER RIDGE',4020,2350),('THE MESA',3880,750),('SOUTH RANCH',660,1900),('GHOST MISSION',2900,2550)]:
   self.draw_text(x+tx/WW*w,y+ty/WH*h,name,9,'#241a14',True)
  target=self.quest_target()
  if target:
   tx=x+target[0]/WW*w;ty=y+target[1]/WH*h
   self.canvas.create_oval(tx-8,ty-8,tx+8,ty+8,outline='#fff2ac',width=3)
  px=x+self.x/WW*w;py=y+self.y/WH*h
  self.canvas.create_oval(px-7,py-7,px+7,py+7,fill='#d94530',outline='#fff8d7',width=2)
  self.draw_text(480,520,'M TO CLOSE  •  RED = YOU  •  GOLD RING = OBJECTIVE  •  4,800 × 3,200' ,11,'#e2c397',anchor='center')

 def draw_journal(self):
  self.panel(132,59,700,485)
  self.draw_text(160,81,'THE OUTLAW JOURNAL',27,'#e8c28b',True)
  self.draw_text(160,144,'CURRENT JOB',12,'#b89c70',True)
  self.draw_text(160,169,MISSIONS[self.stage][0],21,'#f0dcad',True)
  self.draw_text(160,210,MISSIONS[self.stage][1],15,'#e9d7b7',width=630)
  self.canvas.create_line(160,280,801,280,fill='#8d744e',width=2)
  self.draw_text(160,305,'YOUR RECORD',12,'#b89c70',True)
  self.draw_text(160,340,f'Outlaws defeated: {self.kills}       Money: ${self.money}',15,'#f1dfbd')
  self.draw_text(160,382,f'Wanted: {math.ceil(self.wanted)} stars       Times defeated: {self.death_count}',15,'#f1dfbd')
  self.draw_text(160,424,f'Missions finished: {min(4,self.stage//2)} / 4       Story: {"COMPLETE" if self.stage==8 else "IN PROGRESS"}',15,'#f1dfbd')
  self.draw_text(480,516,'J TO CLOSE',12,'#e2bb7e',True,anchor='center')

 def draw_help(self):
  self.panel(190,89,580,418)
  self.draw_text(216,110,'HOW TO SURVIVE THE FRONTIER',20,'#efc58a',True)
  controls=[('WASD / ARROWS','Walk / steer horse'),('SHIFT','Sprint / gallop'),('MOUSE / LEFT CLICK','Aim and shoot'),('SPACE','Fire in facing direction'),('R','Reload revolver'),('E','Talk / collect quest items'),('H','Mount or dismount Whiskey'),('1','Drink a health tonic'),('M / J','Territory map / journal'),('F5','Save game'),('F11','Toggle fullscreen'),('ESC','Pause'),('F1','Close this screen')]
  for i,(k,v) in enumerate(controls):
   yy=156+i*24
   self.draw_text(218,yy,k,12,'#f4d59e',True)
   self.draw_text(440,yy,v,12,'#e3d2b8')

 def draw_title(self):
  self.canvas.create_image(0,0,image=self.titleimg,anchor='nw')
  self.draw_text(480,84,'DUST & DEBT',58,'#f3dbaf',True,anchor='center')
  self.draw_text(480,162,'AN ORIGINAL TOP-DOWN WESTERN ADVENTURE',14,'#f2b777',True,anchor='center')
  self.draw_text(480,280,'ONE HORSE. SIX BULLETS. A TERRITORY FULL OF TROUBLE.',16,'#e5cdaf',True,anchor='center')
  self.panel(308,371,344,151,'#261e19','#d2a369')
  self.draw_text(480,393,'ENTER  /  CLICK  —  NEW GAME',16,'#f6d5a0',True,anchor='center')
  if os.path.exists(SAVE):self.draw_text(480,473,'L  /  CLICK  —  CONTINUE',16,'#f0c28a',True,anchor='center')
  else:self.draw_text(480,473,'NO SAVED GAME YET',13,'#8c806e',anchor='center')
  self.draw_text(480,554,'Built for Linux  •  960×600  •  Python + Tkinter  •  Original artwork',11,'#d6b38e',anchor='center')

 def draw_pause(self):
  self.canvas.create_rectangle(0,0,VW,VH,fill='#17130f',stipple='gray50',outline='')
  self.panel(277,180,406,242)
  self.draw_text(480,215,'PAUSED',38,'#efcf9d',True,anchor='center')
  self.draw_text(480,282,'ESC  —  RESUME',17,'#f0d3a5',True,anchor='center')
  self.draw_text(480,330,'F5  —  SAVE GAME',15,'#e5be86',anchor='center')
  self.draw_text(480,383,'Close window to quit (autosaves).',12,'#d4b995',anchor='center')

 def draw_death(self):
  self.canvas.create_image(0,0,image=self.titleimg,anchor='nw')
  self.canvas.create_rectangle(0,0,VW,VH,fill='#27120f',stipple='gray50',outline='')
  self.draw_text(480,192,'YOU DIED',64,'#e8a17c',True,anchor='center')
  self.draw_text(480,299,'The territory never forgets a debt.',18,'#f1d0ac',anchor='center')
  self.draw_text(480,368,'ENTER — WAKE UP AT THE DOCTOR (LOSE UP TO $25)',15,'#e1b889',True,anchor='center')
  self.draw_text(480,414,'ESC — MAIN MENU',13,'#f4ddbe',anchor='center')

 def draw_ending(self):
  self.canvas.create_image(0,0,image=self.titleimg,anchor='nw')
  self.draw_text(480,92,'THE END',46,'#f1d5ab',True,anchor='center')
  self.draw_text(480,170,'DUST & DEBT',33,'#edbc82',True,anchor='center')
  lines=['Crow fell, but the West kept moving.','Sheriff Bell paid the final $250. The ledger was safe.','Some men ride toward redemption.','Others just ride.']
  for i,line in enumerate(lines):self.draw_text(480,270+i*40,line,17,'#eed8bc',anchor='center')
  self.draw_text(480,500,'STORY COMPLETE  •  ENTER TO CONTINUE FREE ROAM',14,'#f3cd8e',True,anchor='center')

 def render(self):
  self.canvas.delete('all')
  if self.screen=='title':self.draw_title();return
  if self.screen=='death':self.draw_death();return
  if self.screen=='ending':self.draw_ending();return
  self.draw_world();self.draw_hud()
  if self.screen=='paused':self.draw_pause()
  if self.map_open:self.draw_map()
  if self.journal_open:self.draw_journal()
  if self.show_help:self.draw_help()
  self.draw_dialog()

 def quit(self):
  if self.screen in ('playing','paused','ending'):self.save()
  self.root.destroy()


def main():
 if '--self-test' in sys.argv:
  assert len(MISSIONS)==9 and len(BUILDINGS)>=25 and (WW,WH)==(4800,3200)
  assert os.path.exists(os.path.join(ASSETS,'world.png'))
  assert os.path.exists(os.path.join(ASSETS,'title.png'))
  print('Self-test OK: story, buildings, and artwork present.')
  return
 root=tk.Tk()
 Game(root)
 root.mainloop()
if __name__=='__main__':main()
