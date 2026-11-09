"""Deterministic, low-cost enemy tactics for Dust & Debt v2.8.

Only free-roam outlaws and named bounty targets have surrender morale.
Scripted story enemies never surrender, preserving mission completion triggers.
"""
import math

ARCHETYPES={
 "raider":{"range":320,"cooldown":2.30,"windup":.62,"spread":.20,"preferred":180},
 "skirmisher":{"range":330,"cooldown":2.55,"windup":.72,"spread":.25,"preferred":235},
 "marksman":{"range":395,"cooldown":2.85,"windup":.85,"spread":.10,"preferred":295},
 "enforcer":{"range":275,"cooldown":2.05,"windup":.65,"spread":.24,"preferred":145},
 "boss":{"range":355,"cooldown":1.25,"windup":.55,"spread":.12,"preferred":240},
 "deputy":{"range":335,"cooldown":2.75,"windup":.70,"spread":.16,"preferred":190},
}

def is_hostile(actor):
 return actor.kind in ("bandit","bounty_target","deputy") or actor.kind.startswith("mission_")

def archetype(actor):
 if actor.name=="Crow":return "boss"
 if actor.kind=="deputy":return "deputy"
 # Derive from name for reproducible spawns; no frame RNG.
 token=sum((i+1)*ord(ch) for i,ch in enumerate(actor.name))
 if actor.kind=="bounty_target":return ("enforcer","skirmisher","marksman")[token%3]
 return ("raider","skirmisher","marksman","enforcer")[token%4]

def morale(actor,nearby_allies=0):
 """0..100: injury and lack of allies lower confidence."""
 if actor.kind not in ("bandit","bounty_target"):return 100
 fraction=max(0.,min(1.,actor.hp/max(1.,actor.maxhp)))
 return max(0.,min(100.,int(24+fraction*64+min(2,nearby_allies)*9)))

def should_surrender(actor,nearby_allies=0,surrounded=False):
 if actor.kind not in ("bandit","bounty_target") or actor.dead or actor.hp<=0:return False
 return actor.hp<=actor.maxhp*.35 or surrounded or morale(actor,nearby_allies)<45

def movement(actor,dx,dy,distance):
 """Direction toward desired spacing, with deterministic flanking behavior."""
 profile=ARCHETYPES[archetype(actor)]
 length=max(1.,distance);ux,uy=dx/length,dy/length
 preferred=profile["preferred"]
 if distance>preferred+42:return ux,uy
 if distance<preferred-70:return -ux*.65,-uy*.65
 side=1 if sum(ord(c) for c in actor.name)%2 else -1
 return -uy*.47*side,ux*.47*side

def cover_goal(actor,player_x,player_y,rocks,max_search=340):
 """Seek a solid boulder between actor and player, never teleport."""
 if archetype(actor) not in ("skirmisher","marksman"):return None
 best=None
 for rx,ry,r,solid in rocks:
  if not solid:continue
  da=math.hypot(rx-actor.x,ry-actor.y)
  dp=math.hypot(rx-player_x,ry-player_y)
  if da>max_search or dp<r+80:continue
  # Stand on the far side from player; leave some breathing room.
  vx=(rx-player_x)/dp;vy=(ry-player_y)/dp
  gx=rx+vx*(r+32);gy=ry+vy*(r+32)
  score=math.hypot(gx-actor.x,gy-actor.y)
  if score<max_search and (best is None or score<best[0]):best=(score,gx,gy)
 return (best[1],best[2]) if best else None
