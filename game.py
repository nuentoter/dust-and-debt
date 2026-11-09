#!/usr/bin/env python3
"""DUST & DEBT — an original, single-player, top-down Western adventure.
Runtime: Python 3 and Tk 8.6 (tkinter), no pip modules required.
"""
import tkinter as tk
from tkinter import messagebox
import os, math, random, json, time, textwrap, sys, shutil
from dataclasses import dataclass
from working_frontier import work_offer, shop_prices, daily_stock
from audio_system import AudioDirector
from natural_terrain import draw_ground,draw_landforms,landform_solid,hash32,noise
from combat_progression import WEAPONS, DIFFICULTIES, available_weapons, normal_weapon, normal_difficulty, incoming_damage, aim_vector
from horse_riding import step_motion, TROT_SPEED, GALLOP_SPEED
from frontier_chapters import CHAPTERS,CHAPTER_BY_ID,node_for,available_chapter
import deadwood_pulp as pulp
from road_events import (EVENT_TYPES,EVENT_TITLES,offer_for_day,nearby_station,
                        dispatch_rumor,safe_event_position,nearest_landmark)
from frontier_world import (WORLD_WIDTH,WORLD_HEIGHT,SECTOR_W,SECTOR_H,SECTOR_NAMES,
 BIOME_PALETTES,BIOME_GRID,LANDMARKS,ROAD_X,ROAD_Y,START_SPUR,MAP_RECT,
 region_at,biome_at,near_landmark,landmark_by_key,road_at,map_view,
 point_on_map,world_from_map,draw_map_background,draw_landmark,
 WAYSTATIONS,near_waystation,waystation_by_key,draw_waystations)
from new_austellia import (TOWNS,MAJOR_TOWNS,near_atlas_town,is_water,
                            draw_local_geography,draw_starting_transition,coastal_water,region_at as austellia_region)
from frontier_expansion import (SETTLEMENTS,SIDE_JOBS,extra_buildings,extra_npcs,resource_nodes,
                                nearby_settlement,get_settlement,get_job,draw_frontier_towns)

ROOT=os.path.dirname(os.path.abspath(__file__))
ASSETS=os.path.join(ROOT,'assets')
SAVE=os.path.join(os.path.expanduser('~'),'.local','share','dust-and-debt','save.json')
VW,VH=960,600
OLD_WW,OLD_WH=4800,3200
WW,WH=WORLD_WIDTH,WORLD_HEIGHT  # Exactly 10x v2.5 world area; camera-local terrain
FPS=33
VERSION='2.8-dev — Combat & Character Progression'
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

# Expansion definitions leave every original mission and old-town coordinate intact.
for _name,_x,_y,_w,_h,_kind in extra_buildings():
 BUILDINGS.append((_name,_x,_y,_w,_h))
 INTERIOR_TYPES[_name]=_kind
