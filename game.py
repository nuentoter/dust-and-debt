#!/usr/bin/env python3
"""DUST & DEBT — an original, single-player, top-down Western adventure.
Runtime: Python 3 and Tk 8.6 (tkinter), no pip modules required.
"""
import tkinter as tk
from tkinter import messagebox
import os, math, random, json, time, textwrap, sys, shutil
from dataclasses import dataclass

ROOT=os.path.dirname(os.path.abspath(__file__))
ASSETS=os.path.join(ROOT,'assets')
SAVE=os.path.join(os.path.expanduser('~'),'.local','share','dust-and-debt','save.json')
VW,VH=960,600
OLD_WW,OLD_WH=4800,3200
WW,WH=19200,12800  # 16x original area, drawn incrementally
FPS=33
VERSION='2.0 — Complete Frontier'
# Interiors are lightweight procedural rooms: no extra graphics libraries or image files.
INTERIOR_TYPES={
 'Sheriff':'office','Sheriff Annex':'office','Saloon':'saloon','Sagebrush Saloon':'saloon',
 'General Store':'store','Trading Post':'store','Doctor':'doctor','Stable':'stable',
 'Livery':'stable','Hotel':'hotel','Station':'station','Cabin':'home',
 'Fishing Shack':'home','Lake Cabin':'home','Ranch':'home','South Ranch':'home',
 'Assay Office':'store','Bunkhouse':'hotel','Ghost Chapel':'chapel',
 'Old Mission':'chapel','Outpost':'hideout','Smuggler Shed':'hideout',
 'Watchtower':'home','Mesa Camp':'hideout','Copper Mine':'hideout',
 'Riverside Camp':'home'}
