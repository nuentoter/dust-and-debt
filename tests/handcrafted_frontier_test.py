#!/usr/bin/env python3
"""Handcrafted Frontier v2.7: horse controls, chapters, map and safe interiors."""
import os,sys,math,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from horse_riding import step_motion,TROT_SPEED,GALLOP_SPEED
from frontier_chapters import CHAPTERS,CHAPTER_BY_ID,node_for

def main():
 assert len(CHAPTERS)==2 and all(len(c['steps'])==4 for c in CHAPTERS)
 assert abs(TROT_SPEED/205-1.5)<.01
 assert GALLOP_SPEED==650
 horse={'stamina':100.,'speed':0.,'heading_x':0.,'heading_y':-1.,'exhausted':False}
 for _ in range(25):
  vx,vy,running=step_motion(horse,1,0,.10,True,100)
 assert running and horse['speed']>560 and 20<horse['stamina']<60
 old=horse['stamina']
 for _ in range(60):step_motion(horse,1,0,.10,False,100)
 assert horse['stamina']>old and horse['speed']<TROT_SPEED+15
 for _ in range(70):step_motion(horse,1,0,.1,True,100)
 assert horse['exhausted'] and not step_motion(horse,1,0,.1,True,100)[2]
 for _ in range(40):step_motion(horse,0,0,.1,False,100)
 assert horse['stamina']>28
 assert step_motion(horse,1,0,.1,True,100)[2]
 with tempfile.TemporaryDirectory() as temp:
  game.SAVE=os.path.join(temp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert game.VERSION.startswith('2.7')
  assert 'horse_motion' in vars(g)
  g.mounted=True
  g.keys={'d','shift_l'}
  g.x,g.y=2200,2900
  origin=(g.x,g.y)
  for _ in range(18):g.update(.05)
  assert g.x>origin[0]+110 and g.horse_motion['stamina']<100
  g.keys={'d'}
  before=g.horse_motion['stamina']
  for _ in range(40):g.update(.05)
  assert g.horse_motion['stamina']>before
  # A full-speed horse cannot pass straight through an impassable building.
  g.x,g.y=260,360;g.keys={'d','shift_l'};g.horse_motion['speed']=GALLOP_SPEED
  for _ in range(15):g.update(.05)
  assert g.x<=game.BUILDINGS[0][1]-16,'Horse tunneled into Sheriff building'
  g.keys.clear();g.mounted=False
  # Each regional story contains three distant destinations plus a return.
  for chapter in CHAPTERS:
   start=node_for(chapter,0)
   g.x,g.y=start['x'],start['y'];g.dialog=None
   assert g.progress_regional_chapter(),chapter['id']
   assert g.chapter_active['step']==1
   assert g.waypoint
   assert g.save(manual=True)
   restored=game.Game(root);restored.continue_game();restored.dialog=None
   assert restored.chapter_active['id']==chapter['id']
   assert restored.chapter_active['step']==1
   g=restored
   previous=g.money
   for index in (1,2,3):
    node=node_for(chapter,index)
    x,y=g.safe_enemy_spawn(node['x'],node['y'])
    assert g.can_move(x,y),('Unreachable chapter site',chapter['id'],index)
    g.x,g.y=x,y
    g.dialog=None
    assert g.progress_regional_chapter(),(chapter['id'],index)
    if index<3:
     assert g.chapter_active['step']==index+1
     assert g.waypoint
    else:
     assert g.chapter_active is None
   assert g.money==previous+chapter['reward']
   assert chapter['id'] in g.chapter_completed
   assert g.chapter_earnings>=chapter['reward']
  assert len(g.chapter_completed)==2
  g.map_open=True;g.map_destination_index=0;g.render()
  e=type('Key',(),{'keysym':'Tab','state':0})()
  g.key_down(e);g.key_up(e)
  assert g.map_destination_index==1
  e=type('Key',(),{'keysym':'Return','state':0})()
  g.key_down(e);g.key_up(e)
  assert g.waypoint==list(game.MAP_DESTINATIONS[1][2:])
  g.map_open=False
  # Existing town interiors remain usable and preserve E versus Shift+E.
  n=next(n for n in game.BUILDINGS if n[0].startswith('Galloway '))
  g.enter_interior(n[0]);g.render()
  assert g.interior==n[0]
  g.leave_interior();assert g.interior is None
  assert g.save(manual=True)
  loaded=game.Game(root);loaded.continue_game()
  assert len(loaded.chapter_completed)==2
  assert loaded.chapter_earnings==sum(c['reward'] for c in CHAPTERS)
  assert loaded.horse_motion['stamina']<=100.
  loaded.audio.stop();g.audio.stop();root.destroy()
 print('OK: 1.5x trot/2.5x gallop, stamina recovery/exhaustion, solid walls, both regional stories, atlas selector, interior and save')

if __name__=='__main__':main()