NPCS.extend(extra_npcs())
RESOURCE_NODES=resource_nodes()
MAP_DESTINATIONS=(('cinder_creek','Cinder Creek',660,600),)+tuple(
 (key,name,x,y) for key,name,x,y,kind in TOWNS
 if kind in ('city','town','port','settlement','post','fort','ranch','mine'))

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
  self.root=root;root.title('DUST & DEBT | Combat Progression v2.8')
  root.resizable(False,False)
  self.canvas=tk.Canvas(root,width=VW,height=VH,bg='#19140f',highlightthickness=0,cursor='crosshair')
  self.canvas.pack()
  self.world=tk.PhotoImage(file=os.path.join(ASSETS,'world.png'))
  self.titleimg=tk.PhotoImage(file=os.path.join(ASSETS,'title.png'))
  self.mapimg=tk.PhotoImage(file=os.path.join(ASSETS,'map.png'))
  self.mapthumb=self.mapimg.subsample(4,4)
  # Optional authentic illustrated atlas. Vector atlas still works without it.
  self.austellia_image=None
  try:
   source=os.path.join(ASSETS,'new_austellia_map.png')
   if os.path.isfile(source):
    atlas=tk.PhotoImage(file=source)
    if (atlas.width(),atlas.height())==MAP_RECT[2:]:self.austellia_image=atlas
  except (OSError,tk.TclError):pass
  self.audio=AudioDirector(bell=root.bell,assets_path=os.path.join(ASSETS,'audio'))
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
  self.audio.stop()
  self.x,self.y=698.,610.;self.hp=100.;self.maxhp=100;self.money=35;self.ammo=6;self.reserve=42;self.tonics=2
  self.stage=0;self.kills=0;self.wanted=0.;self.law_timer=0.;self.clock=8.0;self.mounted=False
  self.honor=50;self.crimes=0;self.law_status='PEACE';self.deadeye=100.;self.deadeye_active=False;self.deadeye_regen_delay=0.;self.witness_timer=0.;self.law_spawn_timer=0.;self.shot_trails=[]
  self.horse_x,self.horse_y=764.,646.;self.horse_hp=100
  self.horse_motion={'stamina':100.,'speed':0.,'heading_x':0.,'heading_y':-1.,'exhausted':False}
  self.facing=(0.,-1.);self.shot_timer=0;self.reload_timer=0;self.invuln=0;self.hit_marker=0.;self.combat_warning=0.
  self.weapon='peacemaker';self.difficulty='standard';self.aim_assist=False
  self.actors=[];self.bullets=[];self.effects=[];self.dialog=None;self.choice_dialog=None;self.dialog_from='';self.toast=[]
  self.camx=0;self.camy=0;self.map_open=False;self.journal_open=False;self.show_help=False
  self.map_zoom=False;self.map_center=[self.x,self.y];self.landmarks_found=[];self.map_destination_index=0
  self.waypoint=None;self.sound_on=False;self.audio.enabled=False;self.audio.music_enabled=False;self.audio.set_music_state('silence');self.last_bell=0.;self.autosave_timer=90.;self.loaded_backup=False
  self.economy_day=0;self.shop_stock={};self.work_active=None;self.work_records={};self.work_finished=0;self.work_income=0;self.work_expenses=0;self.store_id=None;self.work_ledger_open=False
  self.interior=None;self.indoor_x=480.;self.indoor_y=465.;self.shop_open=False;self.show_jail=False
  self.npc_schedule_tick=0;self.npc_home={}
  for a in self.actors:
   if a.kind=='civilian':self.npc_home[a.name]=(a.x,a.y)
  self.wins=0;self.mission_activated=set();self.ledger=False;self.quest_total=0;self.death_count=0;self.last_region='Cinder Creek'
  for n,x,y,kind in NPCS:
   self.actors.append(Actor(x,y,kind,n,100,100,42))
   if kind=='civilian':self.npc_home[n]=(x,y)
  self.contract=None;self.bounties_done=0;self.encounter_cooldown=35.
  self.lasso_cooldown=0.;self.lasso_visual=None
  self.field_prisoner=None;self.field_arrests=0
  self.jail_roster=[];self.law_reputation=0;self.patrol_alert_timer=0.
  self.side_job=None;self.side_completed=[];self.gathered_nodes=[];self.camps_used=[]
  self.chapter_active=None;self.chapter_completed=[];self.chapter_earnings=0
  self.visited_settlements=[];self.settlement_news_timer=0.
  self.road_contract=None;self.road_contracts_done=0;self.road_income=0
  self.road_offer_day={};self.regional_standing={};self.road_event_cooldown=65.
  self.spawn_roamers()
  self.spawn_outer_frontier()
  self.spawn_law_patrols()
  self.update_npc_schedules()
  self.safe_timer=50.
  self.last_save_ok=False;self.save_error='';self.last_save_time=''

 def in_safe_settlement(self,x,y):
  return (self.in_town(x,y) or (3120<x<3890 and 1500<y<2230) or
          nearby_settlement(x,y,445) is not None or near_waystation(x,y,275) is not None
          or near_atlas_town(x,y,310) is not None)

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

 def spawn_outer_frontier(self):
  # Lightweight standing agents and outer-sector threats make remote regions live.
  for key,name,x,y in WAYSTATIONS:
   pos=safe_event_position(x+77,y+62,self.can_move)
   if pos:self.actors.append(Actor(*pos,'station_agent',name+' Dispatcher',100,100,0))
  for row in range(4):
   for col in range(6):
    if row==0 and col<2:continue
    center_x=col*SECTOR_W+SECTOR_W//2
    center_y=row*SECTOR_H+SECTOR_H//2
    for n in range(2):
     ox=(n*913+row*307+col*1103)%2300-1150
     oy=(n*431+row*797+col*601)%2000-1000
     point=safe_event_position(center_x+ox,center_y+oy,self.can_move)
     if not point or self.in_safe_settlement(*point):continue
     self.actors.append(Actor(*point,'bandit','Roadside Outlaw',80,80,78))

 def spawn_law_patrols(self):
  # Permanent, non-hostile lawmen circle town edges. Only pursue when wanted.
  routes=[
   ((1180,700),(1260,720),(1300,830),(1180,900)),
   ((3250,1640),(3860,1660),(3910,2230),(3220,2200)),
   ((6000,3890),(6380,4260),(6000,4680),(5620,4300)),
   ((10200,3880),(10560,4300),(10200,4660),(9840,4300)),
   ((14400,3910),(14790,4320),(14400,4680),(14020,4320)),
   ((6000,7500),(6400,7910),(6000,8300),(5600,7910)),
   ((10200,7510),(10610,7920),(10200,8290),(9790,7900)),
   ((14400,7500),(14810,7900),(14400,8300),(13990,7900)),
  ]
  for i,route in enumerate(routes):
   x,y=self.safe_enemy_spawn(*route[0])
   a=Actor(x,y,'law_patrol','Deputy Patrol '+str(i+1),95,95,63)
   a.route=tuple(self.safe_enemy_spawn(*pt) for pt in route)
   a.route_index=1
   self.actors.append(a)

 def in_town(self,x,y):return 245<x<1150 and 230<y<960
 def solid(self,x,y,r=11):
  if x<23 or y<23 or x>WW-23 or y>WH-23:return True
  if is_water(x,y):return True
  if landform_solid(x,y,r):return True
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
  local_standing=self.regional_standing.get(region_at(a.x,a.y),0)
  if self.law_status=='WANTED':
   greeting='Keep your hands where I can see them, stranger.'
  elif local_standing>=9:greeting='You have helped travelers all over this district. Folks remember.'
  elif local_standing<=-9:greeting='Word of your crimes has reached this town. Keep your distance.'
  elif self.law_reputation>=12:greeting='The deputies say you have brought real outlaws to justice.'
  elif self.honor>=75:greeting='Word is you have been helping folks around here.'
  elif self.honor<30:greeting='You have made a name for yourself, and not a good one.'
  else:greeting='Afternoon, traveler. What brings you this way?'
  region=self.region_name(a.x,a.y)
  rumors={
   'Drybone Junction':'The mail riders lost their bags in the northern ravines.',
   'Ironwell':'The closed shaft still holds rare ore below the old road.',
   'Painted Mesa':'Scouts have been leaving painted trail marks to the east.',
   'Saltwater Crossing':'The ferry brought trouble, and a medicine crate went missing.',
   'Ember Gulch':'A smuggler left two ledgers, but neither names the same man.',
   'Sundown Station':'The telegraph is silent, even on the clearest nights.',
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

 def advance_clock(self,hours):
  previous=self.clock
  self.clock=(self.clock+hours)%24
  if hours>=0:self.economy_day+=int((previous+hours)//24)

 def active_shop(self):
  kind=INTERIOR_TYPES.get(self.interior,'home')
  return (self.interior,kind,SHOP_GOODS.get(kind,[]))

 def shop_inventory(self):
  name,kind,goods=self.active_shop()
  if not name or not goods:return []
  current=self.shop_stock.get(name)
  if not current or current.get('day')!=self.economy_day or len(current.get('remaining',[]))!=len(goods):
   current={'day':self.economy_day,'remaining':daily_stock(kind,goods)}
   self.shop_stock[name]=current
  return current['remaining']

 def shop_cost(self,index):
  name,kind,goods=self.active_shop()
  if index<0 or index>=len(goods):return None
  if goods[index][2]=='bounty':return int(math.ceil(self.wanted*28))
  town=nearby_settlement(self.x,self.y,600) or ''
  return shop_prices(kind,goods,self.honor,town)[index]

 def work_provider(self):
  nearest=None;best=95.
  for actor in self.actors:
   if actor.dead:continue
   offer=work_offer(actor.name,actor.x,actor.y,SETTLEMENTS)
   if not offer:continue
   d=math.hypot(self.x-actor.x,self.y-actor.y)
   if d<best:nearest=actor;best=d
  return nearest

 def offer_work(self):
  if self.mounted or self.interior or self.dialog or self.choice_dialog:return False
  giver=self.work_provider()
  if not giver:
   self.notify('Work is available from station agents, miners, ranchers and town workers.',4)
   return False
  if self.work_active:
   task=self.work_active
   if task['giver']==giver.name and task['status']=='return':
    amount=int(task['reward'])
    self.money+=amount;self.work_income+=amount;self.work_finished+=1
    self.work_records[giver.name]=self.economy_day
    self.change_honor(1,'Honest work')
    self.work_active=None;self.waypoint=None
    self.notify('WORK FINISHED: +$'+str(amount)+' • '+giver.name,5)
    self.audio.cue('job_complete');self.save()
    return True
   self.notify('Finish the current job: '+task['title']+'.',4);return False
  if self.work_records.get(giver.name)==self.economy_day:
   self.notify('This employer has no more work today. Try another or return tomorrow.',4)
   return False
  offer=work_offer(giver.name,giver.x,giver.y,SETTLEMENTS)
  if not offer:return False
  kind,title,destination,reward=offer
  destination=self.safe_enemy_spawn(*destination)
  self.work_active={'giver':giver.name,'giver_pos':[giver.x,giver.y],
                    'kind':kind,'title':title,'destination':list(destination),
                    'reward':reward,'status':'outbound'}
  self.waypoint=list(destination)
  self.notify('WORK ACCEPTED: '+title+' • $'+str(reward)+' upon return.',5)
  self.audio.cue('job_accept');self.save();return True

 def complete_work_step(self):
  job=self.work_active
  if not job or job.get('status')!='outbound' or self.mounted:return False
  tx,ty=job['destination']
  if math.hypot(self.x-tx,self.y-ty)>90:return False
  job['status']='return'
  self.waypoint=list(job['giver_pos'])
  self.notify('WORK DONE: Return to '+job['giver']+' and press P for pay.',5)
  self.audio.cue('job_complete');self.save();return True

 def near_bounty_board(self):
  if self.mounted or self.interior:return False
  return any(a.kind=='sheriff' and not a.dead and math.hypot(a.x-self.x,a.y-self.y)<105 for a in self.actors)

 def record_jail_intake(self,name,offense):
  self.jail_roster.append({'name':name,'case':offense,'hour':round(self.clock,2),
                           'town':'Cinder Creek'})
  self.jail_roster=self.jail_roster[-40:]
  self.law_reputation=min(100,self.law_reputation+(5 if offense=='named bounty' else 2))

 def field_actor(self):
  return next((a for a in self.actors if a.kind=='field_prisoner' and not a.dead),None)

 def field_status(self):
  return self.field_prisoner.get('status') if self.field_prisoner else None

 def deliver_field_prisoner(self):
  if self.field_status()!='carried' or self.mounted or not self.near_bounty_board():return False
  self.record_jail_intake('Drifter','field arrest')
  self.field_prisoner=None;self.field_arrests+=1
  self.money+=24;self.change_honor(2,'Bandit arrested alive')
  self.notify('DRIFTER DELIVERED ALIVE: +$24',5)
  self.sound_cue('arrest');self.save()
  return True

 def bounty_state(self):
  return self.contract.get('status','hunting') if self.contract else None

 def bounty_actor(self):
  if not self.contract:return None
  return next((a for a in self.actors if a.kind=='bounty_target' and
               a.name==self.contract['name'] and not a.dead),None)

 def spawn_contract_target(self):
  if not self.contract or self.contract.get('finished'):return
  status=self.bounty_state()
  if status=='carried':return
  if self.bounty_actor():return
  x,y=(self.contract.get('captive_pos') or self.contract['location'])
  x,y=self.safe_enemy_spawn(x,y)
  a=Actor(x,y,'bounty_target',self.contract['name'],145,145,86)
  self.actors.append(a)
  if status in ('roped','hogtied'):self.contract['captive_pos']=[x,y]

 def begin_bounty(self):
  if not self.near_bounty_board():return
  if self.contract:
   self.notify('Active bounty: '+self.contract['name']+' ('+self.bounty_state()+'). See J.',5)
   return
  jobs=[
   ('Vulture Jack',(1820,600),60),
   ('Rattlesnake Cole',(4210,1120),90),
   ('Maeve Blackwater',(7250,4320),110),
   ('Red Sand Boone',(10400,8000),140),
   ('The Iron Fox',(16200,9500),180)]
  name,location,reward=jobs[self.bounties_done%len(jobs)]
  self.contract={'name':name,'location':list(location),'reward':reward,
                 'alive_reward':reward*2,'status':'hunting','finished':False}
  self.spawn_contract_target()
  self.notify('WANTED DEAD $'+str(reward)+' / ALIVE $'+str(reward*2)+' — '+name,6)
  self.save()

 def finish_bounty(self,a=None,alive=False):
  if not self.contract:return False
  if a is not None and a.name!=self.contract['name']:return False
  if alive and self.bounty_state()!='carried':return False
  reward=(int(self.contract.get('alive_reward',self.contract['reward']*2)) if alive
          else int(self.contract['reward']))
  target=self.bounty_actor()
  if target:target.dead=True
  name=self.contract['name']
  if alive and self.waypoint==[418,463]:self.waypoint=None
  if alive:self.record_jail_intake(name,'named bounty')
  self.money+=reward;self.bounties_done+=1;self.contract=None
  self.change_honor(5 if alive else 2,'Bounty delivered alive' if alive else 'Bounty brought to justice')
  self.notify(name+(' DELIVERED ALIVE' if alive else ' DEAD')+': +$'+str(reward),5)
  self.sound_cue('bounty_complete');self.save()
  return True

 def throw_lasso(self):
  if self.screen!='playing' or self.dialog or self.interior or self.map_open or self.journal_open or self.lasso_cooldown>0:return False
  if self.field_prisoner or self.bounty_state() in ('roped','hogtied','carried','surrendered'):
   self.notify('Secure or deliver your current prisoner first.',3);return False
  self.lasso_cooldown=1.2
  mx,my=self.mouse;ax=mx+self.camx-self.x;ay=my+self.camy-self.y
  length=math.hypot(ax,ay)
  if length<8:ax,ay=self.facing;length=math.hypot(ax,ay)
  ux,uy=ax/max(length,.01),ay/max(length,.01)
  fx,fy=self.x+ux*15,self.y+uy*15
  tx,ty=self.x+ux*235,self.y+uy*235
  candidates=[a for a in self.actors if not a.dead and (a.kind=='bandit' or
              (a.kind=='bounty_target' and self.bounty_state()=='hunting'))]
  hits=[]
  for a in candidates:
   projection=(a.x-fx)*ux+(a.y-fy)*uy
   sideways=abs((a.x-fx)*uy-(a.y-fy)*ux)
   if 0<=projection<=220 and sideways<=26 and self.line_of_fire(fx,fy,a.x,a.y):
    hits.append((projection,a))
  if hits:
   # If both are in the aim corridor, prefer the named wanted target.
   target=min(hits,key=lambda hit:(0 if hit[1].kind=='bounty_target' else 1,hit[0]))[1]
   self.lasso_visual=[fx,fy,target.x,target.y,.48]
   if target.kind=='bounty_target':
    self.contract['status']='roped';self.contract['rope_timer']=8.0
    self.contract['captive_pos']=[target.x,target.y]
   else:
    target.kind='field_prisoner';target.shoot=0.
    self.field_prisoner={'status':'roped','position':[target.x,target.y],'rope_timer':8.0}
   self.notify('LASSO HIT! Dismount and press G nearby to hogtie.',4);self.audio.cue('lasso')
   return True
  self.lasso_visual=[fx,fy,tx,ty,.3]
  self.notify('Lasso missed. Aim at an outlaw within range.',2)
  return False

 def surrender_outlaw(self,a):
  # Surrender is never applied to scripted mission enemies or deputies.
  if a.dead or a.kind not in ('bandit','bounty_target'):return False
  if a.kind=='bounty_target':
   if not self.contract or self.bounty_state()!='hunting':return False
   self.contract['status']='surrendered'
   self.contract['captive_pos']=[a.x,a.y]
  else:
   if self.field_prisoner:return False
   a.kind='field_prisoner';a.shoot=0.
   self.field_prisoner={'status':'surrendered','position':[a.x,a.y]}
  a.shoot=0.;a.speed=0.
  self.notify(a.name.upper()+' SURRENDERS! Dismount and press G to hogtie.',5)
  return True

 def check_surrender(self,a):
  if a.dead or a.kind not in ('bandit','bounty_target'):return False
  if self.field_prisoner and a.kind=='bandit':return False
  if a.hp<=0:return False
  wounded=a.hp<=a.maxhp*.35
  # Local patrols and player have the outlaw surrounded.
  deputies=sum(not p.dead and p.kind=='law_patrol' and
              math.hypot(p.x-a.x,p.y-a.y)<225 for p in self.actors)
  outnumbered=deputies>=2 and math.hypot(a.x-self.x,a.y-self.y)<200
  if wounded or outnumbered:return self.surrender_outlaw(a)
  return False

 def hogtie_bounty(self):
  field=self.field_status() in ('roped','surrendered')
  if not field and self.bounty_state() not in ('roped','surrendered'):return False
  if self.mounted:
   self.notify('Dismount Whiskey (H) before hogtying.',2);return False
  a=self.field_actor() if field else self.bounty_actor()
  if not a or math.hypot(a.x-self.x,a.y-self.y)>76:
   self.notify('Move closer to the roped outlaw to hogtie.',2);return False
  if field:
   self.field_prisoner['status']='hogtied';self.field_prisoner.pop('rope_timer',None)
   self.field_prisoner['position']=[a.x,a.y]
  else:
   self.contract['status']='hogtied';self.contract.pop('rope_timer',None)
   self.contract['captive_pos']=[a.x,a.y]
  self.notify('HOGTIED! Press E nearby to pick up the prisoner.',4);self.audio.cue('hogtie')
  self.save();return True

 def pick_up_bounty(self):
  if self.mounted:return False
  field=self.field_status()=='hogtied'
  if not field and self.bounty_state()!='hogtied':return False
  a=self.field_actor() if field else self.bounty_actor()
  if not a or math.hypot(a.x-self.x,a.y-self.y)>77:return False
  self.actors.remove(a)
  if field:
   self.field_prisoner['status']='carried'
  else:
   self.contract['status']='carried';self.contract.pop('captive_pos',None)
  self.waypoint=[418,463]
  self.notify('Prisoner secured. Ride to Sheriff Bell; dismount and press E.',5)
  self.save();return True

 def deliver_bounty(self):
  if not self.contract or self.bounty_state()!='carried':return False
  if self.mounted:
   self.notify('Dismount (H) to hand your prisoner to the sheriff.',2);return False
  if not self.near_bounty_board():return False
  return self.finish_bounty(alive=True)

 def update_bounty_capture(self,dt):
  self.lasso_cooldown=max(0.,self.lasso_cooldown-dt)
  if self.lasso_visual:
   self.lasso_visual[4]-=dt
   if self.lasso_visual[4]<=0:self.lasso_visual=None
  if self.contract and self.bounty_state()=='roped':
   timer=max(0.,float(self.contract.get('rope_timer',8.))-dt)
   self.contract['rope_timer']=timer
   if timer<=0:
    self.contract['status']='hunting';self.contract.pop('rope_timer',None)
    self.contract.pop('captive_pos',None)
    self.notify('The wanted outlaw broke free!',3)
  if self.field_status()=='roped':
   timer=max(0.,float(self.field_prisoner.get('rope_timer',8.))-dt)
   self.field_prisoner['rope_timer']=timer
   if timer<=0:
    a=self.field_actor()
    if a:a.kind='bandit';a.shoot=1.5
    self.field_prisoner=None
    self.notify('The drifter slipped the rope!',3)

 def spawn_road_encounter(self):
  if any(not a.dead and a.kind in ('traveler','road_wagon','road_cache') for a in self.actors):return False
  if self.in_safe_settlement(self.x,self.y) or self.safe_timer>0:return False
  for _ in range(10):
   angle=random.random()*math.tau;distance=random.randint(270,380)
   x=self.x+math.cos(angle)*distance;y=self.y+math.sin(angle)*distance
   if not self.can_move(x,y,20) or self.in_safe_settlement(x,y):continue
   incident=random.choice(('traveler','traveler','road_wagon','road_wagon','road_cache','road_cache','ambush'))
   if incident=='ambush':
    spawned=0
    for sx,sy in ((x,y),(x+75,y-35)):
     if self.can_move(sx,sy,20) and not self.in_safe_settlement(sx,sy):
      self.actors.append(Actor(sx,sy,'bandit','Road Ambusher',75,75,80));spawned+=1
    if spawned:
     self.notify('AMBUSH! Armed riders are closing in along the road.',5)
     return True
    continue
   names={'traveler':'Stranded Traveler','road_wagon':'Broken Wagon','road_cache':'Forgotten Supply Crate'}
   self.actors.append(Actor(x,y,incident,names[incident],100,100,0))
   self.notify({'traveler':'Someone needs help along the road.',
                'road_wagon':'A broken wagon lies up ahead.',
                'road_cache':'Someone abandoned supplies along the trail.'}[incident],4)
   return True
  return False

 def road_escort(self):
  return next((a for a in self.actors if a.kind=='escort' and not a.dead),None)

 def restore_road_escort(self):
  job=self.road_contract
  if not job or job['type']!='escort' or job.get('status')!='outbound':return
  if self.road_escort():return
  pos=job.get('escort_pos',job['origin_pos'])
  position=safe_event_position(*pos,self.can_move)
  if position:
   a=Actor(*position,'escort','Wagon Passenger',65,65,112)
   self.actors.append(a)
  else:self.notify('Escort route blocked. Return to the waystation.',4)

 def offer_road_contract(self):
  if self.mounted or self.interior or self.dialog or self.choice_dialog:return False
  station=nearby_station(self.x,self.y,220)
  if not station:
   self.notify('Road jobs are posted at named waystations. Approach a signpost.',4);return False
  if self.road_contract:
   job=self.road_contract
   if job['origin']==station[0] and job['status']=='return':
    return self.complete_road_contract()
   self.notify('ACTIVE ROAD JOB: '+job['title']+'. Finish the current assignment.',4)
   return False
  if self.road_offer_day.get(station[0])==self.economy_day:
   self.notify('No more dispatches here today. Try another station or return tomorrow.',4)
   return False
  job=offer_for_day(station[0],self.economy_day)
  if not job:return False
  if job['type'] in ('survey','salvage'):
   pos=safe_event_position(*job['target_pos'],self.can_move)
   if pos:job['target_pos']=list(pos)
  self.road_contract=job
  self.road_offer_day[station[0]]=self.economy_day
  self.waypoint=list(job['target_pos'])
  if job['type']=='escort':
   self.restore_road_escort()
  self.notify('ROAD JOB: '+job['title']+' to '+job['destination']+' • $'+str(job['reward']),6)
  self.audio.cue('job_accept')
  self.save()
  return True

 def complete_road_contract(self):
  job=self.road_contract
  if not job:return False
  if job['type']=='escort':
   follower=self.road_escort()
   if follower:self.actors.remove(follower)
  amount=int(job['reward'])
  self.money+=amount;self.road_income+=amount;self.road_contracts_done+=1
  region=region_at(*job['target_pos'])
  self.regional_standing[region]=min(100,self.regional_standing.get(region,0)+3)
  self.change_honor(2 if job['type']=='escort' else 1,'Frontier road service')
  self.road_contract=None
  self.waypoint=None
  self.notify('ROAD JOB COMPLETE: +$'+str(amount)+' • '+region,6)
  self.audio.cue('job_complete');self.save()
  return True

 def progress_road_contract(self):
  job=self.road_contract
  if not job or self.mounted or job['status']!='outbound':return False
  tx,ty=job['target_pos']
  if math.hypot(self.x-tx,self.y-ty)>145:return False
  if job['type']=='escort':
   follower=self.road_escort()
   if not follower or math.hypot(follower.x-tx,follower.y-ty)>240:
    self.notify('Wait for your passenger to reach the destination.',3);return False
   return self.complete_road_contract()
  if job['type']=='courier':
   return self.complete_road_contract()
  job['status']='return'
  self.waypoint=list(job['origin_pos'])
  self.notify('Evidence secured. Return to '+job['origin_name']+' and press N.',5)
  self.audio.cue('job_complete');self.save()
  return True

 def update_road_escort(self,dt):
  job=self.road_contract
  if not job or job['type']!='escort' or job['status']!='outbound':return
  passenger=self.road_escort()
  if not passenger:
   self.notify('Your passenger is lost. The escort contract failed.',4)
   self.road_contract=None;self.waypoint=None;return
  gap=math.hypot(self.x-passenger.x,self.y-passenger.y)
  if gap>1250:
   job['lost_time']=job.get('lost_time',0.)+dt
   if job['lost_time']>18:
    self.actors.remove(passenger);self.road_contract=None;self.waypoint=None
    self.notify('ESCORT FAILED: You left your passenger too far behind.',5);self.save()
   return
  job['lost_time']=0.
  if gap<75:return
  dx=(self.x-passenger.x)/gap;dy=(self.y-passenger.y)/gap
  original=(passenger.x,passenger.y)
  speed=(455 if self.horse_motion.get('speed',0)>370 else 305) if self.mounted else 133
  self.move_actor(passenger,dx*speed*dt,dy*speed*dt)
  if math.hypot(passenger.x-original[0],passenger.y-original[1])<.1:
   job['stuck_time']=job.get('stuck_time',0.)+dt
   if job['stuck_time']>3 and gap<450:
    new_pos=safe_event_position(self.x-dx*78,self.y-dy*78,self.can_move)
    if new_pos:passenger.x,passenger.y=new_pos
    job['stuck_time']=0.
  else:job['stuck_time']=0.
  job['escort_pos']=[passenger.x,passenger.y]

 def regional_rumor(self):
  text=dispatch_rumor(self.x,self.y,self.economy_day)
  site=nearest_landmark(self.x,self.y)
  if site and not (self.road_contract or self.work_active or self.side_job):
   self.waypoint=[site[2],site[3]]
   self.notify('RUMOR: '+site[1]+' marked on map. '+text,6)
  else:self.notify('ROAD RUMOR: '+text,5)
  return text

 def chapter_node(self):
  if not self.chapter_active:return None
  chapter=CHAPTER_BY_ID.get(self.chapter_active.get('id'))
  if not chapter:return None
  return node_for(chapter,self.chapter_active.get('step',0))

 def chapter_target(self):
  node=self.chapter_node()
  if not node:return None
  # Nodes are in real named towns. Use nearest safe sidewalk if the center is occupied.
  return self.safe_enemy_spawn(node['x'],node['y'])

 def progress_regional_chapter(self):
  if self.mounted or self.interior or self.dialog or self.choice_dialog:
   self.notify('Dismount and finish conversations before investigating.',3);return False
  if not self.chapter_active:
   chapter=available_chapter(self.x,self.y,self.chapter_completed)
   if not chapter:
    self.notify('Regional stories begin in Galloway or Roan Creek. Visit their town squares.',4)
    return False
   self.chapter_active={'id':chapter['id'],'step':1}
   node=node_for(chapter,1)
   self.waypoint=list(self.safe_enemy_spawn(node['x'],node['y']))
   self.say('FRONTIER DISPATCH',[chapter['dialogue'][0],node['description']])
   self.notify('STORY BEGINS: '+chapter['title']+' — '+node['town_name'],5)
   self.save();return True
  chapter=CHAPTER_BY_ID.get(self.chapter_active.get('id'))
  if not chapter:
   self.chapter_active=None;return False
  step=int(self.chapter_active.get('step',1))
  if step<1 or step>=len(chapter['steps']):return False
  node=node_for(chapter,step)
  tx,ty=self.safe_enemy_spawn(node['x'],node['y'])
  if math.hypot(self.x-tx,self.y-ty)>330:
   self.notify('Next lead: '+node['town_name']+'. Follow the white map marker.',4)
   return False
  if step==len(chapter['steps'])-1:
   self.chapter_completed.append(chapter['id'])
   self.chapter_active=None
   self.money+=chapter['reward'];self.chapter_earnings+=chapter['reward']
   self.change_honor(chapter['honor'],'Finished '+chapter['title'])
   region=region_at(self.x,self.y)
   self.regional_standing[region]=min(100,self.regional_standing.get(region,0)+6)
   self.waypoint=None
   self.say('FRONTIER DISPATCH',[chapter['dialogue'][step],
      'Received $'+str(chapter['reward'])+' for '+chapter['title']+'.'])
   self.audio.cue('bounty_complete');self.save();return True
  self.chapter_active['step']=step+1
  next_node=node_for(chapter,step+1)
  self.waypoint=list(self.safe_enemy_spawn(next_node['x'],next_node['y']))
  self.say('FRONTIER DISPATCH',[chapter['dialogue'][step],next_node['description']])
  self.notify(chapter['title']+' — '+next_node['town_name'],5)
  self.audio.cue('job_complete');self.save();return True

 def offer_frontier_job(self,guide):
  town=nearby_settlement(guide.x,guide.y)
  if not town:return
  job=next((j for j in SIDE_JOBS if j[1]==town),None)
  if not job:return
  key,origin,title,description,targets,reward=job
  if key in self.side_completed:
   self.say(guide.name.upper(),['You kept your word, traveler. Our town remembers it.','The roads have been a little safer since you helped.'])
   return
  if self.side_job:
   active=get_job(self.side_job.get('id'))
   self.say(guide.name.upper(),['You have unfinished work: '+(active[2] if active else 'the frontier job')+'.','Finish your current errand before taking another.'])
   return
  self.side_job={'id':key,'step':0}
  self.waypoint=list(targets[0])
  self.say(guide.name.upper(),[title+'. '+description+'.',f'Payment is ${reward} when you finish. The first clue is marked on your map.'])
  self.notify('NEW SIDE JOB: '+title+' — see J journal',5)
  self.save()

 def advance_side_job(self):
  if not self.side_job:return False
  job=get_job(self.side_job.get('id'))
  if not job:return False
  key,origin,title,description,targets,reward=job
  step=int(self.side_job.get('step',0))
  if step<0 or step>=len(targets):return False
  tx,ty=targets[step]
  if (self.x-tx)**2+(self.y-ty)**2>85**2:return False
  step+=1
  if step<len(targets):
   self.side_job['step']=step
   self.waypoint=list(targets[step])
   self.say('JESSE',['Found the first piece of evidence for '+title+'.','The next lead is now marked on your map.'])
  else:
   self.money+=reward
   self.change_honor(2,'Frontier job completed')
   self.side_completed.append(key)
   self.side_job=None;self.waypoint=None
   self.say('JESSE',['That settles '+title+'.',f'The agreed payment of ${reward} is yours.'])
   self.notify('SIDE JOB COMPLETE: +$'+str(reward),5)
  self.save()
  return True

 def gather_resource(self):
  if self.mounted or self.interior:return False
  for identifier,x,y,label,kind in RESOURCE_NODES:
   if identifier in self.gathered_nodes or (self.x-x)**2+(self.y-y)**2>90**2:continue
   self.gathered_nodes.append(identifier)
   if kind=='tonic':
    self.tonics+=1;message='Gathered '+label+': +1 health tonic'
   else:
    self.money+=9;message='Collected '+label+': +$9'
   self.notify(message,4);self.save()
   return True
  self.notify('No uncollected resource nearby. Look for a herb or ore marker.',2)
  return False

 def rest_at_frontier_camp(self):
  if self.mounted or self.interior:return False
  town=nearby_settlement(self.x,self.y,225) or near_waystation(self.x,self.y,225)
  if not town:return False
  if town in self.camps_used:
   self.notify('You have already used the free camp at this settlement.',3);return False
  self.camps_used.append(town)
  self.hp=min(self.maxhp,self.hp+30)
  self.advance_clock(6);self.update_npc_schedules()
  self.safe_timer=max(self.safe_timer,15.)
  self.notify('Rested by the campfire: +30 HP, six hours passed.',5)
  self.save()
  return True

 def discover_landmark(self):
  key=near_landmark(self.x,self.y,365)
  if not key or key in self.landmarks_found:return False
  item=landmark_by_key(key)
  self.landmarks_found.append(key)
  self.notify('LANDMARK DISCOVERED: '+item[1].upper()+' ('+
              str(len(self.landmarks_found))+'/'+str(len(LANDMARKS))+')',5)
  self.save()
  return True

 def discover_settlement(self):
  town=nearby_settlement(self.x,self.y,385)
  if not town or town in self.visited_settlements:return False
  self.visited_settlements.append(town)
  info=get_settlement(town)
  self.money+=5
  self.notify('DISCOVERED: '+info[1].upper()+' — +$5 in trail supplies',5)
  self.save()
  return True

 def safe_enemy_spawn(self,x,y):
  # Don't place enemies inside cabins, walls or terrain cover.
  if self.can_move(x,y,20):return (x,y)
  for radius in range(35,366,35):
   for dx,dy in ((radius,0),(-radius,0),(0,radius),(0,-radius),
                 (radius,radius),(radius,-radius),(-radius,radius),(-radius,-radius)):
    nx,ny=x+dx,y+dy
    if self.can_move(nx,ny,20):return (nx,ny)
  raise ValueError('No clear mission spawn near '+str((x,y)))

 def quest(self,stage):
  self.stage=stage;self.notify('NEW OBJECTIVE: '+MISSIONS[stage][0].upper(),5)
  self.save()
  if stage==1:self.spawn_mission('hollow',[(1900,350),(2010,420),(2090,510),(1970,610),(1820,660)],95)
  if stage==4:self.spawn_mission('blackspur',[(1975,1290),(2080,1280),(2030,1340)],105)
  if stage==6:self.spawn_mission('crow',[(1370,1030),(1430,1100),(1510,1080),(1580,1030)],115,boss=(1480,1030))
 def spawn_mission(self,tag,positions,hp,boss=None):
  if tag in self.mission_activated:return
  self.mission_activated.add(tag)
  for i,(x,y) in enumerate(positions):
   x,y=self.safe_enemy_spawn(x,y)
   self.actors.append(Actor(x,y,'mission_'+tag,tag.title()+' rider',hp,hp,91))
  if boss:
   bx,by=self.safe_enemy_spawn(*boss)
   self.actors.append(Actor(bx,by,'mission_'+tag,'Crow',240,240,105))
 def enemies_remaining(self,tag):return sum(not a.dead and a.kind=='mission_'+tag for a in self.actors)

 def key_down(self,e):
  key=e.keysym.lower();first=key not in self.keys;self.keys.add(key)
  if not first:return
  if key=='q' and self.screen=='playing' and not self.dialog and not self.interior and not self.map_open and not self.journal_open:
   self.deadeye_active=not self.deadeye_active and self.deadeye>0
   self.notify('DEAD EYE '+('ENGAGED' if self.deadeye_active else 'DISENGAGED'),1.0)
   return
  if key=='f6' and self.screen in ('playing','paused'):
   levels=list(DIFFICULTIES);self.difficulty=levels[(levels.index(self.difficulty)+1)%len(levels)]
   self.notify('COMBAT DIFFICULTY: '+self.difficulty.upper(),2);return
  if key=='f7' and self.screen in ('playing','paused'):
   self.aim_assist=not self.aim_assist;self.notify('AIM ASSIST '+('ON' if self.aim_assist else 'OFF'),2);return
  if key=='f5' and self.screen in ('playing','paused'):
   self.save(manual=True);return
  if key=='v' and self.screen in ('title','playing','paused'):
   self.sound_on=not self.sound_on;self.audio.enabled=self.sound_on
   self.notify('SOUND EFFECTS '+('ON' if self.sound_on else 'OFF')+' ('+self.audio.backend+')',2)
   self.sound_cue('menu');return
  if key=='o' and self.screen in ('title','playing','paused'):
   self.audio.set_music_enabled(not self.audio.music_enabled)
   self.notify('AMBIENT MUSIC '+('ON' if self.audio.music_enabled else 'OFF')+' ('+self.audio.backend+')',3)
   return
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
   if key=='k' and self.interior=='Sheriff':self.show_jail=not self.show_jail
   elif self.show_jail and key in ('escape','e','k'):self.show_jail=False
   elif key=='b' and self.indoor_y<380:self.use_counter()
   elif key=='e':
    if self.indoor_y>475:self.leave_interior()
    elif self.indoor_y<360:self.use_counter()
    else:self.notify('Walk up to the counter or the exit, then press E.')
   elif key=='escape':self.leave_interior()
   elif key=='f5':self.save(manual=True)
   elif key=='f1':self.show_help=not self.show_help
   return
  if key=='escape' and self.work_ledger_open:self.work_ledger_open=False;return
  if key=='escape':self.screen='playing' if self.screen=='paused' else 'paused';self.deadeye_active=False;return
  if self.screen=='paused':return
  if self.map_open and key in ('z','up','down','left','right','w','a','s','d','escape','tab','return'):
   if key=='z':self.map_zoom=not self.map_zoom;self.map_center=[self.x,self.y]
   elif key=='escape':self.map_open=False
   elif key=='tab':self.map_destination_index=(self.map_destination_index+1)%len(MAP_DESTINATIONS)
   elif key=='return':
    _,name,tx,ty=MAP_DESTINATIONS[self.map_destination_index]
    self.waypoint=[tx,ty];self.notify('DESTINATION: '+name+' marked on the map.',3)
   else:
    dx=int(key in ('right','d'))-int(key in ('left','a'))
    dy=int(key in ('down','s'))-int(key in ('up','w'))
    stride=2400 if self.map_zoom else 7500
    self.map_center=[max(0,min(WW,self.map_center[0]+dx*stride)),
                     max(0,min(WH,self.map_center[1]+dy*stride))]
    self.map_zoom=True
   self.keys.discard(key);return
  if key=='f1':self.show_help=not self.show_help
  elif key=='m':
   self.map_open=not self.map_open;self.journal_open=False;self.work_ledger_open=False;self.deadeye_active=False
   if self.map_open:self.map_center=[self.x,self.y];self.keys.clear()
  elif key=='j':self.journal_open=not self.journal_open;self.map_open=False;self.work_ledger_open=False;self.deadeye_active=False
  elif key=='c' and self.waypoint is not None:self.waypoint=None;self.notify('Waypoint cleared.',2)
  elif key=='e':
   # Read the X11 Shift bit as well as key tracking for reliable combinations.
   shift=bool(getattr(e,'state',0)&0x0001) or 'shift_l' in self.keys or 'shift_r' in self.keys
   if shift:
    door=self.near_door()
    if door:self.enter_interior(door)
    else:self.notify('Stand at a building entrance, then press Shift+E.',2)
   else:self.interact()
  elif key=='b' and self.near_bounty_board():self.begin_bounty()
  elif key=='p' and not self.map_open and not self.journal_open:self.offer_work()
  elif key=='n' and not self.map_open and not self.journal_open:self.offer_road_contract()
  elif key=='u' and not self.map_open and not self.journal_open:self.regional_rumor()
  elif key=='y' and not self.map_open and not self.journal_open:self.progress_regional_chapter()
  elif key=='i':self.work_ledger_open=not self.work_ledger_open;self.map_open=False;self.journal_open=False
  elif key=='f':self.gather_resource()
  elif key=='t':self.rest_at_frontier_camp()
  elif key=='l':self.throw_lasso()
  elif key=='g':self.hogtie_bounty()
  elif key=='h':self.toggle_horse()
  elif key=='2':self.switch_weapon()
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
 def new_game(self):
  sound=self.audio.enabled;music=self.audio.music_enabled
  self.reset();self.audio.enabled=sound;self.sound_on=sound
  self.audio.set_music_enabled(music)
  self.screen='playing';self.say('NARRATOR',['1889. The borderlands have no patience for saints.','Your name is Jesse Vale. You have $35, six rounds, and a horse named Whiskey.','Sheriff Bell is looking for someone with nothing left to lose. Find him at the jail.']);self.save()
 def continue_game(self):
  self.reset()
  try:
   s=self.read_save_data()
   for k in ('x','y','hp','money','ammo','reserve','tonics','stage','kills','wanted','clock','mounted','horse_x','horse_y','ledger','death_count','honor','crimes','deadeye','bounties_done'):
    if k in s:setattr(self,k,s[k])
   self.deadeye=max(0.,min(100.,float(self.deadeye)))
   self.honor=max(0,min(100,int(self.honor)))
   self.law_status='WANTED' if self.wanted>=1.2 else ('INVESTIGATING' if self.wanted>0 else 'PEACE')
   self.mission_activated=set(s.get('mission_activated',[]))
   self.waypoint=s.get('waypoint')
   self.sound_on=bool(s.get('sound_on',False))
   self.audio.configure(s.get('audio',{}))
   self.audio.enabled=self.sound_on
   self.economy_day=int(s.get('economy_day',0))
   self.shop_stock=dict(s.get('shop_stock',{}))
   self.work_active=s.get('work_active')
   self.work_records=dict(s.get('work_records',{}))
   self.work_finished=int(s.get('work_finished',0))
   self.work_income=int(s.get('work_income',0))
   self.work_expenses=int(s.get('work_expenses',0))
   self.chapter_active=s.get('chapter_active')
   self.chapter_completed=list(s.get('chapter_completed',[]))
   self.chapter_earnings=int(s.get('chapter_earnings',0))
   self.horse_motion.update(s.get('horse_motion',{}))
   self.side_job=s.get('side_job')
   self.side_completed=list(s.get('side_completed',[]))
   self.gathered_nodes=list(s.get('gathered_nodes',[]))
   self.camps_used=list(s.get('camps_used',[]))
   self.visited_settlements=list(s.get('visited_settlements',[]))
   self.landmarks_found=list(s.get('landmarks_found',[]))
   self.road_contract=s.get('road_contract')
   self.road_contracts_done=int(s.get('road_contracts_done',0))
   self.road_income=int(s.get('road_income',0))
   self.road_offer_day=dict(s.get('road_offer_day',{}))
   self.regional_standing=dict(s.get('regional_standing',{}))
   self.field_arrests=int(s.get('field_arrests',0))
   self.weapon=normal_weapon(s.get('weapon','peacemaker'),self.field_arrests,self.work_finished,self.kills)
   self.difficulty=normal_difficulty(s.get('difficulty','standard'))
   self.aim_assist=bool(s.get('aim_assist',False))
   self.ammo=max(0,min(int(self.ammo),WEAPONS[self.weapon]['capacity']))
   self.jail_roster=list(s.get('jail_roster',[]))
   self.law_reputation=int(s.get('law_reputation',0))
   self.field_prisoner=s.get('field_prisoner')
   if self.field_prisoner and self.field_prisoner.get('status') in ('roped','hogtied','surrendered'):
    px,py=self.field_prisoner['position']
    px,py=self.safe_enemy_spawn(px,py)
    self.field_prisoner['position']=[px,py]
    self.actors.append(Actor(px,py,'field_prisoner','Captured Drifter',70,70,0))
   self.contract=s.get('contract')
   if self.contract and not self.contract.get('finished',False):
    self.contract.setdefault('status','hunting')
    self.contract.setdefault('alive_reward',int(self.contract['reward'])*2)
    self.spawn_contract_target()
   # Quest combat must regenerate after loading (kill progress is persisted).
   tag={1:'hollow',4:'blackspur',6:'crow'}.get(self.stage)
   if tag:
    self.mission_activated.discard(tag)
    positions={'hollow':[(1900,350),(2010,420),(2090,510),(1970,610),(1820,660)],'blackspur':[(1975,1290),(2080,1280),(2030,1340)],'crow':[(1370,1030),(1430,1100),(1510,1080),(1580,1030)]}[tag]
    self.spawn_mission(tag,positions,{'hollow':95,'blackspur':105,'crow':115}[tag],boss=(1480,1030) if tag=='crow' else None)
    eliminated=int(s.get('stage_kills',0))
    for a in [a for a in self.actors if a.kind=='mission_'+tag][:eliminated]:a.dead=True
   self.restore_road_escort()
   self.update_npc_schedules()
   self.screen='playing';self.safe_timer=18.;self.notify('Recovered backup save. Press F5 to restore primary.' if self.loaded_backup else 'Loaded last save from disk. F5 saves manually.',5)
  except (OSError,ValueError,TypeError,KeyError) as ex:
   # Never overwrite a damaged save by quietly starting a new game.
   self.screen='title';self.notify('SAVE ERROR: '+str(ex),7)
   print('Cannot load save:',ex,file=sys.stderr)
 def read_save_data(self):
  errors=[]
  for path in (SAVE,SAVE+'.bak'):
   try:
    with open(path,encoding='utf-8') as file:data=json.load(file)
    if not isinstance(data,dict):raise ValueError('save is not an object')
    for key in ('x','y','stage'):
     if key not in data:raise ValueError('save lacks '+key)
    if not (0<=int(data['stage'])<len(MISSIONS)):raise ValueError('invalid story stage')
    if not (23<=float(data['x'])<=WW-23 and 23<=float(data['y'])<=WH-23):
     raise ValueError('coordinates outside territory')
    self.loaded_backup=(path!=SAVE)
    return data
   except (OSError,ValueError,TypeError,KeyError) as ex:errors.append(str(ex))
  raise ValueError('primary and backup unusable: '+'; '.join(errors))

 def save(self,manual=False):
  if self.screen not in ('playing','paused','ending'):return False
  d={k:getattr(self,k) for k in ('x','y','hp','money','ammo','reserve','tonics','stage','kills','wanted','clock','mounted','horse_x','horse_y','ledger','death_count','honor','crimes','deadeye')}
  d['mission_activated']=list(self.mission_activated)
  d['contract']=self.contract;d['bounties_done']=self.bounties_done
  d['field_prisoner']=self.field_prisoner;d['field_arrests']=self.field_arrests
  d['jail_roster']=self.jail_roster;d['law_reputation']=self.law_reputation
  d['waypoint']=self.waypoint;d['sound_on']=self.sound_on;d['audio']=self.audio.settings()
  d['economy_day']=self.economy_day;d['shop_stock']=self.shop_stock
  d['work_active']=self.work_active;d['work_records']=self.work_records
  d['work_finished']=self.work_finished;d['work_income']=self.work_income;d['work_expenses']=self.work_expenses
  d['chapter_active']=self.chapter_active;d['chapter_completed']=self.chapter_completed
  d['chapter_earnings']=self.chapter_earnings;d['horse_motion']=self.horse_motion
  d['side_job']=self.side_job;d['side_completed']=self.side_completed
  d['gathered_nodes']=self.gathered_nodes;d['camps_used']=self.camps_used
  d['visited_settlements']=self.visited_settlements
  d['landmarks_found']=self.landmarks_found
  if self.road_contract and self.road_contract.get('type')=='escort':
   passenger=self.road_escort()
   if passenger:self.road_contract['escort_pos']=[passenger.x,passenger.y]
  d['road_contract']=self.road_contract;d['road_contracts_done']=self.road_contracts_done
  d['road_income']=self.road_income;d['road_offer_day']=self.road_offer_day
  d['regional_standing']=self.regional_standing
  d['weapon']=self.weapon;d['difficulty']=self.difficulty;d['aim_assist']=self.aim_assist
  d['save_version']=VERSION
  tag={1:'hollow',4:'blackspur',6:'crow'}.get(self.stage)
  if tag:d['stage_kills']=sum(a.dead for a in self.actors if a.kind=='mission_'+tag)
  try:
   os.makedirs(os.path.dirname(SAVE),exist_ok=True)
   tmp=SAVE+'.tmp'
   with open(tmp,'w') as f:
    json.dump(d,f);f.flush();os.fsync(f.fileno())
   # Rotate only valid existing saves, preserving a recoverable backup.
   if os.path.exists(SAVE) and not self.loaded_backup:
    try:
     with open(SAVE,encoding='utf-8') as old:
      old_data=json.load(old)
     if isinstance(old_data,dict) and all(k in old_data for k in ('x','y','stage')):
      shutil.copy2(SAVE,SAVE+'.bak')
    except (OSError,ValueError,TypeError):pass
   os.replace(tmp,SAVE)
   self.loaded_backup=False
   self.last_save_ok=True;self.save_error='';self.last_save_time=time.strftime('%H:%M:%S')
   if manual:self.notify('SAVED at '+self.last_save_time+' to '+SAVE,5)
   return True
  except (OSError,TypeError,ValueError) as ex:
   self.last_save_ok=False;self.save_error=str(ex)
   self.notify('SAVE FAILED: '+str(ex),6)
   return False

 def current_map_view(self):
  return map_view(self.map_zoom,*self.map_center)

 def set_waypoint_from_map(self,px,py):
  location=world_from_map(px,py,self.current_map_view())
  if location is None:return False
  wx,wy=int(location[0]),int(location[1])
  self.waypoint=[wx,wy]
  self.notify('Waypoint set: '+self.region_name(wx,wy),3)
  return True

 def weather_kind(self):
  cycle=int(self.clock//3)
  region=int(self.x//2400)+int(self.y//1600)
  value=(cycle*7+region*11)%13
  return 'rain' if value in (2,6) else ('dust' if value in (4,8,10) else 'clear')

 def sound_cue(self,event='menu'):
  # Routes semantic cues to optional backend (system bell for now).
  return self.audio.cue(event)

 def quest_target(self):
  return [(418,463),(1840,470),(418,463),(1270,1465),(2040,1280),(1270,1465),(1480,1030),(418,463),None][self.stage]
 def advance_dialog(self):
  if not self.dialog:return
  self.dialog[2]+=1
  if self.dialog[2]>=len(self.dialog[1]):self.dialog=None
 def interact(self):
  # Deliver any prisoner before normal sheriff conversation.
  if self.field_status()=='carried':
   sheriffs=(a for a in self.actors if a.kind=='sheriff' and not a.dead)
   if any(math.hypot(a.x-self.x,a.y-self.y)<105 for a in sheriffs):
    if self.mounted:self.notify('Dismount (H) before delivering the drifter.',3)
    else:self.deliver_field_prisoner()
    return
  if self.contract and self.bounty_state()=='carried':
   sheriffs=(a for a in self.actors if a.kind=='sheriff' and not a.dead)
   if any(math.hypot(a.x-self.x,a.y-self.y)<105 for a in sheriffs):
    self.deliver_bounty();return
  if self.mounted and (self.bounty_state()=='hogtied' or self.field_status()=='hogtied'):
   captive=self.field_actor() if self.field_status()=='hogtied' else self.bounty_actor()
   if captive and math.hypot(captive.x-self.x,captive.y-self.y)<80:
    self.notify('Dismount (H) before picking up the prisoner.',2);return
  if self.pick_up_bounty():return
  if self.progress_road_contract():return
  if self.complete_work_step():return
  if self.advance_side_job():return
  nearest=None;best=64
  for a in self.actors:
   if a.dead or a.kind.startswith('mission_') or a.kind in ('bandit','animal','deputy','law_patrol','bounty_target'):continue
   dist=math.hypot(a.x-self.x,a.y-self.y)
   if dist<best:nearest=a;best=dist
  # Plain E never enters a building; Shift+E owns that action.
  if nearest is None:
   if self.stage==4 and math.hypot(self.x-2040,self.y-1280)<95 and self.enemies_remaining('blackspur')==0:
    self.ledger=True;self.quest(5);self.say('JESSE',['Under a loose floorboard: the stolen manifest.','The pages name Crow as the man who bought the railroad robbery. Nell needs to see this.'])
   else:self.notify('Nobody nearby to talk to. Walk up to a character and press E.',2)
   return
  k=nearest.kind
  if k=='guide':self.offer_frontier_job(nearest);return
  if k=='station_agent':
   text=dispatch_rumor(nearest.x,nearest.y,self.economy_day)
   self.say('DISPATCHER',[text,'Press N at this outpost for a paid road assignment.','Bring passengers safely or recover lost cargo; your standing will improve.'])
   return
  if k in ('road_wagon','road_cache'):
   self.actors.remove(nearest)
   if k=='road_wagon':
    self.money+=14;self.change_honor(1,'Repaired a stranded wagon')
    self.say('WAGON DRIVER',['These axles were close to giving way. Thank you for stopping.','Take fourteen dollars for your trouble.'])
   else:
    self.reserve+=12;self.money+=6
    self.say('JESSE',['A supply crate left beside the trail. Twelve cartridges and six dollars.','Maybe someone will come looking for it.'])
   self.encounter_cooldown=75.;self.audio.cue('purchase');self.save();return
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
   elif self.law_reputation>=12:self.say('SHERIFF BELL',['The cells are filling because you have been bringing criminals in alive.','Keep the roads safe, Vale, and the town will remember.'])
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
   if self.horse_hp>=100:self.say('STABLEHAND',['Whiskey is already well fed and rested.','Press H while near your horse to mount.'])
   elif self.money>=5:
    self.money-=5;self.work_expenses+=5;self.horse_hp=100
    self.horse_x,self.horse_y=nearest.x+45,nearest.y+25
    self.say('STABLEHAND',['Five dollars for good feed and a fresh brushing. Whiskey is ready.'])
    self.audio.cue('horse');self.save()
   else:self.say('STABLEHAND',['Five dollars for full horse care. Come back when you can afford it.'])
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
  self.interior=name;self.indoor_x=480.;self.indoor_y=465.;self.shop_open=False;self.show_jail=False
  self.audio.cue('door')
  self.keys.clear();self.notify('Entered '+name+' — E at counter; E at south door to leave.',4)

 def leave_interior(self):
  if not self.interior:return
  name=self.interior
  self.interior=None;self.shop_open=False;self.show_jail=False;self.keys.clear()
  self.notify('Back outside '+name+'.',1.7)

 def update_indoor(self,dt):
  vx=int('d' in self.keys or 'right' in self.keys)-int('a' in self.keys or 'left' in self.keys)
  vy=int('s' in self.keys or 'down' in self.keys)-int('w' in self.keys or 'up' in self.keys)
  mag=math.hypot(vx,vy)
  if mag:
   self.indoor_x=max(225,min(735,self.indoor_x+vx/mag*165*dt))
   self.indoor_y=max(340,min(510,self.indoor_y+vy/mag*165*dt))
  self.advance_clock(dt*.020)

 def use_counter(self):
  kind=INTERIOR_TYPES.get(self.interior,'home')
  if kind in SHOP_GOODS:
   if kind=='office' and self.wanted<=0:
    self.say('DEPUTY',['No warrants out for you. Keep it that way.']);return
   self.shop_inventory()
   self.shop_open=True;self.keys.clear();return
  talks={'home':'The hearth is cold, but the roof still holds.',
         'chapel':'The frontier holds many sins, and few confessions.',
         'hideout':'Dusty supplies. Looks like the owners left in a hurry.'}
  self.say(self.interior.upper(),talks.get(kind,'Nothing here but frontier dust.'))

 def buy_item(self,index):
  kind=INTERIOR_TYPES.get(self.interior,'home')
  goods=SHOP_GOODS.get(kind,[])
  if index<0 or index>=len(goods):return
  label,_base,action=goods[index]
  stock=self.shop_inventory()
  if not stock or stock[index]<=0:
   self.notify('Sold out today. Stock returns tomorrow.',3);return
  cost=self.shop_cost(index)
  if self.money<cost:self.notify('Not enough money for '+label+'.');return
  if action=='heal' and self.hp>=100:self.notify('Already at full health.');return
  if action=='bounty' and self.wanted<=0:self.notify('No bounty to pay.');return
  self.money-=cost
  stock[index]-=1;self.work_expenses+=cost
  if action=='bounty':self.change_honor(2,'Settled a debt with the law')
  if action=='ammo':self.reserve+=30
  elif action=='tonic':self.tonics+=1
  elif action=='supplies':self.hp=min(100,self.hp+15)
  elif action=='meal':self.hp=min(100,self.hp+35)
  elif action=='coffee':self.advance_clock(2);self.update_npc_schedules()
  elif action=='heal':self.hp=100
  elif action=='horse':self.horse_hp=100
  elif action=='sleep':self.advance_clock(8);self.hp=min(100,self.hp+25);self.update_npc_schedules()
  elif action=='bounty':self.wanted=0;self.law_timer=0;self.law_status='PEACE';self.witness_timer=0
  self.notify('Purchased '+label+f' for ${cost}.',3)
  self.audio.cue('purchase');self.save()

 def change_honor(self,amount,reason=''):
  before=self.honor
  self.honor=max(0,min(100,self.honor+amount))
  if self.honor!=before and reason:self.notify(('HONOR + ' if amount>0 else 'HONOR - ')+str(abs(self.honor-before))+'  •  '+reason,2.3)

 def report_crime(self,severity,reason):
  # A crime witnessed near town escalates immediately; elsewhere it may take
  # longer to reach the law. Mission firefights against bandits are legal.
  self.crimes+=1
  self.law_reputation=max(0,self.law_reputation-max(1,int(severity*2)))
  region=region_at(self.x,self.y)
  self.regional_standing[region]=max(-100,self.regional_standing.get(region,0)-max(1,int(severity*3)))
  nearby=any(not a.dead and a.kind in ('civilian','sheriff','store','doctor','station','saloon','stable') and math.hypot(a.x-self.x,a.y-self.y)<310 for a in self.actors)
  witnessed=nearby or self.in_town(self.x,self.y)
  self.wanted=min(5.,self.wanted+severity*(1 if witnessed else .55))
  self.law_timer=max(self.law_timer,5. if witnessed else 2.)
  self.witness_timer=5. if witnessed else 0.
  self.law_status='WANTED' if self.wanted>=1.2 else 'INVESTIGATING'
  self.patrol_alert_timer=12. if witnessed else 5.
  if witnessed:self.notify('WITNESSES ALERTED: '+reason+' — deputies responding.',2.8)
  else:self.notify('CRIME REPORTED: '+reason,2.0)

 def update_law(self,dt):
  if self.wanted<=0:
   self.wanted=0.;self.law_status='PEACE';return
  self.patrol_alert_timer=max(0.,self.patrol_alert_timer-dt)
  self.law_timer=max(0.,self.law_timer-dt)
  self.witness_timer=max(0.,self.witness_timer-dt)
  if self.law_timer==0:
   rate=.008 if self.in_town(self.x,self.y) else .035
   if not any(a.kind in ('deputy','law_patrol') and not a.dead and math.hypot(a.x-self.x,a.y-self.y)<230 for a in self.actors):
    self.wanted=max(0,self.wanted-dt*rate)
  self.law_status='WANTED' if self.wanted>=1.2 else ('INVESTIGATING' if self.wanted>0 else 'PEACE')

 def draw_scattered_props(self):
  # Staggered, heavily jittered foliage and scree: no visible cell grid.
  cell=265
  left=int(self.camx//cell)-2;top=int(self.camy//cell)-2
  right=int((self.camx+VW)//cell)+3;bottom=int((self.camy+VH)//cell)+3
  for gy in range(top,bottom):
   for gx in range(left,right):
    h=hash32(gx+319,gy-67)
    if h%5>=3:continue
    wx=(gx+.5+(gy%2)*.3)*cell+(h%177)-88
    wy=(gy+.5)*cell+((h//177)%183)-91
    if not(0<wx<WW and 0<wy<WH):continue
    if noise(wx,wy,1800)<.32:continue
    if self.in_town(wx,wy) or self.is_frontier_road(wx,wy) or is_water(wx,wy):continue
    if any(bx-45<wx<bx+bw+45 and by-45<wy<by+bh+45 for _,bx,by,bw,bh in BUILDINGS):continue
    sx,sy=self.pos(wx,wy)
    if h%4==0:
     for off in (-7,0,8):self.canvas.create_line(sx+off,sy+6,sx+off-3,sy-6-(h%6),fill='#9f8658',width=2)
    elif h%4==1:
     self.canvas.create_oval(sx-13,sy-4,sx+12,sy+6,fill='#897c67',outline='#645b50')
    else:
     self.canvas.create_oval(sx-17,sy-9,sx+17,sy+7,fill='#6c7654',outline='#4b5943')
     self.canvas.create_line(sx-12,sy+2,sx+10,sy-6,fill='#9a9d70',width=2)

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
  town=nearby_settlement(*home,550)
  if town and a.name.endswith((' Courier',' Farmer',' Watcher')):
   center=get_settlement(town)
   cx,cy=center[2],center[3]
   role=a.name.rsplit(' ',1)[-1]
   shifts={'Courier':((80,120),(-80,95),(40,-90)),
           'Farmer':((-90,-160),(285,-115),(105,-130)),
           'Watcher':((-100,-130),(125,-45),(-80,-105))}
   morning,work,evening=shifts[role]
   offset={'morning':morning,'working':work,'evening':evening}.get(period)
   target=(cx+offset[0],cy+offset[1]) if offset else home
  else:target=routines.get(a.name,{}).get(period,home) if period!='night' else home
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
  if period=='working' and a.name.endswith(' Courier'):return 'delivering freight'
  if period=='working' and a.name.endswith(' Farmer'):return 'tending crops'
  if period=='working' and a.name.endswith(' Watcher'):return 'patrolling the road'
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
  if self.interior=='Sheriff':self.draw_jail_cells()
  c.create_oval(self.indoor_x-10,self.indoor_y+8,self.indoor_x+11,self.indoor_y+15,fill='#49372e',outline='')
  c.create_rectangle(self.indoor_x-9,self.indoor_y-9,self.indoor_x+9,self.indoor_y+10,fill='#35565b',outline='#172a2e',width=2)
  c.create_oval(self.indoor_x-8,self.indoor_y-20,self.indoor_x+8,self.indoor_y-7,fill='#d0a078',outline='')
  c.create_rectangle(self.indoor_x-14,self.indoor_y-20,self.indoor_x+14,self.indoor_y-16,fill='#5f3d2c',outline='')
  self.panel(200,18,560,70)
  self.draw_text(480,30,self.interior.upper(),21,'#f2d7a0',True,anchor='center')
  self.draw_text(480,60,'WASD WALK   E INTERACT   ESC EXIT'+('   K JAIL ROSTER' if self.interior=='Sheriff' else ''),11,'#debd86',anchor='center')
  if any(self.interior.startswith(name+' ') for _,name,*_ in SETTLEMENTS):
   town=next(name for _,name,*_ in SETTLEMENTS if self.interior.startswith(name+' '))
   self.canvas.create_rectangle(330,160,630,194,fill='#564332',outline='#d6b48a',width=3)
   self.draw_text(480,170,'WELCOME TO '+town.upper(),12,'#f0d4a4',True,anchor='center')
  if self.indoor_y<365:self.draw_text(480,330,'[ E ]  COUNTER',14,'#ffe5ac',True,anchor='center')
  if self.indoor_y>475:self.draw_text(480,550,'[ E ]  EXIT TO STREET',13,'#f3d79e',True,anchor='center')
  self.draw_text(18,562,f'HEALTH {int(self.hp)}   $ {self.money}   TONICS {self.tonics}   AMMO {self.ammo}/{self.reserve}',12,'#ecd0a0',True)
  for i,(msg,remaining) in enumerate(self.toast[-2:]):self.draw_text(480,104+i*23,msg,12,'#fff0c4',True,anchor='center')
  if self.show_jail and self.interior=='Sheriff':self.draw_jail_roster()

 def draw_jail_cells(self):
  # Visible cell occupants mirror the latest arrests; the full roster is on K.
  c=self.canvas
  occupants=self.jail_roster[-3:]
  for i in range(3):
   x=234+i*174;y=350
   c.create_rectangle(x,y,x+135,y+91,fill='#423f3c',outline='#27282b',width=4)
   if i<len(occupants):
    c.create_oval(x+58,y+25,x+76,y+45,fill='#b88a6b',outline='')
    c.create_rectangle(x+55,y+45,x+79,y+70,fill='#7b5946',outline='')
   for bar in range(5):
    bx=x+8+bar*29
    c.create_line(bx,y+4,bx,y+87,fill='#a49c86',width=5)
   c.create_text(x+68,y-13,text='CELL '+str(i+1),fill='#f1d9a8',font=(self.font,10,'bold'))

 def draw_jail_roster(self):
  self.panel(230,115,505,405,fill='#26231e')
  self.draw_text(480,132,'CINDER CREEK JAIL REGISTER',19,'#f0d39b',True,anchor='center')
  self.draw_text(254,175,'PRISONERS BOOKED: '+str(len(self.jail_roster))+
                 '     LAW REPUTATION: '+str(self.law_reputation),12,'#d9c293',True)
  latest=list(reversed(self.jail_roster[-10:]))
  if not latest:self.draw_text(480,280,'All cells are empty.',15,'#d5bd9a',anchor='center')
  for i,entry in enumerate(latest):
   label=entry.get('name','Unknown')+'   •   '+entry.get('case','Arrest')
   self.draw_text(253,212+i*24,label[:65],11,'#f3d8b1')
  self.draw_text(480,494,'K / E / ESC — CLOSE REGISTER',11,'#c7b393',True,anchor='center')

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
  self.draw_text(480,147,'TRADING COUNTER  •  DAY '+str(self.economy_day+1),20,'#ffe0a9',True,anchor='center')
  self.draw_text(232,191,f'YOUR MONEY: ${self.money}',14,'#f0c994',True)
  stock=self.shop_inventory()
  for i,(name,_base,action) in enumerate(goods):
   price=self.shop_cost(i)
   count=stock[i] if i<len(stock) else 0
   self.draw_text(232,239+i*53,f'{i+1}   {name}   [{count} left]',13,'#f7e1c2' if count else '#997e6e')
   self.draw_text(700,239+i*53,f'${price}' if count else 'SOLD OUT',13,'#d6ac76',True,anchor='e')
  self.draw_text(480,445,'PRESS NUMBER TO BUY    •    B / ESC TO CLOSE',12,'#f0d2a6',True,anchor='center')

 def toggle_horse(self):
  if self.mounted:
   self.mounted=False;self.horse_motion['speed']=0.
   self.horse_x=self.x+28;self.horse_y=self.y+10;self.notify('Dismounted Whiskey.')
  elif math.hypot(self.x-self.horse_x,self.y-self.horse_y)<75:
   self.deadeye_active=False
   self.mounted=True;self.horse_motion['speed']=0.
   self.notify('Mounted Whiskey. Hold Shift to gallop; stamina recovers at a trot.')
  else:self.notify('Get closer to Whiskey to mount (H).')
 def tonic(self):
  if self.tonics<=0:self.notify('No tonics left.');return
  if self.hp>=100:self.notify('Already at full health.');return
  self.tonics-=1;self.hp=min(100,self.hp+55);self.notify('Used a tonic: +55 health.');self.save()
 def switch_weapon(self):
  options=available_weapons(self.field_arrests,self.work_finished,self.kills)
  if len(options)<2:
   self.notify("Marshal's Iron unlocks with 2 arrests, 4 jobs or 10 outlaw defeats.",3);return
  if self.reload_timer>0:self.notify('Finish reloading before swapping revolvers.',2);return
  self.weapon='marshal' if self.weapon=='peacemaker' else 'peacemaker'
  self.ammo=min(self.ammo,WEAPONS[self.weapon]['capacity'])
  self.notify('EQUIPPED: '+WEAPONS[self.weapon]['label'],2)

 def reload(self):
  if self.reload_timer>0 or self.ammo>=WEAPONS[self.weapon]['capacity']:return
  if self.reserve<=0:self.notify('Out of ammunition. Visit the general store.');return
  self.reload_timer=WEAPONS[self.weapon]['reload'];self.notify('Reloading...',1.2);self.audio.cue('reload')
 def fire(self):
  if self.screen!='playing' or self.dialog or self.shot_timer>0 or self.reload_timer>0 or self.map_open or self.journal_open:return
  if self.ammo<=0:self.reload();return
  config=WEAPONS[self.weapon]
  self.ammo-=1;self.shot_timer=.17 if self.deadeye_active else config['cooldown']
  mx,my=self.mouse;dx=(mx+self.camx)-self.x;dy=(my+self.camy)-self.y
  if abs(dx)+abs(dy)<15:dx,dy=self.facing
  dx,dy=aim_vector(dx,dy,self.actors,self.x,self.y,self.aim_assist)
  self.facing=(dx,dy)
  self.bullets.append([self.x+dx*19,self.y+dy*19,dx*config['velocity'],dy*config['velocity'],1.0,True])
  self.effects.append([self.x+dx*22,self.y+dy*22,.14,'flash'])
  self.sound_cue('gunshot')
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
  self.frame+=1;self.advance_clock(dt*.032)
  if self.interior:self.audio.set_music_state('interior')
  elif self.combat_warning>0:self.audio.set_music_state('combat')
  elif self.clock>=20 or self.clock<5:self.audio.set_music_state('night')
  elif self.in_safe_settlement(self.x,self.y):self.audio.set_music_state('town')
  else:self.audio.set_music_state('wilderness')
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
  self.update_bounty_capture(dt)
  self.shot_timer=max(0,self.shot_timer-dt);self.invuln=max(0,self.invuln-dt)
  self.hit_marker=max(0,self.hit_marker-dt);self.combat_warning=max(0,self.combat_warning-dt)
  if self.reload_timer>0:
   self.reload_timer-=dt
   if self.reload_timer<=0:
    n=min(WEAPONS[self.weapon]['capacity']-self.ammo,self.reserve);self.ammo+=n;self.reserve-=n;self.notify('Revolver reloaded.',1.1)
  for toast in self.toast:toast[1]-=dt
  self.toast=[t for t in self.toast if t[1]>0]
  for trail in self.shot_trails:trail[4]-=dt
  self.shot_trails=[v for v in self.shot_trails if v[4]>0]
  for fx in self.effects:fx[2]-=dt
  self.effects=[a for a in self.effects if a[2]>0]
  vx=(int('d' in self.keys or 'right' in self.keys)-int('a' in self.keys or 'left' in self.keys))
  vy=(int('s' in self.keys or 'down' in self.keys)-int('w' in self.keys or 'up' in self.keys))
  wants_gallop='shift_l' in self.keys or 'shift_r' in self.keys
  if self.mounted:
   horse_vx,horse_vy,galloping=step_motion(self.horse_motion,vx,vy,dt,wants_gallop,self.horse_hp)
   distance=math.hypot(horse_vx,horse_vy)*dt
   slices=max(1,int(math.ceil(distance/10.)))
   # Substep the fast gallop so the horse cannot skip through buildings or rivers.
   for _ in range(slices):
    dx=horse_vx*dt/slices;dy=horse_vy*dt/slices
    moved=False
    if abs(dx)>.0001 and self.can_move(self.x+dx,self.y,16):self.x+=dx;moved=True
    if abs(dy)>.0001 and self.can_move(self.x,self.y+dy,16):self.y+=dy;moved=True
    if not moved and abs(dx)+abs(dy)>.01:
     self.horse_motion['speed']=0.
     break
   if vx or vy:self.facing=(horse_vx,horse_vy)
   self.horse_hp=max(0.,self.horse_hp-dt*.025)
  elif vx or vy:
   mag=math.hypot(vx,vy);vx/=mag;vy/=mag
   speed=175 if wants_gallop else 125
   if self.bounty_state()=='carried' or self.field_status()=='carried':speed*=.75
   if self.can_move(self.x+vx*speed*dt,self.y,10):self.x+=vx*speed*dt
   if self.can_move(self.x,self.y+vy*speed*dt,10):self.y+=vy*speed*dt
   self.facing=(vx,vy)
  if self.frame%60==0:self.update_npc_schedules()
  self.encounter_cooldown=max(0.,self.encounter_cooldown-dt)
  if self.road_contract:self.update_road_escort(world_dt)
  if self.encounter_cooldown<=0:
   if self.spawn_road_encounter():self.encounter_cooldown=random.uniform(75,115)
   else:self.encounter_cooldown=15.
  if self.frame%40==0:
   self.discover_settlement();self.discover_landmark()
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
  if self.hp<=0:
   self.screen='death';self.mounted=False
   if self.contract and self.bounty_state()=='carried':
    self.contract['status']='hunting';self.spawn_contract_target()
    self.notify('Your captive escaped after you fell.',4)
   if self.field_prisoner:
    captive=self.field_actor()
    if captive:captive.kind='bandit'
    self.field_prisoner=None
    self.notify('Your captured drifter escaped after you fell.',4)
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
  damage=WEAPONS[self.weapon]['damage']
  return int(round(damage*64/52)) if self.deadeye_active and (a.kind=='bandit' or a.kind.startswith('mission_')) else damage

 def update_patrol(self,a,dt):
  # Patrols follow bounded routes. They pursue only genuinely wanted players.
  distance=math.hypot(a.x-self.x,a.y-self.y)
  if self.law_status=='WANTED' and distance<430:
   dx=self.x-a.x;dy=self.y-a.y;norm=max(1.,distance)
   if distance>125:self.move_actor(a,dx/norm*a.speed*dt,dy/norm*a.speed*dt)
   if distance<320 and a.shoot<=0 and self.line_of_fire(a.x,a.y,self.x,self.y):
    a.shoot=2.8
    angle=math.atan2(dy,dx)+random.uniform(-.13,.13)
    self.combat_warning=.6
    self.bullets.append([a.x,a.y,math.cos(angle)*325,math.sin(angle)*325,1.2,False])
   return
  route=getattr(a,'route',())
  if not route:return
  index=getattr(a,'route_index',0)%len(route)
  target=route[index]
  dx=target[0]-a.x;dy=target[1]-a.y
  norm=math.hypot(dx,dy)
  if norm<21:a.route_index=(index+1)%len(route);return
  before=(a.x,a.y)
  self.move_actor(a,dx/norm*a.speed*dt,dy/norm*a.speed*dt)
  if math.hypot(a.x-before[0],a.y-before[1])<.01:
   a.stuck_time=getattr(a,'stuck_time',0.)+dt
   if a.stuck_time>2.5:
    a.route_index=(index+1)%len(route);a.stuck_time=0.
  else:a.stuck_time=0.

 def update_ai(self,dt):
  for a in self.actors:
   if a.dead:continue
   if a.kind=='field_prisoner':continue
   if a.kind=='bounty_target' and self.bounty_state() in ('roped','hogtied','carried','surrendered'):continue
   if a.kind in ('sheriff','store','doctor','stable','saloon','station','traveler'):continue
   dist=math.hypot(a.x-self.x,a.y-self.y)
   # Dormant distant actors avoid unnecessary pathfinding and collision checks.
   if dist>1200:continue
   a.shoot=max(0,a.shoot-dt);a.wander-=dt
   if a.kind=='law_patrol':self.update_patrol(a,dt);continue
   if a.kind in ('bandit','bounty_target') and dist<370 and self.check_surrender(a):continue
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
   deputies=sum(not a.dead and a.kind in ('deputy','law_patrol') and math.hypot(a.x-self.x,a.y-self.y)<720 for a in self.actors)
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
      if a.dead or a.kind=='field_prisoner' or a.kind=='animal' and a.name=='Jackrabbit' and random.random()<.12:continue
      if math.hypot(a.x-px,a.y-py)<(17 if a.name=='Crow' else 13):
       if a.kind in ('sheriff','law_patrol','store','doctor','stable','saloon','station'):
        self.report_crime(2,'Assault on a citizen');self.change_honor(-8,'Assault')
        a.hp-=32
       elif a.kind=='civilian':
        self.report_crime(2,'Assault on a citizen');self.change_honor(-8,'Assault');a.hp-=55
       else:a.hp-=self.combat_damage(a)
       if a.hp>0:self.check_surrender(a)
       self.effects.append([px,py,.30,'hit']);self.effects.append([px,py,.52,'spark']);self.hit_marker=.20;collided=True
       if a.hp<=0:
        a.dead=True
        if a.kind in ('bandit','deputy','bounty_target') or a.kind.startswith('mission_'):
         if a.kind=='deputy':self.report_crime(2.5,'Lawman killed');self.change_honor(-18,'Killed a lawman')
         elif a.kind=='bounty_target':self.finish_bounty(a)
         else:
          reward=8 if a.kind=='bandit' else 5
          self.money+=reward;self.kills+=1;self.deadeye=min(100.,self.deadeye+12);self.change_honor(1,'Outlaw defeated');self.notify('Outlaw down! +$'+str(reward),1.7)
        elif a.kind in ('civilian','sheriff','law_patrol','store','doctor','stable','saloon','station','traveler'):
         is_lawman=a.kind in ('sheriff','law_patrol')
         self.report_crime(5,'Murdered a lawman' if is_lawman else 'Murder')
         self.change_honor(-22 if is_lawman else -20,'Killed a lawman' if is_lawman else 'Killed a civilian')
         self.wanted=5.;self.law_status='WANTED';self.notify('MURDER! Wanted level maximum.')
       break
    else:
     if math.hypot(self.x-px,self.y-py)<(17 if self.mounted else 11):
      collided=True
      if self.invuln<=0:
       self.hp-=incoming_damage(self.difficulty,random.randrange(7,15));self.invuln=.50;self.effects.append([px,py,.35,'hit']);self.effects.append([px,py,.5,'spark'])
      break
    if collided:break
   if not collided and b[4]>0:kept.append(b)
  self.bullets=kept

 def draw_text(self,x,y,s,size=13,color='#ead8b3',bold=False,anchor='nw',shadow=True,width=None):
  font=(self.font,size,'bold' if bold else 'normal')
  if shadow:self.canvas.create_text(x+1,y+2,text=s,fill='#211912',font=font,anchor=anchor,width=width)
  self.canvas.create_text(x,y,text=s,fill=color,font=font,anchor=anchor,width=width)
 def panel(self,x,y,w,h,fill='#221c18',edge='#b68b54'):
  pulp.panel(self.canvas,x,y,w,h,fill,edge)
 def pos(self,x,y):return int(x-self.camx),int(y-self.camy)
 def draw_actor(self,a):
  sx,sy=self.pos(a.x,a.y)
  if sx< -40 or sy< -45 or sx>VW+40 or sy>VH+40:return
  if a.dead:
   self.canvas.create_oval(sx-12,sy-3,sx+13,sy+6,fill='#6e4b3c',outline='')
   self.canvas.create_line(sx-9,sy-4,sx+9,sy+5,fill='#44352e',width=5)
   return
  if a.kind in ('road_wagon','road_cache'):
   co='#986c49' if a.kind=='road_wagon' else '#a99a6f'
   self.canvas.create_rectangle(sx-23,sy-11,sx+23,sy+11,fill=co,outline='#584330',width=3)
   if a.kind=='road_wagon':
    for ox in (-17,17):self.canvas.create_oval(sx+ox-8,sy+5,sx+ox+8,sy+21,outline='#44392e',width=4)
   else:self.canvas.create_line(sx-20,sy-12,sx+21,sy+11,fill='#53432a',width=3)
   if math.hypot(a.x-self.x,a.y-self.y)<125:self.draw_text(sx,sy-36,'E: '+a.name.upper(),10,'#eeddab',True,anchor='center')
   return
  if a.kind=='animal':
   co='#aa8963' if a.name=='Coyote' else '#c4ae87'
   self.canvas.create_oval(sx-12,sy-6,sx+13,sy+6,fill=co,outline='#65523e')
   self.canvas.create_oval(sx+7,sy-9,sx+16,sy,fill=co,outline='#65523e')
   return
  villain=a.kind in ('bandit','deputy','bounty_target') or a.kind.startswith('mission_')
  clothes=('#3e4b59' if a.kind=='deputy' else '#694332') if villain else {'station_agent':'#596c60','escort':'#9a7a5a','law_patrol':'#3f5361','sheriff':'#384a4f','saloon':'#973f50','store':'#747143','doctor':'#e0d0a4','stable':'#55644a','station':'#526783'}.get(a.kind,'#73654f')
  pulp.person(self.canvas,sx,sy,clothes,
              '#342824' if villain else '#684732',
              sheriff=a.kind in ('sheriff','law_patrol'))
  if a.name=='Crow':
   self.canvas.create_rectangle(sx-11,sy-10,sx+11,sy+8,outline='#b44538',width=2)
  if villain and a.hp<a.maxhp:
   self.canvas.create_rectangle(sx-16,sy-34,sx+16,sy-30,fill='#3d201c',outline='')
   self.canvas.create_rectangle(sx-16,sy-34,sx-16+32*max(0,a.hp)/a.maxhp,sy-30,fill='#b84f40',outline='')
  if (a.kind=='bounty_target' and self.bounty_state() in ('roped','hogtied','surrendered')) or (a.kind=='field_prisoner' and self.field_status() in ('roped','hogtied','surrendered')):
   self.canvas.create_oval(sx-14,sy-13,sx+14,sy+14,outline='#e5cb94',width=3)
   self.canvas.create_line(sx-12,sy+5,sx+12,sy+5,fill='#e5cb94',width=3)
   bound=self.field_status() if a.kind=='field_prisoner' else self.bounty_state()
   if bound=='hogtied':
    self.canvas.create_line(sx-11,sy+12,sx+12,sy-6,fill='#e5cb94',width=4)
   self.draw_text(sx,sy-47,'HOGTIED' if bound=='hogtied' else 'SURRENDERED — G' if bound=='surrendered' else 'ROPED — G',10,'#f7deb0',True,anchor='center')
  if math.hypot(a.x-self.x,a.y-self.y)<125 and not villain:
   self.draw_text(sx,sy-43,a.name,11,'#f3db9e',True,anchor='center')
   if a.kind=='civilian':self.draw_text(sx,sy-56,self.npc_activity(a),9,'#d3c49e',anchor='center')

 def draw_player(self):
  sx,sy=self.pos(self.x,self.y)
  if not self.mounted:
   hx,hy=self.pos(self.horse_x,self.horse_y)
   if -60<hx<VW+60 and -60<hy<VH+60:self.draw_horse(hx,hy)
  else:self.draw_horse(sx,sy+9)
  pulp.person(self.canvas,sx,sy,'#344e50','#5d3e2c',
              facing=self.facing,mounted=self.mounted)
  if self.bounty_state()=='carried' or self.field_status()=='carried':
   cx,cy=sx+18,sy+(5 if self.mounted else 12)
   self.canvas.create_oval(cx-9,cy-9,cx+10,cy+9,fill='#6b4e3d',outline='#e6c88e',width=3)
   self.canvas.create_line(cx-9,cy-3,cx+8,cy+6,fill='#e6c88e',width=3)
  if self.invuln>0:self.canvas.create_oval(sx-23,sy-30,sx+23,sy+20,outline='#eead90',width=2)
 def draw_horse(self,sx,sy):
  pulp.horse(self.canvas,sx,sy)

 def terrain_patch(self,tx,ty):
  value=(tx*73856093 ^ ty*19349663 ^ 0xA53B7C19)&0xffffffff
  value=(value^(value>>13))*1274126177&0xffffffff
  return value^(value>>16)

 def is_frontier_road(self,x,y):
  return road_at(x,y)

 def terrain_obstacle(self,x,y):
  # Collision for new natural cover is handled by landform_solid in solid().
  return None

 def draw_far_terrain(self):
  # Organic, deterministic landforms replace the old square terrain tile grid.
  c=self.canvas
  draw_ground(c,self.camx,self.camy,VW,VH)
  draw_landforms(c,self.camx,self.camy,VW,VH)
  # The starting region connects to the first new trade-route crossroads.
  (x1,y1),(x2,y2)=START_SPUR
  if self.camx-80<x2 and self.camy-80<y2 and self.camx+VW+80>x1 and self.camy+VH+80>y1:
   c.create_line(x1-self.camx,y1-self.camy,x2-self.camx,y2-self.camy,fill='#b9a276',width=38)
   c.create_line(x1-self.camx,y1-self.camy,x2-self.camx,y2-self.camy,fill='#d3b789',width=2,dash=(12,16))

 def draw_expansion_markers(self):
  # Camera-local sprites for gatherable items, campfires, and side-job clues.
  c=self.canvas
  for key,name,cx,cy,*_ in SETTLEMENTS:
   if abs(cx-self.x)>1100 or abs(cy-self.y)>900:continue
   sx,sy=self.pos(cx-120,cy+30)
   if -20<sx<VW+20 and -20<sy<VH+20:
    c.create_oval(sx-18,sy+6,sx+18,sy+15,fill='#544237',outline='')
    c.create_polygon(sx-12,sy+5,sx,sy-22,sx+12,sy+5,fill='#f5ac51',outline='#9e4b26')
    c.create_polygon(sx-5,sy+5,sx+2,sy-12,sx+7,sy+5,fill='#e8d17a',outline='')
    c.create_line(sx-15,sy+12,sx+14,sy+8,fill='#5d402b',width=4)
  for identifier,wx,wy,label,kind in RESOURCE_NODES:
   if identifier in self.gathered_nodes:continue
   sx,sy=self.pos(wx,wy)
   if not (-32<sx<VW+32 and -32<sy<VH+32):continue
   color='#5b8b51' if kind=='tonic' else '#bd9b65'
   c.create_oval(sx-10,sy-8,sx+10,sy+7,fill=color,outline='#3f4935',width=2)
   if kind=='tonic':
    c.create_line(sx,sy-16,sx,sy+8,fill='#426948',width=3)
    c.create_line(sx-9,sy-7,sx+9,sy-7,fill='#81b875',width=2)
   else:
    c.create_polygon(sx-12,sy+4,sx,sy-17,sx+14,sy+5,fill='#a8a09b',outline='#58493c',width=2)
   if math.hypot(wx-self.x,wy-self.y)<145:
    self.draw_text(sx,sy-30,label.upper(),10,'#f9e2a3',True,anchor='center')
  if self.side_job:
   job=get_job(self.side_job.get('id'))
   if job:
    step=int(self.side_job.get('step',0))
    if 0<=step<len(job[4]):
     wx,wy=job[4][step];sx,sy=self.pos(wx,wy)
     if -40<sx<VW+40 and -40<sy<VH+40:
      c.create_rectangle(sx-15,sy-9,sx+15,sy+9,fill='#8f7653',outline='#30271e',width=3)
      c.create_line(sx-13,sy-8,sx+13,sy+8,fill='#c1a475',width=2)
      c.create_oval(sx-7,sy-23,sx+7,sy-9,fill='#4caaa2',outline='#244e4a',width=2)
      self.draw_text(sx,sy-41,'SIDE JOB CLUE',10,'#a8e3d8',True,anchor='center')

 def draw_road_contract_marker(self):
  job=self.road_contract
  if not job:return
  wx,wy=job['target_pos'] if job['status']=='outbound' else job['origin_pos']
  sx,sy=self.pos(wx,wy)
  if not(-55<sx<VW+55 and -55<sy<VH+55):return
  self.canvas.create_oval(sx-28,sy-13,sx+28,sy+12,outline='#c7d9a8',width=3)
  self.canvas.create_rectangle(sx-12,sy-13,sx+12,sy+6,fill='#8b7252',outline='#463b2a',width=3)
  self.canvas.create_line(sx-9,sy-8,sx+10,sy+3,fill='#d1bd92',width=2)
  label='ROAD JOB: E' if job['status']=='outbound' else 'RETURN: N'
  self.draw_text(sx,sy-36,label,11,'#e4f1c3',True,anchor='center')

 def draw_work_marker(self):
  if not self.work_active:return
  job=self.work_active
  wx,wy=job['destination'] if job['status']=='outbound' else job['giver_pos']
  sx,sy=self.pos(wx,wy)
  if not (-45<sx<VW+45 and -45<sy<VH+45):return
  self.canvas.create_oval(sx-17,sy-17,sx+17,sy+17,outline='#90c9dc',width=3)
  self.canvas.create_line(sx-10,sy,sx+10,sy,fill='#e3f1e7',width=3)
  self.canvas.create_line(sx,sy-10,sx,sy+10,fill='#e3f1e7',width=3)
  self.draw_text(sx,sy-38,'WORK — E' if job['status']=='outbound' else 'RETURN — P',10,'#d7edf5',True,anchor='center')

 def draw_world(self):
  self.draw_far_terrain()
  draw_local_geography(self.canvas,self.camx,self.camy,VW,VH)
  if self.camx<OLD_WW and self.camy<OLD_WH:
   self.canvas.create_image(-self.camx,-self.camy,image=self.world,anchor='nw')
   draw_starting_transition(self.canvas,self.camx,self.camy,VW,VH,OLD_WW,OLD_WH)
  draw_frontier_towns(self.canvas,self.camx,self.camy,VW,VH)
  draw_landmark(self.canvas,self.camx,self.camy,VW,VH)
  draw_waystations(self.canvas,self.camx,self.camy,VW,VH)
  self.draw_expansion_markers()
  self.draw_work_marker()
  self.draw_road_contract_marker()
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
  if self.lasso_visual:
   fx,fy,tx,ty,_time=self.lasso_visual
   sx,sy=self.pos(fx,fy);ex,ey=self.pos(tx,ty)
   self.canvas.create_line(sx,sy,ex,ey,fill='#e7d2a3',width=3,dash=(9,4))
   self.canvas.create_oval(ex-11,ey-10,ex+11,ey+10,outline='#e7d2a3',width=3)
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
  if kind=='dust':
   # Distinct gusts rather than a full-screen yellow Dead Eye-like wash.
   for i in range(12):
    px=(i*109+self.frame*3)%VW;py=(i*71+self.frame)%VH
    c.create_line(px-30,py,px+30,py-5,fill='#bba47c',width=2)

 def draw_hud(self):
  self.panel(13,13,307,86)
  self.draw_text(25,21,'JESSE VALE',15,'#f0d39b',True)
  self.canvas.create_rectangle(25,49,209,66,fill='#3b2222',outline='#91684b')
  self.canvas.create_rectangle(27,51,27+180*max(0,self.hp)/100,64,fill='#a74c40',outline='')
  self.draw_text(218,50,f'{max(0,int(self.hp))} HP',11,'#e7d3b5',True)
  self.draw_text(26,73,f'$ {self.money}   HONOR {self.honor}   TONICS {self.tonics}',10,'#edc995',True)
  self.panel(333,13,285,86)
  self.draw_text(345,21,WEAPONS[self.weapon]['label'],11,'#e3c18c',True)
  self.draw_text(345,42,f'{self.ammo} / {self.reserve}',22,'#f2e0bd',True)
  if self.reload_timer>0:self.draw_text(445,46,'RELOADING',12,'#e9a268',True)
  self.canvas.create_rectangle(346,75,596,83,fill='#4d3827',outline='#8b7550')
  self.canvas.create_rectangle(347,76,347+248*self.deadeye/100,82,fill='#e3c078',outline='')
  self.draw_text(505,60,'Q: DEAD EYE' if not self.deadeye_active else 'DEAD EYE ACTIVE',10,'#e9d5a4',True)
  self.draw_text(346,88,'2: WEAPON  F6: '+self.difficulty.upper()+'  F7: AIM '+('ON' if self.aim_assist else 'OFF'),9,'#c9b49a')
  self.panel(631,13,315,86)
  hours=int(self.clock);mins=int((self.clock-hours)*60)
  self.draw_text(642,20,f'{hours%12 or 12}:{mins:02d} {"AM" if hours<12 else "PM"}  |  {self.region_name(self.x,self.y).upper()}',11,'#e2c48f',True)
  stars='★'*min(5,math.ceil(self.wanted))
  self.draw_text(642,43,self.law_status+' '+(stars if stars else '—'),15,'#e7a16b' if stars else '#b9a78b',True)
  self.draw_text(642,69,'H: HORSE   L: LASSO   G: TIE',10,'#e9d6b2')
  if self.mounted:
   label='GALLOP' if 'shift_l' in self.keys or 'shift_r' in self.keys else 'TROT'
   self.draw_text(642,84,'WHISKEY '+label+' • STAMINA '+str(int(self.horse_motion['stamina']))+'%',9,'#d3e8b0')
  else:self.draw_text(642,84,'WEATHER: '+self.weather_kind().upper()+'   F5: SAVE',9,'#ead9b1')
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
  if self.side_job:
   job=get_job(self.side_job['id'])
   if job:
    step=min(int(self.side_job['step']),len(job[4])-1)
    tx,ty=job[4][step]
    distance=int(math.hypot(tx-self.x,ty-self.y))
    self.draw_text(575,534,'SIDE JOB: '+job[2][:20]+f' ({distance}m)',10,'#f0d39b',True)
  if self.work_active:
   self.draw_text(572,514,'WORK: '+self.work_active['title'][:22],10,'#b8dce2',True)
  if self.road_contract:
   job=self.road_contract
   self.draw_text(571,495,'ROAD: '+job['title'][:19]+' ('+job['status']+')',10,'#c1d9a0',True)
  if self.chapter_active:
   chapter=CHAPTER_BY_ID[self.chapter_active['id']];node=self.chapter_node()
   self.draw_text(571,479,'STORY: '+chapter['title'][:17]+' → '+node['town_name'][:13],10,'#efe3c5',True)
  if self.waypoint:
   dx=self.waypoint[0]-self.x;dy=self.waypoint[1]-self.y
   self.draw_text(572,558,f'PIN {int(math.hypot(dx,dy))} m / {self.cardinal(math.atan2(dy,dx))}',11,'#f6d68d',True)
  for i,(s,t) in enumerate(self.toast[-3:]):
   self.draw_text(480,114+i*23,s,13,'#ffe7a8',True,anchor='center')
  nearest=None;dist=65
  for a in self.actors:
   if a.dead or a.kind.startswith('mission_') or a.kind in ('bandit','deputy','law_patrol','animal','bounty_target'):continue
   q=math.hypot(a.x-self.x,a.y-self.y)
   if q<dist:nearest=a;dist=q
  if nearest and not self.dialog and not self.choice_dialog:self.draw_text(480,474,'[ E ]  TALK TO '+nearest.name.upper(),14,'#fff0c4',True,anchor='center')
  provider=self.work_provider() if not self.mounted else None
  if provider:
   label='[ P ] COLLECT WORK PAY' if self.work_active and self.work_active['giver']==provider.name and self.work_active['status']=='return' else '[ P ] ASK FOR WORK'
   self.draw_text(480,380,label,11,'#b7dfe9',True,anchor='center')
  if self.work_active and self.work_active['status']=='outbound' and not self.mounted:
   wx,wy=self.work_active['destination']
   if math.hypot(wx-self.x,wy-self.y)<95:self.draw_text(480,402,'[ E ] COMPLETE WORK TASK',12,'#c2e7ea',True,anchor='center')
  station=nearby_station(self.x,self.y,220)
  if station:
   label='[ N ] CLAIM ROAD PAY' if self.road_contract and self.road_contract['status']=='return' and self.road_contract['origin']==station[0] else '[ N ] ROAD JOB'
   self.draw_text(480,361,label+'   [ U ] RUMOR',11,'#b8e4bb',True,anchor='center')
  if self.road_contract and not self.mounted:
   job=self.road_contract
   if job['status']=='outbound' and math.hypot(self.x-job['target_pos'][0],self.y-job['target_pos'][1])<155:
    self.draw_text(480,405,'[ E ] DELIVER / INSPECT',12,'#d4eab3',True,anchor='center')
  if self.near_bounty_board():
   label='[ E ] TURN IN PRISONER' if (self.bounty_state()=='carried' or self.field_status()=='carried') else '[ B ] BOUNTY BOARD'
   self.draw_text(480,427,label,12,'#f0d28a',True,anchor='center')
  if self.contract or self.field_prisoner:
   captive=self.field_actor() if self.field_prisoner else self.bounty_actor()
   state=self.field_status() if self.field_prisoner else self.bounty_state()
   if state in ('roped','surrendered') and captive and math.hypot(self.x-captive.x,self.y-captive.y)<120:
    self.draw_text(480,406,'[ G ] HOGTIE OUTLAW',12,'#ffe3ae',True,anchor='center')
   elif state=='hogtied' and captive and math.hypot(self.x-captive.x,self.y-captive.y)<110:
    self.draw_text(480,406,'[ E ] PICK UP PRISONER',12,'#ffe3ae',True,anchor='center')
   elif state=='hunting' and captive and math.hypot(self.x-captive.x,self.y-captive.y)<280:
    self.draw_text(480,406,'[ L ] LASSO TARGET (AIM WITH MOUSE)',11,'#ffe3ae',True,anchor='center')
  if self.side_job:
   job=get_job(self.side_job['id'])
   if job and int(self.side_job['step'])<len(job[4]):
    tx,ty=job[4][int(self.side_job['step'])]
    if math.hypot(self.x-tx,self.y-ty)<85:self.draw_text(480,400,'[ E ]  COLLECT QUEST CLUE',13,'#f9e2a5',True,anchor='center')
  chapter_node=self.chapter_node()
  if chapter_node and math.hypot(self.x-chapter_node['x'],self.y-chapter_node['y'])<320:
   self.draw_text(480,345,'[ Y ] INVESTIGATE '+chapter_node['town_name'].upper(),12,'#f7e7c0',True,anchor='center')
  elif not self.chapter_active and available_chapter(self.x,self.y,self.chapter_completed):
   self.draw_text(480,345,'[ Y ] BEGIN REGIONAL STORY',12,'#f7e7c0',True,anchor='center')
  if nearby_settlement(self.x,self.y,220) or near_waystation(self.x,self.y,220):
   self.draw_text(480,380,'[ T ] REST AT CAMP',12,'#f0d39b',True,anchor='center')
  for _id,nx,ny,label,kind in RESOURCE_NODES:
   if _id not in self.gathered_nodes and math.hypot(nx-self.x,ny-self.y)<90:
    self.draw_text(480,411,'[ F ]  GATHER '+label.upper(),12,'#e1efb3',True,anchor='center');break
  door=self.near_door()
  if door:self.draw_text(480,451,'[ SHIFT+E ] ENTER '+door.upper(),14,'#ffebb7',True,anchor='center')
  if not self.mounted and math.hypot(self.x-self.horse_x,self.y-self.horse_y)<75:self.draw_text(480,448,'[ H ]  MOUNT WHISKEY',13,'#e3d29e',True,anchor='center')

 def region_name(self,x,y):
  new_town=nearby_settlement(x,y,440)
  if new_town:return get_settlement(new_town)[1]
  if x>=OLD_WW or y>=OLD_WH:
   station=near_waystation(x,y,290)
   if station:return waystation_by_key(station)[1]
   landmark=near_landmark(x,y,335)
   if landmark:return landmark_by_key(landmark)[1]
   return region_at(x,y)
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
  # Local radar scale instead of compressing a 60,000x40,960 world to 187 pixels.
  self.panel(x,y,w,h,'#3d3328','#987b54')
  self.draw_text(x+12,y+8,'LOCAL TRAIL MAP',11,'#edd3a5',True)
  window_w=6400.;window_h=5600.
  ox=max(0.,min(WW-window_w,self.x-window_w/2))
  oy=max(0.,min(WH-window_h,self.y-window_h/2))
  left=x+10;top=y+27;mw=w-20;mh=h-38
  sx=mw/window_w;sy=mh/window_h
  def mp(wx,wy):
   if not(ox<=wx<=ox+window_w and oy<=wy<=oy+window_h):return None
   return (left+(wx-ox)*sx,top+(wy-oy)*sy)
  for gx in ROAD_X:
   if ox<=gx<=ox+window_w:
    xx=left+(gx-ox)*sx
    self.canvas.create_line(xx,top,xx,top+mh,fill='#ad976c',width=2)
  for gy in ROAD_Y:
   if oy<=gy<=oy+window_h:
    yy=top+(gy-oy)*sy
    self.canvas.create_line(left,yy,left+mw,yy,fill='#ad976c',width=2)
  for n,bx,by,bw,bh in BUILDINGS:
   p=mp(bx+bw/2,by+bh/2)
   if p:self.canvas.create_rectangle(p[0]-2,p[1]-2,p[0]+2,p[1]+2,fill='#bba77e',outline='')
  for key,name,cx,cy,*_ in SETTLEMENTS:
   p=mp(cx,cy)
   if p:self.canvas.create_oval(p[0]-4,p[1]-4,p[0]+4,p[1]+4,fill='#b7c894',outline='#44563a')
  for key,name,cx,cy in WAYSTATIONS:
   p=mp(cx,cy)
   if p:self.canvas.create_rectangle(p[0]-4,p[1]-4,p[0]+4,p[1]+4,fill='#70b3a1',outline='')
  for key,name,cx,cy,kind in LANDMARKS:
   p=mp(cx,cy)
   if p:self.canvas.create_oval(p[0]-3,p[1]-3,p[0]+3,p[1]+3,fill='#b67c4d' if key in self.landmarks_found else '#71695c',outline='')
  for a in self.actors:
   if not a.dead and (a.kind=='bandit' or a.kind.startswith('mission_')):
    p=mp(a.x,a.y)
    if p:self.canvas.create_oval(p[0]-2,p[1]-2,p[0]+2,p[1]+2,fill='#d77b56',outline='')
  target=self.quest_target()
  if target:
   p=mp(*target)
   if p:self.canvas.create_oval(p[0]-5,p[1]-5,p[0]+5,p[1]+5,outline='#f5df91',width=2)
  if self.waypoint:
   p=mp(*self.waypoint)
   if p:
    self.canvas.create_line(p[0]-5,p[1],p[0]+5,p[1],fill='#8ce0c4',width=2)
    self.canvas.create_line(p[0],p[1]-5,p[0],p[1]+5,fill='#8ce0c4',width=2)
  p=mp(self.x,self.y)
  if p:self.canvas.create_oval(p[0]-4,p[1]-4,p[0]+4,p[1]+4,fill='#f1e8c6',outline='#2d322b')
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
  self.panel(106,37,748,547,'#26211b')
  self.draw_text(145,59,'NEW AUSTELLIA — 1898',21,'#ebca95',True)
  mode='REGIONAL' if self.map_zoom else 'WHOLE TERRITORY'
  self.draw_text(805,78,mode,11,'#e4c797',True,anchor='e')
  view=self.current_map_view()
  if not self.map_zoom and self.austellia_image:
   x,y,w,h=MAP_RECT
   self.canvas.create_image(x,y,image=self.austellia_image,anchor='nw')
   self.canvas.create_rectangle(x,y,x+w,y+h,outline='#6d5136',width=3)
  else:draw_map_background(self.canvas,view)
  def mark(wx,wy):
   return point_on_map(wx,wy,view)
  for key,name,cx,cy,*_ in SETTLEMENTS:
   p=mark(cx,cy)
   if not p:continue
   sx,sy=p
   self.canvas.create_rectangle(sx-4,sy-4,sx+4,sy+4,fill='#516f4e',outline='#dddeab')
   if self.map_zoom:self.draw_text(sx+7,sy-9,name.upper(),8,'#322a1f',True)
  for name,tx,ty in (('CINDER CREEK',660,600),('SAGEBRUSH',3340,1920)):
   p=mark(tx,ty)
   if p:
    sx,sy=p
    self.canvas.create_rectangle(sx-4,sy-4,sx+4,sy+4,fill='#4e7060',outline='#f7dfaa')
    if self.map_zoom:self.draw_text(sx+7,sy,name,8,'#342a20',True)
  for key,name,tx,ty in WAYSTATIONS:
   p=mark(tx,ty)
   if p:
    sx,sy=p
    self.canvas.create_rectangle(sx-3,sy-3,sx+3,sy+3,fill='#52726d',outline='#e1d8a2')
    if self.map_zoom:self.draw_text(sx+7,sy+5,name.upper(),8,'#3f3025',True)
  for key,name,tx,ty,kind in LANDMARKS:
   p=mark(tx,ty)
   if not p:continue
   sx,sy=p
   found=key in self.landmarks_found
   self.canvas.create_oval(sx-3,sy-3,sx+3,sy+3,fill='#b16c3f' if found else '#756b5a',outline='#f5ddaf' if found else '')
   if found and self.map_zoom:self.draw_text(sx+7,sy-12,name.upper(),8,'#3f3025',True)
  if self.map_zoom:
   for n,bx,by,bw,bh in BUILDINGS:
    p=mark(bx+bw/2,by+bh/2)
    if p:self.canvas.create_rectangle(p[0]-2,p[1]-2,p[0]+2,p[1]+2,fill='#69543e',outline='')
   for node_id,nx,ny,label,kind in RESOURCE_NODES:
    if node_id not in self.gathered_nodes:
     p=mark(nx,ny)
     if p:self.canvas.create_oval(p[0]-2,p[1]-2,p[0]+2,p[1]+2,fill='#37804b',outline='')
  if self.side_job:
   job=get_job(self.side_job['id'])
   if job:
    step=int(self.side_job['step'])
    if 0<=step<len(job[4]):
     p=mark(*job[4][step])
     if p:self.canvas.create_oval(p[0]-6,p[1]-6,p[0]+6,p[1]+6,outline='#178982',width=3)
  if self.work_active:
   job=self.work_active
   p=mark(*(job['destination'] if job['status']=='outbound' else job['giver_pos']))
   if p:self.canvas.create_oval(p[0]-6,p[1]-6,p[0]+6,p[1]+6,outline='#3288aa',width=3)
  if self.chapter_active:
   target=self.chapter_target()
   p=mark(*target) if target else None
   if p:
    self.canvas.create_oval(p[0]-8,p[1]-8,p[0]+8,p[1]+8,outline='#eee7d4',width=3)
  if self.road_contract:
   job=self.road_contract
   marker=job['target_pos'] if job['status']=='outbound' else job['origin_pos']
   p=mark(*marker)
   if p:
    self.canvas.create_rectangle(p[0]-7,p[1]-7,p[0]+7,p[1]+7,outline='#5c8357',width=3)
    if self.map_zoom:self.draw_text(p[0]+10,p[1]-9,job['title'].upper(),8,'#423728',True)
  target=self.quest_target()
  if target:
   p=mark(*target)
   if p:self.canvas.create_oval(p[0]-6,p[1]-6,p[0]+6,p[1]+6,outline='#fff0a3',width=3)
  if self.contract or self.field_prisoner:
   if self.bounty_state()=='carried' or self.field_status()=='carried':target=(418,463)
   else:
    actor=self.field_actor() if self.field_prisoner else self.bounty_actor()
    fallback=self.field_prisoner['position'] if self.field_prisoner else self.contract['location']
    target=(actor.x,actor.y) if actor else fallback
   p=mark(*target)
   if p:self.canvas.create_oval(p[0]-6,p[1]-6,p[0]+6,p[1]+6,fill='#9d3d34',outline='#f3dbc0',width=2)
  if self.waypoint:
   p=mark(*self.waypoint)
   if p:
    sx,sy=p
    self.canvas.create_line(sx-9,sy,sx+9,sy,fill='#157661',width=3)
    self.canvas.create_line(sx,sy-9,sx,sy+9,fill='#157661',width=3)
  p=mark(self.x,self.y)
  if p:self.canvas.create_oval(p[0]-6,p[1]-6,p[0]+6,p[1]+6,fill='#d94530',outline='#fff8d7',width=2)
  _key,_name,_px,_py=MAP_DESTINATIONS[self.map_destination_index]
  self.draw_text(184,88,'TAB: '+_name[:42]+'  •  ENTER: PIN',10,'#e4d6a9',True)
  # Compact cartographic legend; overlay avoids adding a huge atlas texture.
  self.canvas.create_rectangle(597,109,778,177,fill='#e0cfaa',outline='#70563d',width=2)
  self.draw_text(606,115,'MAP LEGEND',9,'#4c3929',True)
  for px,py,color,label in ((606,133,'#d94530','YOU'),(681,133,'#516f4e','TOWN'),
                            (606,153,'#eee7d4','STORY'),(681,153,'#3288aa','JOB')):
   self.canvas.create_oval(px,py,px+7,py+7,fill=color,outline='#61513e')
   self.draw_text(px+11,py-2,label,9,'#4c3929',True)
  self.draw_text(480,570,'CLICK PIN • Z ZOOM • WASD PAN • TAB DESTINATIONS • M CLOSE',10,'#e2c397',anchor='center')

 def draw_journal(self):
  self.panel(132,59,700,485)
  self.draw_text(160,81,'THE OUTLAW JOURNAL',27,'#e8c28b',True)
  self.draw_text(160,144,'CURRENT JOB',12,'#b89c70',True)
  self.draw_text(160,169,MISSIONS[self.stage][0],21,'#f0dcad',True)
  self.draw_text(160,210,MISSIONS[self.stage][1],15,'#e9d7b7',width=630)
  self.canvas.create_line(160,280,801,280,fill='#8d744e',width=2)
  self.draw_text(160,305,'YOUR RECORD',12,'#b89c70',True)
  self.draw_text(160,340,f'Outlaws defeated: {self.kills}       Money: ${self.money}    Paid jobs: {self.work_finished}',14,'#f1dfbd')
  self.draw_text(160,382,f'Honor: {self.honor}/100   Law: {self.law_status}   Crimes: {self.crimes}   Booked: {len(self.jail_roster)}',13,'#f1dfbd')
  self.draw_text(160,424,f'Missions finished: {min(4,self.stage//2)} / 4       Story: {"COMPLETE" if self.stage==8 else "IN PROGRESS"}',15,'#f1dfbd')
  if self.contract:
   dead=int(self.contract['reward']);alive=int(self.contract.get('alive_reward',dead*2))
   title='BOUNTY: '+self.contract['name']+'  DEAD $'+str(dead)+' / ALIVE $'+str(alive)
   self.draw_text(160,457,title,11,'#f0ce92',True)
   self.draw_text(160,472,'STATUS: '+self.bounty_state().upper()+' • L rope, G tie, E carry/turn in',10,'#edcf9d')
  else:self.draw_text(160,459,'Bounties completed: '+str(self.bounties_done)+' — Press B near sheriff',12,'#f0ce92',True)
  self.draw_text(160,482,'DRIFTERS ARRESTED: '+str(self.field_arrests)+((' • PRISONER: '+self.field_status().upper()) if self.field_prisoner else ' • $24 alive each'),10,'#b2dbce',True)
  if self.side_job:
   job=get_job(self.side_job['id'])
   if job:self.draw_text(160,499,'SIDE JOB: '+job[2]+f' ({int(self.side_job["step"])+1}/{len(job[4])})',10,'#b2dbce',True)
  else:self.draw_text(160,499,f'Side jobs: {len(self.side_completed)}/{len(SIDE_JOBS)}    Towns found: {len(self.visited_settlements)}/{len(SETTLEMENTS)}',10,'#b2dbce',True)
  if self.chapter_active:
   chapter=CHAPTER_BY_ID[self.chapter_active['id']];node=self.chapter_node()
   self.draw_text(160,520,'REGIONAL: '+chapter['title']+' — '+node['town_name'],10,'#f0d6ad',True)
  else:self.draw_text(160,520,'REGIONAL STORIES: '+str(len(self.chapter_completed))+'/'+str(len(CHAPTERS))+' COMPLETE',10,'#f0d6ad')
  self.draw_text(480,536,'J CLOSE   •   I WORK LEDGER',11,'#e2bb7e',True,anchor='center')

 def draw_work_ledger(self):
  self.panel(130,70,700,465,fill='#24201b')
  self.draw_text(480,98,'WORKING FRONTIER — LEDGER',24,'#efcc94',True,anchor='center')
  self.draw_text(158,152,'Day '+str(self.economy_day+1)+'   Jobs finished: '+str(self.work_finished),15,'#ead6b3',True)
  self.draw_text(158,193,'Wages earned: $'+str(self.work_income)+'    Purchases and services: $'+str(self.work_expenses),14,'#e2c5a1')
  self.draw_text(158,230,'Whiskey condition: '+str(int(self.horse_hp))+'/100   Gallop stamina: '+str(int(self.horse_motion['stamina']))+'   Law reputation: '+str(self.law_reputation),12,'#d9bca0')
  self.draw_text(158,255,'Road jobs: '+str(self.road_contracts_done)+'   Road wages: $'+str(self.road_income)+'   Region standing: '+str(self.regional_standing.get(region_at(self.x,self.y),0)),12,'#c7d8ae')
  if self.work_active:
   job=self.work_active
   self.draw_text(158,285,'CURRENT WORK: '+job['title'],16,'#b9e5ee',True)
   instruction='Go to the blue map marker; press E on foot.' if job['status']=='outbound' else 'Return to '+job['giver']+' and press P.'
   self.draw_text(158,320,instruction,13,'#e9d3b5')
   self.draw_text(158,355,'Payment due: $'+str(job['reward']),14,'#f6d4a1')
  else:
   self.draw_text(158,290,'No active job. Press P near a station, rancher, miner,',13,'#e9d3b5')
   self.draw_text(158,316,'stablehand or settlement worker to accept paid work.',13,'#e9d3b5')
  if self.road_contract:self.draw_text(158,408,'ROAD JOB: '+self.road_contract['title']+' — '+self.road_contract['status'].upper(),13,'#c7d8ae',True)
  else:self.draw_text(158,408,'N at waystations: escort, courier, salvage or survey jobs.',12,'#c7d8ae')
  self.draw_text(480,486,'I / ESC CLOSE LEDGER',12,'#e6c38b',True,anchor='center')

 def draw_help(self):
  self.panel(190,52,580,506)
  self.draw_text(216,110,'HOW TO SURVIVE THE FRONTIER',20,'#efc58a',True)
  controls=[('WASD / ARROWS','Move'),('SHIFT','Sprint / gallop'),('MOUSE CLICK','Aim and shoot'),('SPACE / R','Fire / reload'),('Q','Dead Eye'),('2 / F6 / F7','Weapon / difficulty / aim assist'),('E / SHIFT+E','Interact / enter buildings'),('H','Mount / dismount Whiskey'),('B','Accept bounty near sheriff'),('L','Lasso wanted targets or bandits'),('G','Hogtie roped outlaw (on foot)'),('E BY TIED TARGET','Pick up captive'),('E BY SHERIFF','Deliver prisoner alive (on foot)'),('1','Health tonic'),('M / J','Map / journal (TAB and Enter choose map towns)'),('F / T','Gather / camp'),('P','Take or collect paid work'),('N / U','Waystation road jobs / rumors'),('Y','Regional stories at Galloway / Roan Creek'),('I','Work ledger and horse condition'),('V / O','Sound effects / ambient music'),('F5','Save game'),('F11','Fullscreen'),('ESC / F1','Pause / help')]
  for i,(k,v) in enumerate(controls):
   yy=139+i*17
   self.draw_text(218,yy,k,11,'#f4d59e',True)
   self.draw_text(445,yy,v,11,'#e3d2b8')

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
  if self.screen=='title':
   self.audio.set_music_state('title')
   self.draw_title();return
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
  if self.work_ledger_open:self.draw_work_ledger()
  if self.show_help:self.draw_help()
  self.draw_dialog()
  self.draw_choice_dialogue()

 def quit(self):
  if self.screen in ('playing','paused','ending'):self.save()
  self.audio.stop()
  self.root.destroy()


def main():
 if '--self-test' in sys.argv:
  assert len(MISSIONS)==9 and len(BUILDINGS)>=25 and (WW,WH)==(60000,40960)
  assert all(t in INTERIOR_TYPES for t in ('Saloon','General Store','Hotel','Sheriff'))
  assert len(SHOP_GOODS)>=6
  assert VERSION.startswith('2.7')
  assert os.path.exists(os.path.join(ASSETS,'world.png'))
  assert os.path.exists(os.path.join(ASSETS,'title.png'))
  print('Self-test OK: story, buildings, and artwork present.')
  return
 root=tk.Tk()
 Game(root)
 root.mainloop()
if __name__=='__main__':main()
