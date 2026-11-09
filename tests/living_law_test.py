#!/usr/bin/env python3
"""Living Law v2.4 regression: xvfb-run -a python3 tests/living_law_test.py"""
import os,sys,tempfile,tkinter as tk,math
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert game.VERSION.startswith('2.4')
  patrols=[a for a in g.actors if a.kind=='law_patrol']
  assert len(patrols)==8 and all(g.can_move(a.x,a.y,20) for a in patrols)
  patrol=patrols[0]
  assert len(patrol.route)==4
  before=(patrol.x,patrol.y)
  g.x,g.y=patrol.x+160,patrol.y
  g.law_status='PEACE';g.wanted=0
  g.update_patrol(patrol,.5)
  assert patrol.dead is False and (patrol.x,patrol.y)!=before
  assert not g.bullets, 'Peaceful lawmen must never open fire'
  # A wounded roaming outlaw surrenders, without a lasso.
  bandit=game.Actor(2100,800,'bandit','Drifter',24,70,75)
  g.actors.append(bandit)
  g.x,g.y=2100,835
  assert g.check_surrender(bandit)
  assert bandit.kind=='field_prisoner' and g.field_status()=='surrendered'
  g.mounted=False
  assert g.hogtie_bounty() and g.field_status()=='hogtied'
  assert g.pick_up_bounty() and g.field_status()=='carried'
  assert g.field_actor() is None
  sheriff=next(a for a in g.actors if a.name=='Sheriff Bell')
  g.x,g.y=sheriff.x,sheriff.y
  balance=g.money
  g.interact()
  assert g.field_arrests==1 and g.money==balance+24
  assert g.jail_roster[-1]['case']=='field arrest' and g.law_reputation>=2
  g.interior='Sheriff';g.show_jail=True;g.render()
  assert g.jail_roster[-1]['name']=='Drifter'
  assert g.save(manual=True)
  restored=game.Game(root);restored.continue_game();restored.dialog=None
  assert len(restored.jail_roster)==1 and restored.law_reputation>=2
  assert restored.field_arrests==1
  # A named wanted outlaw can surrender, be delivered alive and appear in jail.
  restored.x,restored.y=sheriff.x,sheriff.y
  restored.begin_bounty()
  wanted=restored.bounty_actor()
  wanted.hp=25
  assert restored.check_surrender(wanted) and restored.bounty_state()=='surrendered'
  restored.x,restored.y=wanted.x,wanted.y
  assert restored.hogtie_bounty()
  assert restored.pick_up_bounty()
  restored.x,restored.y=sheriff.x,sheriff.y
  cash=restored.money
  restored.interact()
  assert restored.contract is None and restored.money==cash+120
  assert restored.jail_roster[-1]['name']=='Vulture Jack'
  assert len(restored.jail_roster)==2
  # Story-quest enemies cannot surrender and block a scripted elimination goal.
  mission=game.Actor(1900,350,'mission_hollow','Hollow rider',10,95,91)
  assert restored.check_surrender(mission) is False
  # Lawmen respond to actual wanted status but not mere innocent proximity.
  fresh=game.Game(root);fresh.new_game();fresh.dialog=None
  guard=next(a for a in fresh.actors if a.kind=='law_patrol')
  fresh.x,fresh.y=guard.x+80,guard.y
  fresh.wanted=2.5;fresh.law_status='WANTED';guard.shoot=0
  fresh.update_patrol(guard,.1)
  assert guard.dead is False
  # Sheriff Bell still begins the original campaign.
  starter=game.Game(root);starter.new_game();starter.dialog=None
  bell=next(a for a in starter.actors if a.name=='Sheriff Bell')
  starter.x,starter.y=bell.x,bell.y
  starter.interact()
  assert starter.stage==1 and starter.dialog is not None
  root.destroy()
 print('OK: patrol routes, surrender, hogtie, jail intake, persistence, named bounty, original story')
if __name__=='__main__':main()
