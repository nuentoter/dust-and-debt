#!/usr/bin/env python3
"""v2.1 Frontier Reborn content regression: xvfb-run -a python3 tests/frontier_reborn_test.py"""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from frontier_expansion import SETTLEMENTS,SIDE_JOBS,resource_nodes,nearby_settlement

def main():
 assert len(SETTLEMENTS)==6 and len(SIDE_JOBS)==6 and len(resource_nodes())==12
 assert len(game.BUILDINGS)>=45 and len(game.NPCS)>=60
 with tempfile.TemporaryDirectory() as directory:
  game.SAVE=os.path.join(directory,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  for key,name,cx,cy,*_ in SETTLEMENTS:
   assert nearby_settlement(cx,cy)==key
   assert g.in_safe_settlement(cx,cy)
   assert g.region_name(cx,cy)==name
   assert g.can_move(cx,cy)
  assert not g.in_safe_settlement(8300,6000)
  # Verify the six side jobs are offered by the expected named local residents.
  for key,name,cx,cy,wall,roof,guide_name in SETTLEMENTS:
   actor=next(a for a in g.actors if a.name==guide_name)
   assert actor.kind=='guide'
   g.x,g.y=actor.x,actor.y
   assert not g.side_job
   g.interact()
   assert g.side_job and g.side_job['step']==0
   job=next(j for j in SIDE_JOBS if j[1]==key)
   assert g.side_job['id']==job[0]
   assert g.waypoint==list(job[4][0])
   g.dialog=None
   before=g.money
   for step,(tx,ty) in enumerate(job[4]):
    g.x,g.y=tx,ty;g.interact()
    assert g.dialog
    g.dialog=None
   assert job[0] in g.side_completed and g.side_job is None
   assert g.money>=before+job[5]
  assert len(g.side_completed)==6
  # New work schedules are occupation-based while story givers remain fixed.
  courier=next(a for a in g.actors if a.name==SETTLEMENTS[0][1]+' Courier')
  sheriff=next(a for a in g.actors if a.name=='Sheriff Bell')
  original=(sheriff.x,sheriff.y)
  g.clock=8;g.update_npc_schedules()
  first=courier.destination
  g.clock=14;g.update_npc_schedules()
  assert courier.destination!=first and 'freight' in g.npc_activity(courier)
  assert (sheriff.x,sheriff.y)==original
  # Two kinds of resource gathering, then a free camp rest.
  key,name,cx,cy,*_=SETTLEMENTS[0]
  medicine=next(x for x in resource_nodes() if x[0]==key+'-herbs')
  g.x,g.y=medicine[1:3]
  tonics=g.tonics
  assert g.gather_resource() and g.tonics==tonics+1
  assert not g.gather_resource()
  ore=next(x for x in resource_nodes() if x[0]==key+'-ore')
  g.x,g.y=ore[1:3];money=g.money
  assert g.gather_resource() and g.money==money+9
  g.x,g.y=cx,cy;g.hp=45;clock=g.clock
  assert g.rest_at_frontier_camp() and g.hp==75
  assert not g.rest_at_frontier_camp()
  assert g.discover_settlement() and key in g.visited_settlements
  # Both expanded scenery and the map can render at new town coordinates.
  g.camx=int(cx-game.VW/2);g.camy=int(cy-game.VH/2)
  g.render();g.map_open=True;g.render();g.map_open=False
  assert g.save(manual=True)
  restored=game.Game(root);restored.continue_game()
  assert len(restored.side_completed)==6
  assert key in restored.camps_used and key in restored.visited_settlements
  assert len(restored.gathered_nodes)==2
  # Original mission remains accessible after loading an expansion save.
  g.dialog=None;g.stage=0;g.x,g.y=original
  g.interact()
  assert g.stage==1 and g.dialog
  root.destroy()
 print('OK: 6 towns, 6 side missions, work routines, gathering, rest, discovery, rendering, saves and story')
if __name__=='__main__':main()
