#!/usr/bin/env python3
"""Frontier Justice: arrest ordinary bandits alive without breaking named bounties."""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game

class Key:
 def __init__(self,key):self.keysym=key;self.state=0
def tap(g,key):
 event=Key(key);g.key_down(event);g.key_up(event)

def prepare_shot(g,enemy):
 for distance in (120,85):
  for dx,dy in ((distance,0),(-distance,0),(0,distance),(0,-distance)):
   px,py=enemy.x+dx,enemy.y+dy
   if g.can_move(px,py,12) and g.line_of_fire(px,py,enemy.x,enemy.y):
    g.x,g.y=px,py
    g.camx=max(0,min(game.WW-game.VW,int(px-game.VW/2)))
    g.camy=max(0,min(game.WH-game.VH,int(py-game.VH/2)))
    g.mouse=(int(enemy.x-g.camx),int(enemy.y-g.camy))
    return
 raise AssertionError('No clear lasso approach')

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  # Other randomly spawned bandits can intercept the lasso aim corridor.
  g.actors=[a for a in g.actors if a.kind!='bandit']
  x,y=g.safe_enemy_spawn(2000,900)
  drifter=game.Actor(x,y,'bandit','Drifter',70,70,75)
  g.actors.append(drifter)
  prepare_shot(g,drifter)
  tap(g,'l')
  assert g.field_status()=='roped'
  assert drifter.kind=='field_prisoner'
  old=(drifter.x,drifter.y)
  g.update_ai(.10)
  assert (drifter.x,drifter.y)==old
  g.x,g.y=drifter.x,drifter.y
  tap(g,'g')
  assert g.field_status()=='hogtied'
  assert g.save(manual=True)
  r=game.Game(root);r.continue_game();r.dialog=None
  assert r.field_status()=='hogtied' and r.field_actor()
  r.x,r.y=r.field_actor().x,r.field_actor().y
  tap(r,'e')
  assert r.field_status()=='carried' and r.field_actor() is None
  assert r.save(manual=True)
  carry=game.Game(root);carry.continue_game();carry.dialog=None
  assert carry.field_status()=='carried'
  carry.horse_x,carry.horse_y=carry.x+20,carry.y
  tap(carry,'h')
  assert carry.mounted and carry.field_status()=='carried'
  sheriff=next(a for a in carry.actors if a.name=='Sheriff Bell')
  carry.x,carry.y=sheriff.x,sheriff.y
  before=carry.money;honor=carry.honor
  tap(carry,'e')
  assert carry.field_status()=='carried'
  tap(carry,'h')
  tap(carry,'e')
  assert carry.field_prisoner is None and carry.field_arrests==1
  assert carry.money==before+24 and carry.honor==min(100,honor+2)
  assert not carry.deliver_field_prisoner()
  assert carry.save(manual=True)
  reloaded=game.Game(root);reloaded.continue_game();reloaded.dialog=None
  assert reloaded.field_arrests==1 and reloaded.field_prisoner is None
  # Escape after eight seconds: captives become hostile bandits again.
  reloaded.actors=[a for a in reloaded.actors if a.kind!='bandit']
  ax,ay=reloaded.safe_enemy_spawn(2140,750)
  fugitive=game.Actor(ax,ay,'bandit','Drifter',70,70,75)
  reloaded.actors.append(fugitive)
  prepare_shot(reloaded,fugitive)
  reloaded.lasso_cooldown=0
  tap(reloaded,'l')
  assert reloaded.field_status()=='roped'
  reloaded.update_bounty_capture(9)
  assert reloaded.field_status() is None and fugitive.kind=='bandit'
  # The named bounty board still works after an ordinary field arrest.
  reloaded.x,reloaded.y=sheriff.x,sheriff.y
  tap(reloaded,'b')
  assert reloaded.contract and reloaded.contract['name']=='Vulture Jack'
  assert reloaded.contract['alive_reward']==120
  root.destroy()
 print('OK: roaming bandit lasso, tie, pickup, horse, sheriff, pay, save, escape, and named bounty compatibility')

if __name__=='__main__':main()
