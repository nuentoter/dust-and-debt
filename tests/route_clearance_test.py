#!/usr/bin/env python3
"""Fine route sampling, actor margins and physical acceptance gates."""
import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from frontier_routes import Route
from tools.audit_routes import (route_samples,physical_audit,collision_reason,
                                acceptance_failures)


class ClearanceTest(unittest.TestCase):
 def test_spacing_endpoints_and_offsets(self):
  route=Route('fixture','wagon',((100,100),(123,100),(123,127)))
  samples=list(route_samples(route,10,11))
  for segment in (0,1):
   for lane in ('center','left','right'):
    points=[s for s in samples if s['segment']==segment and s['lane']==lane]
    self.assertEqual((points[0]['t'],points[-1]['t']),(0,1))
    self.assertTrue(all(math.dist(a['xy'],b['xy'])<=10.000001
                        for a,b in zip(points,points[1:])))
  self.assertEqual(samples[0]['xy'],(100.,100.))
  left=next(s for s in samples if s['lane']=='left')
  self.assertEqual(left['offset'],39)
  self.assertEqual(left['xy'],(100.,139.))

 def test_fine_sampling_finds_obstacle_coarse_audit_misses(self):
  route=Route('fixture','wagon',((0,0),(100,0)))
  classify=lambda x,y,r:'building' if 9<=x<=11 else None
  coarse=physical_audit(90,False,(route,),classify)['fixture']
  fine=physical_audit(10,False,(route,),classify)['fixture']
  self.assertEqual(coarse['blocked'],0)
  self.assertGreater(fine['blocked'],0)
  failure=fine['first_failures'][0]
  self.assertEqual(failure['segment'],0)
  self.assertEqual(failure['t'],.1)
  self.assertEqual(failure['radius'],11)
  self.assertEqual(failure['xy'],[10.,0.])

 def test_edge_obstacle_and_horse_radius_are_separate(self):
  route=Route('fixture','wagon',((0,100),(20,100)))
  classify=lambda x,y,r:'water' if y>130 else ('building' if r==16 else None)
  result=physical_audit(10,True,(route,),classify)['fixture']
  foot=result['actor_profiles']['11']
  horse=result['actor_profiles']['16']
  self.assertEqual(foot['lanes']['center']['blocked'],0)
  self.assertGreater(foot['lanes']['left']['blocked'],0)
  self.assertEqual(horse['blocked'],horse['samples'])
  self.assertTrue(all('start_t' in r and 'end_t' in r for r in result['blocked_ranges']))
  self.assertEqual(sum(r['samples'] for r in result['blocked_ranges']),result['blocked'])

 def test_invalid_sampling_inputs(self):
  route=Route('fixture','trail',((0,0),(1,0)))
  for step in (0,-1,float('nan'),float('inf')):
   with self.assertRaises(ValueError):list(route_samples(route,step))
  for radius in (0,-1,float('nan')):
   with self.assertRaises(ValueError):list(route_samples(route,radius=radius))

 def test_zero_length_segments_are_skipped(self):
  route=Route('fixture','trail',((100,100),(100,100),(101,100)))
  samples=list(route_samples(route))
  self.assertTrue(samples)
  self.assertEqual({s['segment'] for s in samples},{1})

 def test_classifier_matches_game_static_collision(self):
  import game
  from new_austellia import BRIDGES,LAKES
  instance=object.__new__(game.Game)
  positions=[(0,0),(700,610),(60001,2000)]
  positions.extend((b[0],b[1]) for b in BRIDGES)
  positions.extend((x,y) for _,x,y,_,_ in LAKES)
  for _,x,y,w,h in game.BUILDINGS:
   positions.extend(((x+w/2,y+h/2),(x-13,y+h/2),(x+w+20,y+h/2)))
  for radius in (11,16):
   for x,y in positions:
    self.assertEqual(bool(collision_reason(x,y,radius)),instance.solid(x,y,radius),
                     (x,y,radius))

 def test_bridge_dedup_preserves_nearby_crossings_and_turns(self):
  import new_austellia as atlas
  water=(("Test River",((-1000,0),(1000,0)),20),)
  roads=(((0,-200),(0,200)),((100,-200),(100,200)),
         ((-200,-200),(200,200)),((0,200),(0,-200)))
  rails=(((0,-200),(0,200)),)
  with patch.multiple(atlas,WATERWAYS=water,ROADS=roads,RAILS=rails,SECONDARY_ROADS=()):
   bridges=atlas.build_bridges()
  self.assertEqual(len(bridges),4,'Only the reversed duplicate road should merge')
  self.assertEqual(sum(b[5]=='rail' for b in bridges),1)
  self.assertEqual(sum(b[5]=='road' for b in bridges),3)
  self.assertTrue(any(abs(b[0]-100)<.001 for b in bridges))

 def test_authored_crossings_keep_each_surface_heading(self):
  import new_austellia as atlas
  for name,water,width in atlas.WATERWAYS:
   for kind,routes in (('rail',atlas.RAILS),('road',atlas.ROADS),
                        ('road',tuple(p for _,p in atlas.SECONDARY_ROADS))):
    for route in routes:
     for a,b in zip(route,route[1:]):
      for c,d in zip(water,water[1:]):
       hit=atlas._crossing(a,b,c,d)
       if hit:
        self.assertTrue(any(math.dist(hit[:2],deck[:2])<1e-4
                             and abs(hit[2]*deck[2]+hit[3]*deck[3])>1-1e-6
                             and deck[4]==name and deck[5]==kind
                             for deck in atlas.BRIDGES),(name,kind,hit))

 def test_acceptance_rejects_blocked_roads_and_incomplete_probes(self):
  base={'graph':{'wagon_components':1,'disconnected_or_missing_road_core_ids':[]},
        'waystations':[]}
  self.assertEqual(acceptance_failures(base),[])
  base['physical_collision']={'road':{'kind':'wagon','sample_step':90,
                                     'edges_sampled':False,'blocked':1}}
  self.assertEqual(len(acceptance_failures(base)),2)
  base['physical_collision']['road'].update(sample_step=10,edges_sampled=True,blocked=0)
  self.assertEqual(acceptance_failures(base),[])
  base['physical_collision']['rail']={'kind':'rail','sample_step':90,
                                     'edges_sampled':False,'blocked':100}
  self.assertEqual(acceptance_failures(base),[],'Rail must not certify or block wagon clearance')
  base['waystations']=[{'id':'isolated','distance_to_wagon':181}]
  self.assertTrue(acceptance_failures(base))


if __name__=='__main__':unittest.main()
