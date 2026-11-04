#!/usr/bin/env python3
"""Regression: Dust Hollow riders must not be inside buildings or blocked from combat."""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  # Old hard-coded location is inside Cabin (1670..1810, 320..430).
  assert g.solid(1780,420,20)
  assert g.can_move(*g.safe_enemy_spawn(1780,420),20)
  g.quest(1);g.dialog=None
  riders=[a for a in g.actors if a.kind=='mission_hollow' and not a.dead]
  assert len(riders)==5
  assert all(g.can_move(a.x,a.y,20) for a in riders)
  # At least one unobstructed approach to each rider from nearby ground.
  for a in riders:
   open_shot=False
   for dx,dy in ((90,0),(-90,0),(0,90),(0,-90)):
    sx,sy=a.x+dx,a.y+dy
    if g.can_move(sx,sy,10) and g.line_of_fire(sx,sy,a.x,a.y):
     open_shot=True;break
   assert open_shot, 'Unshootable mission rider: '+str((a.x,a.y))
  # Simulate existing save where four out of five riders were defeated.
  for a in riders[:4]:a.dead=True
  g.x,g.y=1790,715
  assert g.save(manual=True)
  restored=game.Game(root);restored.continue_game();restored.dialog=None
  alive=[a for a in restored.actors if a.kind=='mission_hollow' and not a.dead]
  assert len(alive)==1 and restored.can_move(alive[0].x,alive[0].y,20)
  # The last remaining rider is killable; story moves on.
  alive[0].dead=True
  restored.update(.03)
  assert restored.stage==2
  restored.dialog=None
  # Validate other mission and boss spawns too.
  for tag,locations,hp,boss in (
   ('blackspur',[(1975,1290),(2080,1280),(2030,1340)],105,None),
   ('crow',[(1370,1030),(1430,1100),(1510,1080),(1580,1030)],115,(1480,1030)),
  ):
   restored.spawn_mission(tag,locations,hp,boss)
   for a in restored.actors:
    if a.kind=='mission_'+tag:assert restored.can_move(a.x,a.y,20)
  root.destroy()
 print('OK: Dust Hollow cabin collision, reachable gunfire, four-kill save recovery, story progression and bosses')

if __name__=='__main__':main()