SHOP_GOODS={
 'store': [('Revolver rounds (30)',18,'ammo'),('Health tonic',22,'tonic'),('Trail supplies',8,'supplies')],
 'saloon':[('Hot meal (+35 health)',7,'meal'),('Coffee (pass 2 hours)',3,'coffee'),('Health tonic',26,'tonic')],
 'doctor':[('Full treatment',15,'heal'),('Health tonic',20,'tonic')],
 'stable':[('Care for Whiskey',5,'horse'),('Health tonic',24,'tonic')],
 'hotel':[('Rent a room (sleep 8 hours)',10,'sleep'),('Hot meal (+35 health)',9,'meal')],
 'office':[('Pay off your bounty',0,'bounty')],
 'station':[('Travel supplies (30 rounds)',22,'ammo')],
}
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
 ('Riverboat Eli',2490,2700,'civilian'),('Brother Thomas',3000,2860,'civilian'),
 ('Hattie the seamstress',3480,1810,'civilian'),('Will the drover',3680,2020,'civilian'),
 ('Della the cook',3590,1850,'civilian'),('Deputy Rowan',3310,2030,'civilian')]
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
  self.root=root;root.title('DUST & DEBT | Complete Frontier v2.0')
  root.resizable(False,False)
  self.canvas=tk.Canvas(root,width=VW,height=VH,bg='#19140f',highlightthickness=0,cursor='crosshair')
  self.canvas.pack()
  self.world=tk.PhotoImage(file=os.path.join(ASSETS,'world.png'))
  self.titleimg=tk.PhotoImage(file=os.path.join(ASSETS,'title.png'))
  self.mapimg=tk.PhotoImage(file=os.path.join(ASSETS,'map.png'))
  self.mapthumb=self.mapimg.subsample(4,4)
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
  self.honor=50;self.crimes=0;self.law_status='PEACE';self.deadeye=100.;self.deadeye_active=False;self.deadeye_regen_delay=0.;self.witness_timer=0.;self.law_spawn_timer=0.;self.shot_trails=[]
  self.horse_x,self.horse_y=764.,646.;self.horse_hp=100
  self.facing=(0.,-1.);self.shot_timer=0;self.reload_timer=0;self.invuln=0;self.hit_marker=0.;self.combat_warning=0.
  self.actors=[];self.bullets=[];self.effects=[];self.dialog=None;self.choice_dialog=None;self.dialog_from='';self.toast=[]
  self.camx=0;self.camy=0;self.map_open=False;self.journal_open=False;self.show_help=False
  self.waypoint=None;self.sound_on=False;self.last_bell=0.;self.autosave_timer=90.
  self.interior=None;self.indoor_x=480.;self.indoor_y=465.;self.shop_open=False
  self.npc_schedule_tick=0;self.npc_home={}
  for a in self.actors:
   if a.kind=='civilian':self.npc_home[a.name]=(a.x,a.y)
  self.wins=0;self.mission_activated=set();self.ledger=False;self.quest_total=0;self.death_count=0;self.last_region='Cinder Creek'
  for n,x,y,kind in NPCS:
   self.actors.append(Actor(x,y,kind,n,100,100,42))
   if kind=='civilian':self.npc_home[n]=(x,y)
  self.contract=None;self.bounties_done=0;self.encounter_cooldown=35.
  self.spawn_roamers()
  self.update_npc_schedules()
  self.safe_timer=50.
  self.last_save_ok=False;self.save_error='';self.last_save_time=''

 def in_safe_settlement(self,x,y):
  return self.in_town(x,y) or (3120<x<3890 and 1500<y<2230)

 def spawn_roamers(self):
  camps=[(1700,500),(2010,990),(1650,1370),(2100,1480),(2970,1080),(4150,1070),(4300,2000),(3650,2840),(2890,2940),(1820,2290),(6500,4200),(8200,7100),(10800,2550),(13100,9700),(15900,4700),(17900,10900),(6900,10300),(10200,11200)]
  for i in range(42):
   x,y=random.choice(camps);x+=random.randint(-145,145);y+=random.randint(-135,135)
   if self.in_safe_settlement(x,y) or math.hypot(x-698,y-610)<950:continue
   if self.can_move(x,y):self.actors.append(Actor(x,y,'bandit','Drifter',70,70,75))
  for i in range(72):
   x=random.randint(120,WW-150);y=random.randint(100,WH-120)
   if self.in_safe_settlement(x,y):continue
   self.actors.append(Actor(x,y,'animal',random.choice(['Coyote','Jackrabbit']),24,24,85))

 def in_town(self,x,y):return 245<x<1150 and 230<y<960
 def solid(self,x,y,r=11):
  if x<23 or y<23 or x>WW-23 or y>WH-23:return True
  for n,bx,by,bw,bh in BUILDINGS:
   if bx-r<x<bx+bw+r and by-r<y<by+bh+r:return True
  obstacle=self.terrain_obstacle(x,y)
  if obstacle:
   ox,oy,rad=obstacle
   if (x-ox)**2+(y-oy)**2<(rad+r)**2:return True
  return False
 def can_move(self,x,y,r=11):return not self.solid(x,y,r)
 def move_actor(self,a,dx,dy):
  if self.can_move(a.x+dx,a.y,9):a.x+=dx
  if self.can_move(a.x,a.y+dy,9):a.y+=dy

 def notify(self,s,t=3.5):self.toast.append([s,t]);self.toast=self.toast[-5:]
 def say(self,speaker,lines):
  if isinstance(lines,str):lines=[lines]
  self.dialog=[speaker,lines,0]
 def offer_civilian_dialogue(self,a):
  # Choice replies reflect reputation and the current legal situation.
  if self.law_status=='WANTED':
   greeting='Keep your hands where I can see them, stranger.'
  elif self.honor>=75:greeting='Word is you have been helping folks around here.'
  elif self.honor<30:greeting='You have made a name for yourself, and not a good one.'
  else:greeting='Afternoon, traveler. What brings you this way?'
  region=self.region_name(a.x,a.y)
  rumors={
   'Cinder Creek':'They say the sheriff has been looking for help with the Red Mesa riders.',
   'Sagebrush Crossing':'Traders are wary of the roads after sundown.',
   'Copper Ridge':'The mine is still drawing hopeful fools up into the hills.',
  }
  news=rumors.get(region,'Keep an eye on the trails. Riders disappear out here.')
  news=f'{news} I am {self.npc_activity(a)}.'
  law=('There is a price on your head. I would leave town quietly.' if self.law_status=='WANTED' else
       'The law remembers your misdeeds.' if self.honor<30 else
       'Folks trust you. That is worth something out here.' if self.honor>=75 else
       'Keep your gun holstered in town and the deputies will leave you be.')
  self.choice_dialog={'speaker':a.name.upper(),'prompt':greeting,'options':[
   ('Any news?',news),('What do folks think of me?',law),('Goodbye.','Safe travels, stranger.') ]}

 def select_dialogue_option(self,index):
  choice=self.choice_dialog
  if not choice or not 0<=index<len(choice['options']):return
  _label,response=choice['options'][index]
  speaker=choice['speaker'];self.choice_dialog=None
  self.say(speaker,response)

 def near_bounty_board(self):
  if self.mounted or self.interior:return False
  return any(a.kind=='sheriff' and not a.dead and math.hypot(a.x-self.x,a.y-self.y)<105 for a in self.actors)

 def spawn_contract_target(self):
  if not self.contract or self.contract.get('finished'):return
  if any(not a.dead and a.kind=='bounty_target' for a in self.actors):return
  x,y=self.contract['location']
  self.actors.append(Actor(x,y,'bounty_target',self.contract['name'],145,145,86))

 def begin_bounty(self):
  if not self.near_bounty_board():return
  if self.contract:
   x,y=self.contract['location']
   self.notify('Active bounty: '+self.contract['name']+f' at {int(x)}, {int(y)}.',5);return
  jobs=[
   ('Vulture Jack',(1820,600),60),
   ('Rattlesnake Cole',(4210,1120),90),
   ('Maeve Blackwater',(7250,4320),110),
   ('Red Sand Boone',(10400,8000),140),
   ('The Iron Fox',(16200,9500),180)]
  name,location,reward=jobs[self.bounties_done%len(jobs)]
  self.contract={'name':name,'location':list(location),'reward':reward,'finished':False}
  self.spawn_contract_target()
  self.notify('WANTED: '+name+' — $'+str(reward)+' | See J journal.',6)
  self.save()

 def finish_bounty(self,a):
  if not self.contract or a.name!=self.contract['name']:return
  reward=int(self.contract['reward'])
  self.money+=reward;self.bounties_done+=1;self.contract=None
  self.change_honor(2,'Bounty brought to justice')
  self.notify('BOUNTY COMPLETE: +$'+str(reward),5)
  self.sound_cue()
  self.save()

 def spawn_road_encounter(self):
  if any(not a.dead and a.kind=='traveler' for a in self.actors):return False
  if self.in_safe_settlement(self.x,self.y) or self.safe_timer>0:return False
  for _ in range(10):
   angle=random.random()*math.tau;distance=random.randint(270,380)
   x=self.x+math.cos(angle)*distance;y=self.y+math.sin(angle)*distance
   if not self.can_move(x,y,20) or self.in_safe_settlement(x,y):continue
   self.actors.append(Actor(x,y,'traveler','Stranded Traveler',100,100,0))
   self.notify('Someone needs help along the road. Look for a traveler.',4)
   return True
  return False

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
  if key=='q' and self.screen=='playing' and not self.dialog and not self.interior and not self.map_open and not self.journal_open:
   self.deadeye_active=not self.deadeye_active and self.deadeye>0
   self.notify('DEAD EYE '+('ENGAGED' if self.deadeye_active else 'DISENGAGED'),1.0)
   return
  if key=='f5' and self.screen in ('playing','paused'):
   self.save(manual=True);return
  if key=='v' and self.screen in ('playing','paused'):
   self.sound_on=not self.sound_on;self.notify('SOUND '+('ON' if self.sound_on else 'OFF'),2);self.sound_cue();return
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
  if self.choice_dialog:
   if key in ('1','2','3'):self.select_dialogue_option(int(key)-1)
   elif key=='escape':self.choice_dialog=None
   return
  if self.shop_open:
   if key in ('escape','b','e'):self.shop_open=False
   elif key in ('1','2','3','4'):self.buy_item(int(key)-1)
   return
  if self.interior:
   if key=='b' and self.indoor_y<380:self.use_counter()
   elif key=='e':
    if self.indoor_y>475:self.leave_interior()
    elif self.indoor_y<360:self.use_counter()
    else:self.notify('Walk up to the counter or the exit, then press E.')
   elif key=='escape':self.leave_interior()
   elif key=='f5':self.save(manual=True)
   elif key=='f1':self.show_help=not self.show_help
   return
  if key=='escape':self.screen='playing' if self.screen=='paused' else 'paused';self.deadeye_active=False;return
  if self.screen=='paused':return
  if key=='f1':self.show_help=not self.show_help
  elif key=='m':self.map_open=not self.map_open;self.journal_open=False;self.deadeye_active=False
  elif key=='j':self.journal_open=not self.journal_open;self.map_open=False;self.deadeye_active=False
  elif key=='c' and self.waypoint is not None:self.waypoint=None;self.notify('Waypoint cleared.',2)
  elif key=='e':
   if ('shift_l' in self.keys or 'shift_r' in self.keys) and self.near_door():self.enter_interior(self.near_door())
   else:self.interact()
  elif key=='b' and self.near_bounty_board():self.begin_bounty()
  elif key=='h':self.toggle_horse()
  elif key=='r':self.reload()
  elif key=='1':self.tonic()
  elif key=='space':self.fire()
  elif key=='f5':self.save(manual=True)

 def key_up(self,e):self.keys.discard(e.keysym.lower())
 def click(self,e):
  if self.screen=='title':
   if 397<e.y<458:self.new_game()
   elif 467<e.y<515 and os.path.exists(SAVE):self.continue_game()
  elif self.screen=='playing' and self.map_open and not self.interior:
   self.set_waypoint_from_map(e.x,e.y)
  elif self.screen=='playing' and not self.interior and not self.dialog and not self.map_open and not self.journal_open:
   self.mouse_down=True;self.mouse=(e.x,e.y);self.fire()
  elif self.screen in ('death','ending'):self.key_down(type('E',(),{'keysym':'Return'})())
 def new_game(self):self.reset();self.screen='playing';self.say('NARRATOR',['1889. The borderlands have no patience for saints.','Your name is Jesse Vale. You have $35, six rounds, and a horse named Whiskey.','Sheriff Bell is looking for someone with nothing left to lose. Find him at the jail.']);self.save()
 def continue_game(self):
  self.reset()
  try:
   with open(SAVE) as f:s=json.load(f)
   for k in ('x','y','hp','money','ammo','reserve','tonics','stage','kills','wanted','clock','mounted','horse_x','horse_y','ledger','death_count','honor','crimes','deadeye','bounties_done'):
    if k in s:setattr(self,k,s[k])
   self.deadeye=max(0.,min(100.,float(self.deadeye)))
   self.honor=max(0,min(100,int(self.honor)))
   self.law_status='WANTED' if self.wanted>=1.2 else ('INVESTIGATING' if self.wanted>0 else 'PEACE')
   self.mission_activated=set(s.get('mission_activated',[]))
   self.waypoint=s.get('waypoint')
   self.sound_on=bool(s.get('sound_on',False))
   self.contract=s.get('contract')
   if self.contract and not self.contract.get('finished',False):self.spawn_contract_target()
   # Quest combat must regenerate after loading (kill progress is persisted).
   tag={1:'hollow',4:'blackspur',6:'crow'}.get(self.stage)
   if tag:
    self.mission_activated.discard(tag)
    positions={'hollow':[(1780,420),(1840,390),(1888,440),(1840,537),(1778,528)],'blackspur':[(1975,1290),(2080,1280),(2030,1340)],'crow':[(1370,1030),(1430,1100),(1510,1080),(1580,1030)]}[tag]
    self.spawn_mission(tag,positions,{'hollow':95,'blackspur':105,'crow':115}[tag],boss=(1480,1030) if tag=='crow' else None)
    eliminated=int(s.get('stage_kills',0))
    for a in [a for a in self.actors if a.kind=='mission_'+tag][:eliminated]:a.dead=True
   self.update_npc_schedules()
   self.screen='playing';self.safe_timer=18.;self.notify('Loaded last save from disk. F5 saves manually.',4)
  except (OSError,ValueError,TypeError,KeyError) as ex:
   self.new_game();self.notify('Save could not be loaded: '+str(ex),5)
 def save(self,manual=False):
  if self.screen not in ('playing','paused','ending'):return False
  d={k:getattr(self,k) for k in ('x','y','hp','money','ammo','reserve','tonics','stage','kills','wanted','clock','mounted','horse_x','horse_y','ledger','death_count','honor','crimes','deadeye')}
  d['mission_activated']=list(self.mission_activated)
  d['contract']=self.contract;d['bounties_done']=self.bounties_done
  d['waypoint']=self.waypoint;d['sound_on']=self.sound_on
  d['save_version']=VERSION
  tag={1:'hollow',4:'blackspur',6:'crow'}.get(self.stage)
  if tag:d['stage_kills']=sum(a.dead for a in self.actors if a.kind=='mission_'+tag)
  try:
   os.makedirs(os.path.dirname(SAVE),exist_ok=True)
   tmp=SAVE+'.tmp'
   with open(tmp,'w') as f:
    json.dump(d,f);f.flush();os.fsync(f.fileno())
   os.replace(tmp,SAVE)
   self.last_save_ok=True;self.save_error='';self.last_save_time=time.strftime('%H:%M:%S')
   if manual:self.notify('SAVED at '+self.last_save_time+' to '+SAVE,5)
   return True
  except (OSError,TypeError,ValueError) as ex:
   self.last_save_ok=False;self.save_error=str(ex)
   self.notify('SAVE FAILED: '+str(ex),6)
   return False

 def set_waypoint_from_map(self,px,py):
  x,y,w,h=150,110,658,394
  if not (x<=px<=x+w and y<=py<=y+h):return False
  wx=min(WW-25,max(25,int((px-x)/w*WW)))
  wy=min(WH-25,max(25,int((py-y)/h*WH)))
  self.waypoint=[wx,wy]
  self.notify('Waypoint set: '+self.region_name(wx,wy),3)
  return True

 def weather_kind(self):
  cycle=int(self.clock//3)
  region=int(self.x//2400)+int(self.y//1600)
  value=(cycle*7+region*11)%13
  return 'rain' if value in (2,6) else ('dust' if value in (4,8,10) else 'clear')

 def sound_cue(self):
  # Optional low-rate system bell; no extra audio dependencies.
  if not self.sound_on:return
  now=time.monotonic()
  if now-self.last_bell<.35:return
  self.last_bell=now
  try:self.root.bell()
  except tk.TclError:pass

 def quest_target(self):
  return [(418,463),(1840,470),(418,463),(1270,1465),(2040,1280),(1270,1465),(1480,1030),(418,463),None][self.stage]
 def advance_dialog(self):
  if not self.dialog:return
  self.dialog[2]+=1
  if self.dialog[2]>=len(self.dialog[1]):self.dialog=None
 def interact(self):
  nearest=None;best=64
  for a in self.actors:
   if a.dead or a.kind.startswith('mission_') or a.kind in ('bandit','animal','deputy','bounty_target'):continue
   dist=math.hypot(a.x-self.x,a.y-self.y)
   if dist<best:nearest=a;best=dist
  # Original mission givers stand near doors: always give close conversations
  # priority so entering an office cannot block story progression.
  door=self.near_door()
  if door and (nearest is None or best>46):
   self.enter_interior(door);return
  if nearest is None:
   if self.stage==4 and math.hypot(self.x-2040,self.y-1280)<95 and self.enemies_remaining('blackspur')==0:
    self.ledger=True;self.quest(5);self.say('JESSE',['Under a loose floorboard: the stolen manifest.','The pages name Crow as the man who bought the railroad robbery. Nell needs to see this.'])
   else:self.notify('Nobody nearby to talk to. Walk up to a character and press E.',2)
   return
  k=nearest.kind
  if k=='traveler':
   self.actors.remove(nearest);self.money+=12
   self.change_honor(1,'Helped a stranded traveler')
   self.say('TRAVELER',['Thank you for stopping. I thought nobody would come.','Take these twelve dollars. It is all I can spare.'])
   self.encounter_cooldown=65.;self.save();return
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
   elif self.honor<30:self.say('SHERIFF BELL',['I know what you have been doing out there, Vale. Folks remember.','A clean slate is earned, not handed over.'])
   elif self.honor>=75:self.say('SHERIFF BELL',['People are beginning to speak well of you, Jesse.','There is still a place for an honest gun on the frontier.'])
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
  else:self.offer_civilian_dialogue(nearest)

 def near_door(self):
  if self.mounted:return None
  closest=None;dist=58
  for n,bx,by,bw,bh in BUILDINGS:
   if n not in INTERIOR_TYPES:continue
   # Doors are painted on the south face of each building.
   x,y=bx+bw/2,by+bh+19
   d=math.hypot(self.x-x,self.y-y)
   if d<dist:closest=n;dist=d
  return closest

 def enter_interior(self,name):
  self.deadeye_active=False
  self.interior=name;self.indoor_x=480.;self.indoor_y=465.;self.shop_open=False
  self.keys.clear();self.notify('Entered '+name+' — E at counter; E at south door to leave.',4)

 def leave_interior(self):
  if not self.interior:return
  name=self.interior
  self.interior=None;self.shop_open=False;self.keys.clear()
  self.notify('Back outside '+name+'.',1.7)

 def update_indoor(self,dt):
  vx=int('d' in self.keys or 'right' in self.keys)-int('a' in self.keys or 'left' in self.keys)
  vy=int('s' in self.keys or 'down' in self.keys)-int('w' in self.keys or 'up' in self.keys)
  mag=math.hypot(vx,vy)
  if mag:
   self.indoor_x=max(225,min(735,self.indoor_x+vx/mag*165*dt))
   self.indoor_y=max(340,min(510,self.indoor_y+vy/mag*165*dt))
  self.clock=(self.clock+dt*.020)%24

 def use_counter(self):
  kind=INTERIOR_TYPES.get(self.interior,'home')
  if kind in SHOP_GOODS:
   if kind=='office' and self.wanted<=0:
    self.say('DEPUTY',['No warrants out for you. Keep it that way.']);return
   self.shop_open=True;self.keys.clear();return
  talks={'home':'The hearth is cold, but the roof still holds.',
         'chapel':'The frontier holds many sins, and few confessions.',
         'hideout':'Dusty supplies. Looks like the owners left in a hurry.'}
  self.say(self.interior.upper(),talks.get(kind,'Nothing here but frontier dust.'))

 def buy_item(self,index):
  kind=INTERIOR_TYPES.get(self.interior,'home')
  goods=SHOP_GOODS.get(kind,[])
  if index>=len(goods):return
  label,cost,action=goods[index]
  if action=='bounty':cost=int(math.ceil(self.wanted*28))
  if self.money<cost:self.notify('Not enough money for '+label+'.');return
  if action=='heal' and self.hp>=100:self.notify('Already at full health.');return
  if action=='bounty' and self.wanted<=0:self.notify('No bounty to pay.');return
  self.money-=cost
  if action=='bounty':self.change_honor(2,'Settled a debt with the law')
  if action=='ammo':self.reserve+=30
  elif action=='tonic':self.tonics+=1
  elif action=='supplies':self.hp=min(100,self.hp+15)
  elif action=='meal':self.hp=min(100,self.hp+35)
  elif action=='coffee':self.clock=(self.clock+2)%24;self.update_npc_schedules()
  elif action=='heal':self.hp=100
  elif action=='horse':self.horse_hp=100
  elif action=='sleep':self.clock=(self.clock+8)%24;self.hp=min(100,self.hp+25);self.update_npc_schedules()
  elif action=='bounty':self.wanted=0;self.law_timer=0;self.law_status='PEACE';self.witness_timer=0
  self.notify('Purchased '+label+f' for ${cost}.',3)
  self.save()

 def change_honor(self,amount,reason=''):
  before=self.honor
  self.honor=max(0,min(100,self.honor+amount))
  if self.honor!=before and reason:self.notify(('HONOR + ' if amount>0 else 'HONOR - ')+str(abs(self.honor-before))+'  •  '+reason,2.3)

 def report_crime(self,severity,reason):
  # A crime witnessed near town escalates immediately; elsewhere it may take
  # longer to reach the law. Mission firefights against bandits are legal.
  self.crimes+=1
  nearby=any(not a.dead and a.kind in ('civilian','sheriff','store','doctor','station','saloon','stable') and math.hypot(a.x-self.x,a.y-self.y)<310 for a in self.actors)
  witnessed=nearby or self.in_town(self.x,self.y)
  self.wanted=min(5.,self.wanted+severity*(1 if witnessed else .55))
  self.law_timer=max(self.law_timer,5. if witnessed else 2.)
  self.witness_timer=5. if witnessed else 0.
  self.law_status='WANTED' if self.wanted>=1.2 else 'INVESTIGATING'
  if witnessed:self.notify('WITNESSES ALERTED: '+reason,2.0)
  else:self.notify('CRIME REPORTED: '+reason,2.0)

 def update_law(self,dt):
  if self.wanted<=0:
   self.wanted=0.;self.law_status='PEACE';return
  self.law_timer=max(0.,self.law_timer-dt)
  self.witness_timer=max(0.,self.witness_timer-dt)
  if self.law_timer==0:
   rate=.008 if self.in_town(self.x,self.y) else .035
   if not any(a.kind=='deputy' and not a.dead and math.hypot(a.x-self.x,a.y-self.y)<230 for a in self.actors):
    self.wanted=max(0,self.wanted-dt*rate)
  self.law_status='WANTED' if self.wanted>=1.2 else ('INVESTIGATING' if self.wanted>0 else 'PEACE')

 def draw_scattered_props(self):
  # Deterministic lightweight foreground accents; no new graphics dependencies.
  # World base image stays unchanged for v1.2 save/map compatibility.
  cell=104
  left=max(0,int(self.camx//cell)-1);top=max(0,int(self.camy//cell)-1)
  right=min(int(WW//cell),int((self.camx+VW)//cell)+1)
  bottom=min(int(WH//cell),int((self.camy+VH)//cell)+1)
  for gy in range(top,bottom+1):
   for gx in range(left,right+1):
    h=(gx*92821+gy*68917+gx*gy*103)%997
    if h%7>2:continue
    wx=gx*cell+20+h%55;wy=gy*cell+17+(h//7)%53
    if self.in_town(wx,wy) or any(bx-30<wx<bx+bw+30 and by-30<wy<by+bh+30 for _,bx,by,bw,bh in BUILDINGS):continue
    sx,sy=self.pos(wx,wy)
    if h%4==0:  # dry grass
     for o in (-5,0,5):self.canvas.create_line(sx+o,sy+5,sx+o-2,sy-4-(h%5),fill='#997f4c',width=2)
    elif h%4==1: # small stones
     self.canvas.create_oval(sx-6,sy-2,sx+8,sy+5,fill='#8d806b',outline='#635b4b')
    else: # sage scrub
     self.canvas.create_oval(sx-9,sy-6,sx+9,sy+5,fill='#697052',outline='#474f3a')
     self.canvas.create_line(sx-6,sy,sx+7,sy-3,fill='#9b976a',width=2)

 def daily_period(self):
  hour=self.clock%24
  if 6<=hour<11:return 'morning'
  if 11<=hour<17:return 'working'
  if 17<=hour<21:return 'evening'
  return 'night'

 def npc_schedule(self,a):
  # Mission givers remain at their original coordinates, unaffected by schedules.
  home=self.npc_home.get(a.name,(a.x,a.y))
  period=self.daily_period()
  routines={
   'Martha':{'morning':(750,550),'working':(746,655),'evening':(655,570)},
   'Old Pete':{'morning':(557,625),'working':(705,663),'evening':(639,553)},
   'Clay':{'morning':(882,665),'working':(951,662),'evening':(740,643)},
   'Vera':{'morning':(1050,690),'working':(1050,610),'evening':(735,571)},
   'Ruth':{'morning':(366,600),'working':(410,645),'evening':(614,605)},
   'Otis':{'morning':(1095,530),'working':(1080,620),'evening':(745,640)},
   'Hattie the seamstress':{'morning':(3480,1810),'working':(3425,1835),'evening':(3595,1855)},
   'Will the drover':{'morning':(3680,2020),'working':(3740,2080),'evening':(3565,1860)},
   'Della the cook':{'morning':(3590,1850),'working':(3510,1840),'evening':(3615,1850)},
   'Deputy Rowan':{'morning':(3310,2030),'working':(3420,2050),'evening':(3350,2080)},
   'Lakekeeper Ada':{'morning':(1090,2600),'working':(1190,2600),'evening':(1090,2535)},
   'Prospector Finn':{'morning':(4320,2615),'working':(4370,2650),'evening':(4170,2715)},
   'Mina the miner':{'morning':(4480,2590),'working':(4465,2675),'evening':(4230,2720)},
   'Rancher Amos':{'morning':(810,2220),'working':(960,2260),'evening':(845,2300)},
   'Riverboat Eli':{'morning':(2490,2700),'working':(2550,2660),'evening':(2420,2730)},
   'Brother Thomas':{'morning':(3000,2860),'working':(3070,2865),'evening':(2970,2790)}
  }
  target=routines.get(a.name,{}).get(period,home) if period!='night' else home
  return target if self.can_move(*target,9) else home

 def npc_activity(self,a):
  period=self.daily_period()
  if self.law_status=='WANTED':return 'keeping clear of the trouble'
  activities={'morning':'heading out for the day','working':'going about daily work',
              'evening':'visiting neighbors','night':'returning home to rest'}
  specific={'Martha':'selling produce','Old Pete':'watching the street',
            'Clay':'running errands','Vera':'visiting the market',
            'Ruth':'heading to the square','Otis':'collecting supplies',
            'Hattie the seamstress':'mending clothes','Will the drover':'tending the cattle',
            'Della the cook':'preparing supper','Deputy Rowan':'walking the beat',
            'Lakekeeper Ada':'checking the lakeshore','Prospector Finn':'prospecting',
            'Mina the miner':'sorting ore','Rancher Amos':'checking the ranch',
            'Riverboat Eli':'watching the river','Brother Thomas':'tending the chapel'}
  return specific.get(a.name,activities[period]) if period=='working' else activities[period]

 def update_npc_schedules(self):
  for a in self.actors:
   if a.dead or a.kind!='civilian':continue
   a.destination=self.npc_schedule(a)
   a.activity=self.npc_activity(a)

 def draw_interior(self):
  c=self.canvas;kind=INTERIOR_TYPES.get(self.interior,'home')
  colors={'saloon':('#76523b','#b18354'),'store':('#5d6347','#ac885a'),
          'office':('#5c5c60','#8f7862'),'hotel':('#6a4f64','#c29d77'),
          'stable':('#64573f','#aa936a'),'doctor':('#768177','#b9a993'),
          'station':('#585c68','#aa8863'),'chapel':('#555365','#8f765b'),
          'home':('#695747','#967651'),'hideout':('#483c36','#7c6652')}
  wall,floor=colors.get(kind,colors['home'])
  c.create_rectangle(0,0,VW,VH,fill='#1b1716',outline='')
  c.create_rectangle(175,100,785,538,fill=wall,outline='#271c19',width=12)
  c.create_rectangle(192,220,768,520,fill=floor,outline='#d1a978',width=4)
  for xx in range(210,770,38):c.create_line(xx,220,xx,520,fill='#66533f',width=1)
  for yy in range(248,525,34):c.create_line(192,yy,768,yy,fill='#836647',width=1)
  c.create_rectangle(300,242,660,314,fill='#51382e',outline='#e1b77a',width=4)
  for xx in (330,390,450,510,570,630):c.create_oval(xx-6,257,xx+6,268,fill='#b89469',outline='#39291e')
  c.create_rectangle(438,514,522,540,fill='#392a26',outline='#e6ca95',width=4)
  c.create_rectangle(230,360,325,425,fill='#51362f',outline='#cfab7a',width=3)
  c.create_rectangle(640,365,735,435,fill='#51362f',outline='#cfab7a',width=3)
  if kind=='saloon':
   for xx in (280,680):
    c.create_oval(xx-30,365,xx+30,408,fill='#c5a575',outline='#4b3127',width=3)
  elif kind=='hotel':
   for xx in (275,680):c.create_rectangle(xx-38,358,xx+38,436,fill='#b5b09b',outline='#4b3331',width=5)
  elif kind=='stable':
   for xx in (257,675):c.create_oval(xx-25,360,xx+25,420,fill='#795139',outline='#452f22',width=4)
  elif kind=='chapel':
   c.create_line(480,239,480,296,fill='#eed8a7',width=8);c.create_line(458,257,502,257,fill='#eed8a7',width=8)
  self.draw_interior_details(kind)
  c.create_oval(self.indoor_x-10,self.indoor_y+8,self.indoor_x+11,self.indoor_y+15,fill='#49372e',outline='')
  c.create_rectangle(self.indoor_x-9,self.indoor_y-9,self.indoor_x+9,self.indoor_y+10,fill='#35565b',outline='#172a2e',width=2)
  c.create_oval(self.indoor_x-8,self.indoor_y-20,self.indoor_x+8,self.indoor_y-7,fill='#d0a078',outline='')
  c.create_rectangle(self.indoor_x-14,self.indoor_y-20,self.indoor_x+14,self.indoor_y-16,fill='#5f3d2c',outline='')
  self.panel(200,18,560,70)
  self.draw_text(480,30,self.interior.upper(),21,'#f2d7a0',True,anchor='center')
  self.draw_text(480,60,'WASD: WALK   E: INTERACT   ESC: OUTSIDE',11,'#debd86',anchor='center')
  if self.indoor_y<365:self.draw_text(480,330,'[ E ]  COUNTER',14,'#ffe5ac',True,anchor='center')
  if self.indoor_y>475:self.draw_text(480,550,'[ E ]  EXIT TO STREET',13,'#f3d79e',True,anchor='center')
  self.draw_text(18,562,f'HEALTH {int(self.hp)}   $ {self.money}   TONICS {self.tonics}   AMMO {self.ammo}/{self.reserve}',12,'#ecd0a0',True)
  for i,(msg,remaining) in enumerate(self.toast[-2:]):self.draw_text(480,104+i*23,msg,12,'#fff0c4',True,anchor='center')

 def draw_interior_details(self,kind):
  c=self.canvas
  # Distinct dressing stays away from the center walking lane and exit.
  c.create_rectangle(342,345,618,444,fill='#775e46',outline='#c09969',width=2)
  for xx in range(356,618,35):c.create_line(xx,347,xx,441,fill='#96734e')
  if kind=='saloon':
   for xx in (225,706):
    for yy in (268,305,340):
     c.create_rectangle(xx-12,yy-8,xx+12,yy+8,fill='#8f5837',outline='#ceab70')
     c.create_oval(xx-4,yy-4,xx+4,yy+4,fill='#d7b66d',outline='')
   c.create_text(480,358,text='SALOON',fill='#efd4a1',font=(self.font,12,'bold'))
  elif kind in ('store','station'):
   for yy in (272,312):
    for xx in (250,300,665,708):
     c.create_rectangle(xx-15,yy-11,xx+15,yy+11,fill='#c5a16b',outline='#55452f',width=2)
  elif kind=='doctor':
   c.create_rectangle(219,390,306,438,fill='#ded6bd',outline='#655b51',width=3)
   c.create_line(273,263,273,295,fill='#e7ddd0',width=5)
   c.create_line(256,278,290,278,fill='#e7ddd0',width=5)
  elif kind=='office':
   for xx in (256,706):
    c.create_rectangle(xx-23,277,xx+23,310,fill='#584a3c',outline='#c4a477')
    c.create_line(xx,281,xx,303,fill='#d3b888',width=2)
   c.create_text(480,355,text='SHERIFF OFFICE',fill='#e4ceb0',font=(self.font,11,'bold'))
  elif kind in ('home','hotel'):
   c.create_rectangle(220,268,307,326,fill='#c0afa0',outline='#5c483e',width=3)
   c.create_rectangle(227,271,300,286,fill='#e5d9bd',outline='')
  elif kind=='stable':
   for xx in (228,692):c.create_line(xx,250,xx,330,fill='#583e2b',width=8)
  elif kind=='chapel':
   for xx in (245,695):c.create_rectangle(xx-15,356,xx+15,416,fill='#523d35',outline='#b8a27c')
  elif kind=='hideout':
   for xx in (238,698):
    c.create_oval(xx-17,365,xx+17,405,fill='#675c47',outline='#352c29',width=3)

 def draw_shop(self):
  kind=INTERIOR_TYPES.get(self.interior,'home')
  goods=SHOP_GOODS.get(kind,[])
  self.panel(205,128,550,350,'#211d1a','#d4a76a')
  self.draw_text(480,147,'TRADING COUNTER',23,'#ffe0a9',True,anchor='center')
  self.draw_text(232,191,f'YOUR MONEY: ${self.money}',14,'#f0c994',True)
  for i,(name,price,action) in enumerate(goods):
   if action=='bounty':price=int(math.ceil(self.wanted*28))
   self.draw_text(232,239+i*53,f'{i+1}   {name}',15,'#f7e1c2')
   self.draw_text(700,239+i*53,f'${price}',15,'#d6ac76',True,anchor='e')
  self.draw_text(480,445,'PRESS NUMBER TO BUY    •    B / ESC TO CLOSE',12,'#f0d2a6',True,anchor='center')

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
  self.ammo-=1;self.shot_timer=.17 if self.deadeye_active else .25
  mx,my=self.mouse;dx=(mx+self.camx)-self.x;dy=(my+self.camy)-self.y
  if abs(dx)+abs(dy)<15:dx,dy=self.facing
  mag=max(.001,math.hypot(dx,dy));dx/=mag;dy/=mag
  self.facing=(dx,dy)
  self.bullets.append([self.x+dx*19,self.y+dy*19,dx*710,dy*710,1.0,True])
  self.effects.append([self.x+dx*22,self.y+dy*22,.14,'flash'])
  self.sound_cue()
  self.combat_warning=max(self.combat_warning,.16)
  self.shot_trails.append([self.x+dx*18,self.y+dy*18,self.x+dx*210,self.y+dy*210,.13])
  if self.in_town(self.x,self.y):self.report_crime(.40,'Gunshots in town')
  if self.ammo==0:self.notify('Cylinder empty — R to reload.',1.5)

 def respawn(self):
  self.death_count+=1;self.hp=100;self.x,self.y=700,620;self.money=max(0,self.money-25);self.wanted=0
  self.deadeye_active=False;self.deadeye=100.;self.ammo=6;self.reserve=max(24,self.reserve);self.tonics=max(1,self.tonics);self.mounted=False
  self.horse_x,self.horse_y=764,646;self.screen='playing';self.notify('You woke up at the doctor. Lost up to $25.');self.save()

 def loop(self):
  now=time.monotonic();dt=min(.06,now-self.last);self.last=now
  try:
   if self.screen=='playing' and not self.dialog and not self.choice_dialog:
    self.update(dt)
   self.render()
  except Exception as ex:
   import traceback;traceback.print_exc()
   self.screen='paused';self.notify('Unexpected error — see terminal.')
  self.root.after(FPS,self.loop)

 def update(self,dt):
  self.frame+=1;self.clock=(self.clock+dt*.032)%24
  self.safe_timer=max(0.,self.safe_timer-dt)
  self.deadeye_regen_delay=max(0,self.deadeye_regen_delay-dt)
  if self.deadeye_active:
   self.deadeye=max(0.,self.deadeye-dt*25)
   self.deadeye_regen_delay=1.8
   if self.deadeye<=0:self.deadeye_active=False;self.notify('Dead Eye exhausted.',1.5)
  elif self.deadeye_regen_delay<=0:self.deadeye=min(100.,self.deadeye+dt*11)
  world_dt=dt*(.25 if self.deadeye_active else 1.)
  if self.interior:
   self.update_indoor(dt)
   self.autosave_timer-=dt
   if self.autosave_timer<=0:
    self.autosave_timer=90.;self.save()
   for toast in self.toast:toast[1]-=dt
   self.toast=[t for t in self.toast if t[1]>0]
   return
  self.shot_timer=max(0,self.shot_timer-dt);self.invuln=max(0,self.invuln-dt)
  self.hit_marker=max(0,self.hit_marker-dt);self.combat_warning=max(0,self.combat_warning-dt)
  if self.reload_timer>0:
   self.reload_timer-=dt
   if self.reload_timer<=0:
    n=min(6-self.ammo,self.reserve);self.ammo+=n;self.reserve-=n;self.notify('Revolver reloaded.',1.1)
  for toast in self.toast:toast[1]-=dt
  self.toast=[t for t in self.toast if t[1]>0]
  for trail in self.shot_trails:trail[4]-=dt
  self.shot_trails=[v for v in self.shot_trails if v[4]>0]
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
  if self.frame%60==0:self.update_npc_schedules()
  self.encounter_cooldown=max(0.,self.encounter_cooldown-dt)
  if self.encounter_cooldown<=0:
   if self.spawn_road_encounter():self.encounter_cooldown=random.uniform(75,115)
   else:self.encounter_cooldown=15.
  if self.frame%40==0:
   region=self.region_name(self.x,self.y)
   if region!=self.last_region:
    self.last_region=region;self.notify('NOW ENTERING: '+region.upper(),3.4)
  if self.mouse_down:self.fire()
  self.camx=max(0,min(WW-VW,int(self.x-VW/2)));self.camy=max(0,min(WH-VH,int(self.y-VH/2)))
  self.update_law(dt)
  self.update_ai(world_dt)
  self.update_bullets(world_dt)
  if self.stage==1 and self.enemies_remaining('hollow')==0:self.quest(2);self.say('JESSE',['Dust Hollow is quiet. Five more graves for the desert.','Bell promised eighty dollars. Time to collect.'])
  if self.stage==6 and self.enemies_remaining('crow')==0:self.quest(7);self.say('JESSE',['Crow is down. His reign ends here, on a patch of dirt nobody will remember.','Bell deserves to hear it from me.'])
  if self.hp<=0:self.screen='death';self.mounted=False
  self.autosave_timer-=dt
  if self.autosave_timer<=0:
   self.autosave_timer=90.
   self.save()

 def line_of_fire(self,x1,y1,x2,y2):
  # A few collision samples prevent shooting through buildings and future cover.
  distance=math.hypot(x2-x1,y2-y1)
  for i in range(1,max(2,int(distance/20))):
   u=i/max(2,int(distance/20))
   if self.solid(x1+(x2-x1)*u,y1+(y2-y1)*u,2):return False
  return True

 def combat_damage(self,a):
  # Dead Eye shots are more accurate and slightly more damaging.
  return 64 if self.deadeye_active and (a.kind=='bandit' or a.kind.startswith('mission_')) else 52

 def update_ai(self,dt):
  for a in self.actors:
   if a.dead:continue
   if a.kind in ('sheriff','store','doctor','stable','saloon','station','traveler'):continue
   dist=math.hypot(a.x-self.x,a.y-self.y)
   # Dormant distant actors avoid unnecessary pathfinding and collision checks.
   if dist>1200:continue
   a.shoot=max(0,a.shoot-dt);a.wander-=dt
   ishostile=a.kind in ('bandit','deputy','bounty_target') or a.kind.startswith('mission_')
   if a.kind=='civilian':
    if (self.law_status=='WANTED' or (self.witness_timer>0 and dist<310)) and dist<280:dx,dy=a.x-self.x,a.y-self.y
    else:
     dest=getattr(a,'destination',None)
     if dest and math.hypot(dest[0]-a.x,dest[1]-a.y)>8:
      dx,dy=dest[0]-a.x,dest[1]-a.y
     else:
      dx,dy=0.,0.
    mag=max(1,math.hypot(dx,dy));self.move_actor(a,dx/mag*a.speed*dt,dy/mag*a.speed*dt)
   elif a.kind=='animal':
    if dist<130:dx,dy=a.x-self.x,a.y-self.y
    else:
     if a.wander<0:a.wander=random.uniform(1,3);a.dx=random.uniform(-1,1);a.dy=random.uniform(-1,1)
     dx,dy=a.dx,a.dy
    mag=max(1,math.hypot(dx,dy));self.move_actor(a,dx/mag*a.speed*dt,dy/mag*a.speed*dt)
   elif ishostile and dist<(620 if a.kind=='deputy' else 335):
    if a.kind=='bandit' and (self.safe_timer>0 or self.in_safe_settlement(self.x,self.y)):continue
    if a.kind=='deputy' and self.law_status!='WANTED':a.dead=True;continue
    dx=self.x-a.x;dy=self.y-a.y;mag=max(.001,dist)
    # Approach, then strafe while maintaining a shooting distance.
    if dist>205:self.move_actor(a,dx/mag*a.speed*dt,dy/mag*a.speed*dt)
    elif dist<120:self.move_actor(a,-dx/mag*a.speed*dt*.6,-dy/mag*a.speed*dt*.6)
    else:
     direction=1 if (sum(map(ord,a.name))+int(a.x//45))%2 else -1
     self.move_actor(a,-dy/mag*a.speed*dt*.40*direction,dx/mag*a.speed*dt*.40*direction)
    if dist<340 and a.shoot<=0 and self.line_of_fire(a.x,a.y,self.x,self.y):
     a.shoot=random.uniform(1.7,2.9) if a.name!='Crow' else .9
     scatter=random.uniform(-.19,.19)
     angle=math.atan2(dy,dx)+scatter
     self.combat_warning=.7
     self.bullets.append([a.x,a.y,math.cos(angle)*330,math.sin(angle)*330,1.3,False])
  if self.law_status=='WANTED':
   deputies=sum(not a.dead and a.kind=='deputy' for a in self.actors)
   self.law_spawn_timer=max(0.,self.law_spawn_timer-dt)
   if deputies<min(5,1+int(self.wanted)) and self.law_spawn_timer<=0:
    self.law_spawn_timer=max(1.1,4.0-self.wanted*.4)
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
        self.report_crime(2,'Assault on a citizen');self.change_honor(-8,'Assault')
        a.hp-=32
       elif a.kind=='civilian':
        self.report_crime(2,'Assault on a citizen');self.change_honor(-8,'Assault');a.hp-=55
       else:a.hp-=self.combat_damage(a)
       self.effects.append([px,py,.30,'hit']);self.effects.append([px,py,.52,'spark']);self.hit_marker=.20;collided=True
       if a.hp<=0:
        a.dead=True
        if a.kind in ('bandit','deputy','bounty_target') or a.kind.startswith('mission_'):
         if a.kind=='deputy':self.report_crime(2.5,'Lawman killed');self.change_honor(-18,'Killed a lawman')
         elif a.kind=='bounty_target':self.finish_bounty(a)
         else:
          reward=8 if a.kind=='bandit' else 5
          self.money+=reward;self.kills+=1;self.deadeye=min(100.,self.deadeye+12);self.change_honor(1,'Outlaw defeated');self.notify('Outlaw down! +$'+str(reward),1.7)
        elif a.kind in ('civilian','sheriff','store','doctor','stable','saloon','station','traveler'):
         self.report_crime(5,'Murder');self.change_honor(-20,'Killed a civilian');self.wanted=5.;self.notify('MURDER! Wanted level maximum.')
       break
    else:
     if math.hypot(self.x-px,self.y-py)<(17 if self.mounted else 11):
      collided=True
      if self.invuln<=0:
       self.hp-=random.randrange(7,15);self.invuln=.50;self.effects.append([px,py,.35,'hit']);self.effects.append([px,py,.5,'spark'])
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
  villain=a.kind in ('bandit','deputy','bounty_target') or a.kind.startswith('mission_')
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
   if a.kind=='civilian':self.draw_text(sx,sy-56,self.npc_activity(a),9,'#d3c49e',anchor='center')

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

 def terrain_patch(self,tx,ty):
  value=(tx*73856093 ^ ty*19349663 ^ 0xA53B7C19)&0xffffffff
  value=(value^(value>>13))*1274126177&0xffffffff
  return value^(value>>16)

 def is_frontier_road(self,x,y):
  if x<OLD_WW and y<OLD_WH:return False
  return any(abs(x-gx)<38 for gx in range(6000,WW,4200)) or any(abs(y-gy)<39 for gy in range(4300,WH,3600))

 def terrain_obstacle(self,x,y):
  # Consistent cover objects on procedural terrain; roads remain passable.
  if x<OLD_WW and y<OLD_WH:return None
  tile=112;tx=int(x//tile);ty=int(y//tile)
  for cy in range(ty-1,ty+2):
   for cx in range(tx-1,tx+2):
    if cx<0 or cy<0:continue
    h=self.terrain_patch(cx,cy)
    if h%11 not in (0,1):continue
    ox=cx*tile+30+(h//11)%48;oy=cy*tile+30+(h//73)%45
    if self.is_frontier_road(ox,oy):continue
    radius=14 if h%11==0 else 10
    if abs(x-ox)<radius+25 and abs(y-oy)<radius+25:return (ox,oy,radius)
  return None

 def draw_far_terrain(self):
  # Only screen-visible terrain cells are rendered, so RAM stays nearly constant.
  c=self.canvas;c.create_rectangle(0,0,VW,VH,fill='#9d895e',outline='')
  tile=112
  ix0=max(0,int(self.camx//tile)-1);iy0=max(0,int(self.camy//tile)-1)
  ix1=min(int(WW//tile)+1,int((self.camx+VW)//tile)+2)
  iy1=min(int(WH//tile)+1,int((self.camy+VH)//tile)+2)
  for yy in range(iy0,iy1):
   for xx in range(ix0,ix1):
    cx=xx*tile;cy=yy*tile
    if cx+tile<=OLD_WW and cy+tile<=OLD_WH:continue
    h=self.terrain_patch(xx,yy)
    biome=(xx//18+yy//13)%5
    palette=('#ae956b','#b4a275','#8b8c60','#bd996c','#a38c68')
    px=cx-self.camx;py=cy-self.camy
    c.create_rectangle(px,py,px+tile+1,py+tile+1,fill=palette[biome],outline='')
    # Ground layer: ridges, dry grass and sun-baked cracks.
    if h%4==0:
     c.create_line(px+9,py+35,px+40,py+28,px+64,py+39,fill='#8d7657',width=3,smooth=True)
    if h%5==0:
     for gx in (20,27,35):
      c.create_line(px+gx,py+86,px+gx-4,py+75-(h%5),fill='#6b704b',width=2)
    if h%6==0:
     c.create_oval(px+74,py+21,px+93,py+29,fill='#bda479',outline='#8e7554')
    # Prop layer: cover objects match terrain collision.
    if h%11 in (0,1):
     ox=cx+30+(h//11)%48;oy=cy+30+(h//73)%45
     if not self.is_frontier_road(ox,oy):
      rx=ox-self.camx;ry=oy-self.camy
      if h%11==0:
       c.create_polygon(rx-17,ry+12,rx-12,ry-7,rx+1,ry-17,rx+16,ry+8,fill='#746e60',outline='#4d4d45',width=2)
       c.create_polygon(rx-10,ry-4,rx+2,ry-12,rx+8,ry+1,fill='#a39a7c',outline='')
      else:
       c.create_line(rx,ry+10,rx,ry-20,fill='#496549',width=7)
       c.create_line(rx,ry-8,rx-11,ry-8,rx-11,ry-17,fill='#496549',width=5)
       c.create_line(rx,ry-2,rx+12,ry-2,rx+12,ry-12,fill='#496549',width=5)
  # Intersecting tracks provide landmarks and long-distance navigation.
  for gx in range(6000,WW,4200):
   sx=gx-self.camx
   if -70<sx<VW+70:
    c.create_rectangle(sx-17,0,sx+17,VH,fill='#b9a276',outline='')
    c.create_line(sx,0,sx,VH,fill='#d3b789',dash=(12,16),width=2)
  for gy in range(4300,WH,3600):
   sy=gy-self.camy
   if -70<sy<VH+70:
    c.create_rectangle(0,sy-18,VW,sy+18,fill='#b9a276',outline='')
    c.create_line(0,sy,VW,sy,fill='#d3b789',dash=(12,16),width=2)

 def draw_world(self):
  self.draw_far_terrain()
  self.canvas.create_image(-self.camx,-self.camy,image=self.world,anchor='nw')
  self.draw_scattered_props()
  visible=(a for a in self.actors if self.camx-45<=a.x<=self.camx+VW+45 and self.camy-50<=a.y<=self.camy+VH+50)
  for a in sorted(visible,key=lambda a:a.y):self.draw_actor(a)
  if self.stage==4 and self.enemies_remaining('blackspur')==0 and not self.ledger:
   x,y=self.pos(2040,1280)
   self.canvas.create_rectangle(x-9,y-12,x+9,y+12,fill='#e5c283',outline='#423628',width=2)
   self.draw_text(x,y-32,'E: TAKE LEDGER',12,'#fff2b6',True,anchor='center')
  self.draw_player()
  for x1,y1,x2,y2,age in self.shot_trails:
   u,v=self.pos(x1,y1);w,z=self.pos(x2,y2)
   self.canvas.create_line(u,v,w,z,fill='#f5d093' if self.deadeye_active else '#d4ac72',width=2)
  for b in self.bullets:
   bx,by=self.pos(b[0],b[1]);self.canvas.create_oval(bx-3,by-3,bx+3,by+3,fill='#ffe1a4' if b[5] else '#f18f61',outline='')
  for x,y,t,kind in self.effects:
   sx,sy=self.pos(x,y);radius=int(4+t*25)
   col={'dust':'#d2b388','hit':'#b7523b','flash':'#ffe4ac','spark':'#ffe7b0'}.get(kind,'white')
   self.canvas.create_oval(sx-radius,sy-radius,sx+radius,sy+radius,outline=col,width=3)
  if self.hit_marker>0:
   mx,my=self.mouse
   for ox,oy in ((-10,-10),(10,10),(-10,10),(10,-10)):
    self.canvas.create_line(mx+ox*.45,my+oy*.45,mx+ox,my+oy,fill='#fff0bb',width=3)
  if self.combat_warning>0:
   self.canvas.create_rectangle(3,3,VW-3,VH-3,outline='#a44e3c',width=2)
  if self.deadeye_active:
   self.canvas.create_rectangle(0,0,VW,VH,fill='#ad7f39',stipple='gray75',outline='')
   self.canvas.create_oval(self.mouse[0]-18,self.mouse[1]-18,self.mouse[0]+18,self.mouse[1]+18,outline='#f7e5a8',width=3)
   sx,sy=self.pos(self.x,self.y)
   self.canvas.create_line(sx,sy,self.mouse[0],self.mouse[1],fill='#ebcd83',dash=(5,9),width=2)
  # Nightfall through stippled dark field, with a warmer lantern-light ellipse around the player.
  self.draw_weather()
  if self.clock>=20 or self.clock<5:
   self.canvas.create_rectangle(0,0,VW,VH,fill='#11192b',stipple='gray50',outline='')
  elif self.clock>=18 or self.clock<7:
   self.canvas.create_rectangle(0,0,VW,VH,fill='#342e37',stipple='gray75',outline='')

 def draw_weather(self):
  kind=self.weather_kind()
  if kind=='clear':return
  c=self.canvas
  for index in range(30 if kind=='rain' else 22):
   seed=(index*1931+71)%10007
   px=(seed*37+self.frame*(7 if kind=='rain' else 2))%VW
   py=(seed*59+self.frame*(13 if kind=='rain' else 1))%VH
   if kind=='rain':c.create_line(px,py,px-5,py+13,fill='#9db1b2',width=1)
   else:c.create_oval(px-2,py-1,px+3,py+2,fill='#c4aa7c',outline='')
  if kind=='dust':c.create_rectangle(0,0,VW,VH,fill='#aa814e',stipple='gray75',outline='')

 def draw_hud(self):
  self.panel(13,13,307,86)
  self.draw_text(25,21,'JESSE VALE',15,'#f0d39b',True)
  self.canvas.create_rectangle(25,49,209,66,fill='#3b2222',outline='#91684b')
  self.canvas.create_rectangle(27,51,27+180*max(0,self.hp)/100,64,fill='#a74c40',outline='')
  self.draw_text(218,50,f'{max(0,int(self.hp))} HP',11,'#e7d3b5',True)
  self.draw_text(26,73,f'$ {self.money}   HONOR {self.honor}   TONICS {self.tonics}',10,'#edc995',True)
  self.panel(333,13,285,86)
  self.draw_text(345,21,'COLT PEACEMAKER',11,'#e3c18c',True)
  self.draw_text(345,42,f'{self.ammo} / {self.reserve}',22,'#f2e0bd',True)
  if self.reload_timer>0:self.draw_text(445,46,'RELOADING',12,'#e9a268',True)
  self.canvas.create_rectangle(346,75,596,83,fill='#4d3827',outline='#8b7550')
  self.canvas.create_rectangle(347,76,347+248*self.deadeye/100,82,fill='#e3c078',outline='')
  self.draw_text(505,60,'Q: DEAD EYE' if not self.deadeye_active else 'DEAD EYE ACTIVE',10,'#e9d5a4',True)
  self.panel(631,13,315,86)
  hours=int(self.clock);mins=int((self.clock-hours)*60)
  self.draw_text(642,20,f'{hours%12 or 12}:{mins:02d} {"AM" if hours<12 else "PM"}  |  {self.region_name(self.x,self.y).upper()}',11,'#e2c48f',True)
  stars='★'*min(5,math.ceil(self.wanted))
  self.draw_text(642,43,self.law_status+' '+(stars if stars else '—'),15,'#e7a16b' if stars else '#b9a78b',True)
  self.draw_text(642,69,'H: HORSE   F5: SAVE   V: SOUND',10,'#e9d6b2')
  self.draw_text(642,84,'WEATHER: '+self.weather_kind().upper(),9,'#ead9b1')
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
  if self.waypoint:
   dx=self.waypoint[0]-self.x;dy=self.waypoint[1]-self.y
   self.draw_text(572,558,f'PIN {int(math.hypot(dx,dy))} m / {self.cardinal(math.atan2(dy,dx))}',11,'#f6d68d',True)
  for i,(s,t) in enumerate(self.toast[-3:]):
   self.draw_text(480,114+i*23,s,13,'#ffe7a8',True,anchor='center')
  nearest=None;dist=65
  for a in self.actors:
   if a.dead or a.kind.startswith('mission_') or a.kind in ('bandit','deputy','animal','bounty_target'):continue
   q=math.hypot(a.x-self.x,a.y-self.y)
   if q<dist:nearest=a;dist=q
  if nearest and not self.dialog and not self.choice_dialog:self.draw_text(480,474,'[ E ]  TALK TO '+nearest.name.upper(),14,'#fff0c4',True,anchor='center')
  if self.near_bounty_board():self.draw_text(480,427,'[ B ]  ACCEPT BOUNTY CONTRACT',12,'#f0d28a',True,anchor='center')
  door=self.near_door()
  if door:self.draw_text(480,451,'[ SHIFT+E ] ENTER '+door.upper(),14,'#ffebb7',True,anchor='center')
  if not self.mounted and math.hypot(self.x-self.horse_x,self.y-self.horse_y)<75:self.draw_text(480,448,'[ H ]  MOUNT WHISKEY',13,'#e3d29e',True,anchor='center')

 def region_name(self,x,y):
  if x>=OLD_WW or y>=OLD_WH:
   row=min(3,int(y//3200));col=min(3,int(x//4800))
   return (('Far Rim','Prairie Expanse','Broken Plateaus','The Long Divide'),('Distant Range','Drybone Basin','Outlaw Trail','Sunset Mesa'),('Sage Ocean','Wandering Plains','Salt Flats','The Iron Hills'),('Southwood','Big Sky Prairie','Red Canyons','Last Horizon'))[row][col]
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
  if self.waypoint:
   wx=x+10+self.waypoint[0]*sx;wy=y+27+self.waypoint[1]*sy
   self.canvas.create_line(wx-5,wy,wx+5,wy,fill='#8ce0c4',width=2)
   self.canvas.create_line(wx,wy-5,wx,wy+5,fill='#8ce0c4',width=2)
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

 def draw_choice_dialogue(self):
  if not self.choice_dialog:return
  data=self.choice_dialog
  self.panel(91,345,778,225,'#241d18','#c8a06a')
  self.draw_text(113,358,data['speaker'],17,'#f4ca85',True)
  self.draw_text(113,388,data['prompt'],15,'#f2e2c9',width=725)
  for i,(label,_reply) in enumerate(data['options']):
   self.draw_text(118,429+i*33,f'{i+1}. {label}',14,'#e8c38b',True)
  self.draw_text(838,548,'1–3 CHOOSE  •  ESC LEAVE',10,'#e2b477',True,anchor='e')

 def draw_map(self):
  self.panel(120,48,720,506,'#26211b')
  self.draw_text(145,66,'TERRITORY MAP',24,'#ebca95',True)
  x,y,w,h=150,110,658,394
  # marker
  self.canvas.create_rectangle(x,y,x+w,y+h,fill='#ac946e',outline='')
  for row in range(4):
   for col in range(4):
    x1=x+col*w/4;y1=y+row*h/4
    self.canvas.create_rectangle(x1,y1,x1+w/4,y1+h/4,fill=('#bba079' if (row+col)%2 else '#a58e68'),outline='#907a60')
  self.canvas.create_image(x,y,image=self.mapthumb,anchor='nw')
  for row in range(4):
   for col in range(4):
    if row==0 and col==0:continue
    cx=x+(col+.5)*w/4;cy=y+(row+.5)*h/4
    label=self.region_name((col+.5)*4800,(row+.5)*3200)
    self.draw_text(cx,cy,label.upper(),8,'#55422d',True,anchor='center')
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
  if self.contract:
   bx=x+self.contract['location'][0]/WW*w;by=y+self.contract['location'][1]/WH*h
   self.canvas.create_oval(bx-6,by-6,bx+6,by+6,fill='#9d3d34',outline='#2d211e',width=2)
  if self.waypoint:
   wx=x+self.waypoint[0]/WW*w;wy=y+self.waypoint[1]/WH*h
   self.canvas.create_line(wx-9,wy,wx+9,wy,fill='#157661',width=3)
   self.canvas.create_line(wx,wy-9,wx,wy+9,fill='#157661',width=3)
  px=x+self.x/WW*w;py=y+self.y/WH*h
  self.canvas.create_oval(px-7,py-7,px+7,py+7,fill='#d94530',outline='#fff8d7',width=2)
  self.draw_text(480,520,'CLICK: PIN  •  C: CLEAR  •  GOLD: QUEST  •  MAROON: BOUNTY',11,'#e2c397',anchor='center')

 def draw_journal(self):
  self.panel(132,59,700,485)
  self.draw_text(160,81,'THE OUTLAW JOURNAL',27,'#e8c28b',True)
  self.draw_text(160,144,'CURRENT JOB',12,'#b89c70',True)
  self.draw_text(160,169,MISSIONS[self.stage][0],21,'#f0dcad',True)
  self.draw_text(160,210,MISSIONS[self.stage][1],15,'#e9d7b7',width=630)
  self.canvas.create_line(160,280,801,280,fill='#8d744e',width=2)
  self.draw_text(160,305,'YOUR RECORD',12,'#b89c70',True)
  self.draw_text(160,340,f'Outlaws defeated: {self.kills}       Money: ${self.money}',15,'#f1dfbd')
  self.draw_text(160,382,f'Honor: {self.honor}/100    Law: {self.law_status}    Crimes: {self.crimes}',15,'#f1dfbd')
  self.draw_text(160,424,f'Missions finished: {min(4,self.stage//2)} / 4       Story: {"COMPLETE" if self.stage==8 else "IN PROGRESS"}',15,'#f1dfbd')
  self.draw_text(160,465,('ACTIVE BOUNTY: '+self.contract['name']+' — $'+str(self.contract['reward']) if self.contract else 'Bounties completed: '+str(self.bounties_done)+' — Press B near sheriff'),12,'#f0ce92',True)
  self.draw_text(480,516,'J TO CLOSE',12,'#e2bb7e',True,anchor='center')

 def draw_help(self):
  self.panel(190,52,580,506)
  self.draw_text(216,110,'HOW TO SURVIVE THE FRONTIER',20,'#efc58a',True)
  controls=[('WASD / ARROWS','Walk / steer horse'),('SHIFT','Sprint / gallop'),('MOUSE / LEFT CLICK','Aim and shoot'),('SPACE','Fire in facing direction'),('R','Reload revolver'),('Q','Toggle Dead Eye (slow-motion)'),('E / SHIFT+E','Talk / enter buildings / interact'),('H','Mount or dismount Whiskey'),('1','Drink a health tonic'),('M / J','Territory map / journal'),('B','Shop / accept bounty near sheriff'),('V','Toggle sound (off by default)'),('F5','Save game'),('F11','Toggle fullscreen'),('ESC','Pause'),('F1','Close this screen')]
  for i,(k,v) in enumerate(controls):
   yy=143+i*24
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
  self.draw_text(480,554,VERSION+'  •  Linux  •  Python + Tkinter',11,'#d6b38e',anchor='center')

 def draw_pause(self):
  self.canvas.create_rectangle(0,0,VW,VH,fill='#17130f',stipple='gray50',outline='')
  self.panel(277,180,406,242)
  self.draw_text(480,215,'PAUSED',38,'#efcf9d',True,anchor='center')
  self.draw_text(480,282,'ESC  —  RESUME',17,'#f0d3a5',True,anchor='center')
  self.draw_text(480,330,'F5  —  SAVE GAME',15,'#e5be86',anchor='center')
  self.draw_text(480,366,'LAST SAVE: '+(self.last_save_time if self.last_save_ok else ('FAILED' if self.save_error else 'NOT YET')),12,'#e8d2ab',anchor='center')
  self.draw_text(480,390,'Close window to quit (autosaves).',11,'#d4b995',anchor='center')

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
  if self.interior:
   self.draw_interior()
   if self.shop_open:self.draw_shop()
   if self.show_help:self.draw_help()
   self.draw_dialog()
   self.draw_choice_dialogue()
   return
  self.draw_world();self.draw_hud()
  if self.screen=='paused':self.draw_pause()
  if self.map_open:self.draw_map()
  if self.journal_open:self.draw_journal()
  if self.show_help:self.draw_help()
  self.draw_dialog()
  self.draw_choice_dialogue()

 def quit(self):
  if self.screen in ('playing','paused','ending'):self.save()
  self.root.destroy()


def main():
 if '--self-test' in sys.argv:
  assert len(MISSIONS)==9 and len(BUILDINGS)>=25 and (WW,WH)==(19200,12800)
  assert all(t in INTERIOR_TYPES for t in ('Saloon','General Store','Hotel','Sheriff'))
  assert len(SHOP_GOODS)>=6
  assert VERSION.startswith('2.0')
  assert os.path.exists(os.path.join(ASSETS,'world.png'))
  assert os.path.exists(os.path.join(ASSETS,'title.png'))
  print('Self-test OK: story, buildings, and artwork present.')
  return
 root=tk.Tk()
 Game(root)
 root.mainloop()
if __name__=='__main__':main()
