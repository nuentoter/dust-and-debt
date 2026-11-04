#!/usr/bin/env python3
"""Emergent Frontier regression test: xvfb-run -a python3 tests/emergent_test.py"""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  sheriff=next(a for a in g.actors if a.name=="Sheriff Bell")
  g.x,g.y=sheriff.x,sheriff.y
  assert g.near_bounty_board()
  g.begin_bounty()
  assert g.contract and g.contract["name"]=="Vulture Jack"
  target=next(a for a in g.actors if a.kind=="bounty_target" and not a.dead)
  assert target.name==g.contract["name"]
  assert g.save(manual=True)
  r=game.Game(root);r.continue_game();r.dialog=None
  assert r.contract and r.contract["name"]=="Vulture Jack"
  assert sum(a.kind=="bounty_target" and not a.dead for a in r.actors)==1
  target=next(a for a in r.actors if a.kind=="bounty_target" and not a.dead)
  amount=r.money;target.dead=True
  r.finish_bounty(target)
  assert r.money==amount+60 and r.contract is None and r.bounties_done==1
  r.x,r.y=6500.,4500.;r.safe_timer=0.
  assert r.spawn_road_encounter()
  traveler=next(a for a in r.actors if a.kind=="traveler")
  r.x,r.y=traveler.x,traveler.y
  old=r.money
  r.interact()
  assert r.money==old+12 and r.dialog and not any(a.kind=="traveler" for a in r.actors)
  r.dialog=None
  r.render()
  assert r.save(manual=True)
  reloaded=game.Game(root);reloaded.continue_game()
  assert reloaded.bounties_done==1 and reloaded.contract is None
  root.destroy()
 print("OK: bounty acceptance, target respawn, completion, rescue, persistence")
if __name__=="__main__":main()
