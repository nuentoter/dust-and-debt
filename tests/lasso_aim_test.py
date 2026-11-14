#!/usr/bin/env python3
"""Regression for cursor-limited lasso range, aiming, and actual capture."""
import math,os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from lasso_targeting import throw_segment,choose_target,LASSO_RANGE

class Key:
 def __init__(self,key):self.keysym=key;self.state=0

def tap(g,key):
 e=Key(key);g.key_down(e);g.key_up(e)

def aim(g,world_x,world_y):
 g.camx=max(0,min(game.WW-game.VW,int(g.x-game.VW/2)))
 g.camy=max(0,min(game.WH-game.VH,int(g.y-game.VH/2)))
 g.mouse=(world_x-g.camx,world_y-g.camy)

def main():
 # Pure geometry: short throws must never project to a fixed full-length rope.
 start,end,unit,length,dist=throw_segment((100,100),(170,115))
 assert math.dist(end,(170,115))<1e-5
 assert math.isclose(length,math.hypot(70,15))
 start,end,unit,length,dist=throw_segment((100,100),(900,100))
 assert math.isclose(length,LASSO_RANGE)
 assert end==(100+LASSO_RANGE,100)
 start,end,unit,length,dist=throw_segment((100,100),(100,100),(0,1))
 assert start==end and length==0
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None;g.mounted=False
  g.x,g.y=1200.,600.
  g.actors=[a for a in g.actors if a.kind not in ('bandit','bounty_target')]
  enemy=game.Actor(1320.,600.,'bandit','Test Drifter',70,70,75)
  g.actors.append(enemy)
  # A short throw near the player must end AT the pointer, and not rope
  # a bandit farther down that direction.
  aim(g,1240.,600.)
  g.lasso_cooldown=0.
  tap(g,'l')
  assert g.field_prisoner is None
  assert math.dist(g.lasso_visual[2:4],(1240,600))<.001, g.lasso_visual
  # Cursor aimed on actor: rope actually attaches and state changes.
  aim(g,enemy.x,enemy.y)
  g.lasso_cooldown=0.
  tap(g,'l')
  assert g.field_status()=='roped'
  assert enemy.kind=='field_prisoner'
  assert g.lasso_visual[2:4]==[enemy.x,enemy.y]
  # Existing hogtie/pickup mechanics must still work.
  g.x,g.y=enemy.x-30,enemy.y
  tap(g,'g')
  assert g.field_status()=='hogtied'
  tap(g,'e')
  assert g.field_status()=='carried'
  # Maximum range still enforced if mouse pointer is far away.
  g.field_prisoner=None
  enemy.kind='bandit'
  enemy.x,enemy.y=1700.,600.
  g.x,g.y=1200.,600.
  aim(g,enemy.x,enemy.y)
  g.lasso_cooldown=0.
  tap(g,'l')
  assert g.field_status() is None
  assert math.isclose(g.lasso_visual[2]-g.x,LASSO_RANGE,abs_tol=.001)
  # With two actors on a ray, the cursor-targeted actor should win
  # rather than the nearer outlaw stealing the throw.
  near=game.Actor(1270.,600.,'bandit','Near Drifter',70,70,75)
  far=game.Actor(1390.,600.,'bandit','Pointed Drifter',70,70,75)
  g.actors.extend((near,far))
  aim(g,far.x,far.y)
  g.lasso_cooldown=0.
  tap(g,'l')
  assert far.kind=='field_prisoner', 'Cursor-highlighted outlaw should be roped'
  assert near.kind=='bandit'
  # Wall/terrain occlusion still excludes capture.
  g.field_prisoner=None
  far.kind='bandit'
  aim(g,far.x,far.y)
  original=g.line_of_fire
  g.line_of_fire=lambda *args:False
  g.lasso_cooldown=0.
  tap(g,'l')
  assert g.field_prisoner is None
  g.line_of_fire=original
  g.audio.stop();root.destroy()
 print('OK: lasso stops at cursor, selects pointed outlaw, respects range, walls, tie and carry')

if __name__=="__main__":main()
