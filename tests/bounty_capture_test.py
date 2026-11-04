#!/usr/bin/env python3
"""Dead-or-alive bounty regression: xvfb-run -a python3 tests/bounty_capture_test.py"""
import os,sys,tempfile,math,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game

class Key:
 def __init__(self,key):self.keysym=key;self.state=0

def tap(g,key):
 event=Key(key);g.key_down(event);g.key_up(event)

def approach_target(g,target):
 # Find a walkable, unobstructed side of the wanted outlaw.
 for distance in (145,105,65):
  for dx,dy in ((distance,0),(-distance,0),(0,distance),(0,-distance),
                (distance*.707,distance*.707),(-distance*.707,distance*.707)):
   x,y=target.x+dx,target.y+dy
   if not g.can_move(x,y,12):continue
   if not g.line_of_fire(x,y,target.x,target.y):continue
   g.x,g.y=x,y
   g.camx=max(0,min(game.WW-game.VW,int(x-game.VW/2)))
   g.camy=max(0,min(game.WH-game.VH,int(y-game.VH/2)))
   g.mouse=(int(target.x-g.camx),int(target.y-g.camy))
   return
 raise AssertionError('No clear lasso approach to '+target.name)

def capture_and_deliver(g):
 sheriff=next(a for a in g.actors if a.name=='Sheriff Bell')
 g.dialog=None;g.mounted=False
 g.x,g.y=sheriff.x,sheriff.y
 tap(g,'b')
 assert g.contract is not None
 assert g.contract['alive_reward']==g.contract['reward']*2
 target=g.bounty_actor()
 assert target is not None
 name=target.name;reward=g.contract['alive_reward']
 approach_target(g,target)
 g.lasso_cooldown=0.
 tap(g,'l')
 assert g.bounty_state()=='roped',name
 old=(target.x,target.y)
 g.update_ai(.1)
 assert (target.x,target.y)==old,'Roped target must stop moving'
 g.x,g.y=target.x-25,target.y
 g.mounted=True
 assert not g.hogtie_bounty(), 'Must dismount before hogtying'
 g.mounted=False
 tap(g,'g')
 assert g.bounty_state()=='hogtied'
 assert g.contract['captive_pos']==[target.x,target.y]
 assert g.save(manual=True)
 # Keeping the target hogtied after reloading must preserve the capture.
 r=game.Game(g.root);r.continue_game();r.dialog=None
 assert r.bounty_state()=='hogtied'
 tied=r.bounty_actor()
 assert tied is not None and (tied.x,tied.y)==old
 r.x,r.y=tied.x,tied.y
 tap(r,'e')
 assert r.bounty_state()=='carried'
 assert r.bounty_actor() is None
 assert not any(a.kind=='bounty_target' for a in r.actors), 'No captive ground corpse after pickup'
 assert r.waypoint==[418,463]
 assert r.save(manual=True)
 saved=game.Game(g.root);saved.continue_game();saved.dialog=None
 assert saved.bounty_state()=='carried' and saved.bounty_actor() is None
 before=saved.money;honor=saved.honor
 # Carrying a prisoner must survive actually mounting and dismounting Whiskey.
 saved.horse_x,saved.horse_y=saved.x+23,saved.y+10
 tap(saved,'h')
 assert saved.mounted and saved.bounty_state()=='carried'
 saved.x,saved.y=sheriff.x,sheriff.y
 tap(saved,'e')
 assert saved.contract and saved.bounty_state()=='carried'
 tap(saved,'h')
 assert not saved.mounted
 tap(saved,'e')
 assert saved.contract is None and saved.money==before+reward
 assert saved.honor==min(100,honor+5)
 assert saved.bounties_done==g.bounties_done+1
 assert not saved.finish_bounty(alive=True), 'No double payout'
 return saved

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  for expected in ('Vulture Jack','Rattlesnake Cole','Maeve Blackwater','Red Sand Boone','The Iron Fox'):
   g=capture_and_deliver(g)
   assert g.bounties_done>0
  assert g.bounties_done==5
  # Old bounty saves without status or alive_reward remain valid.
  sheriff=next(a for a in g.actors if a.name=='Sheriff Bell')
  g.x,g.y=sheriff.x,sheriff.y
  g.contract={'name':'Vulture Jack','location':[1820,600],'reward':60,'finished':False}
  assert g.save(manual=True)
  legacy=game.Game(root);legacy.continue_game()
  assert legacy.bounty_state()=='hunting'
  assert legacy.contract['alive_reward']==120
  # Roped target should eventually escape if not hogtied.
  legacy.dialog=None
  target=legacy.bounty_actor()
  approach_target(legacy,target)
  legacy.lasso_cooldown=0.
  tap(legacy,'l')
  assert legacy.bounty_state()=='roped'
  legacy.update_bounty_capture(9.)
  assert legacy.bounty_state()=='hunting'
  root.destroy()
 print('OK: all five bounties captured and delivered alive; save/reload, mounted transport, payouts, legacy saves, rope timeout')

if __name__=='__main__':main()
