#!/usr/bin/env python3
"""Route-aware bridge approaches: bends, mode isolation and real failures."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from new_austellia import BridgeDeck
from frontier_routes import Route
from tools.bridge_approaches import (clip_deck_segment,route_lengths,point_at,
                                    deck_intervals,approach_anchor,crop_route)
from tools.audit_routes import bridge_approach_audit,acceptance_failures


def deck(kind='rail'):
 return BridgeDeck(1020,1000,1,0,10,5,'Fixture',kind)


def clear(x,y,r):return None

def land(x,y):return 'land'


class BridgeApproachTest(unittest.TestCase):
 def test_rotated_clip_and_parallel_miss(self):
  d=BridgeDeck(100,100,.6,.8,10,5,'Fixture','rail')
  def world(a,b):return (d.x+d.dx*a-d.dy*b,d.y+d.dy*a+d.dx*b)
  hit=clip_deck_segment(d,world(-20,0),world(20,0))
  self.assertAlmostEqual(hit[0],.25);self.assertAlmostEqual(hit[1],.75)
  self.assertIsNone(clip_deck_segment(d,world(-20,6),world(20,6)))
  self.assertIsNone(clip_deck_segment(d,world(-20,5),world(-10,5)))

 def test_crop_preserves_authored_bend_and_terminal(self):
  route=Route('bend','rail',((1000,1000),(1020,1000),(1020,1040)))
  lengths=route_lengths(route)
  self.assertEqual(deck_intervals(deck(),route,lengths),[(10.,25.)])
  cropped=crop_route(route,lengths,5,45)
  self.assertEqual(cropped.vertices,((1005.,1000.),(1020,1000),(1020.,1025.)))
  anchor=approach_anchor(route,lengths,10,-1,land)
  self.assertEqual(anchor['xy'],route.vertices[0]);self.assertTrue(anchor['route_terminal'])
  self.assertEqual(point_at(route,lengths,30)['segment'],1)

 def test_repeated_visits_stay_separate(self):
  d=BridgeDeck(0,0,1,0,10,5,'Fixture','rail')
  route=Route('repeat','rail',((-40,0),(40,0),(40,40),(-40,40),(-40,0),(40,0)))
  self.assertEqual(len(deck_intervals(d,route,route_lengths(route))),2)

 def test_anchors_follow_route_to_supported_ground(self):
  route=Route('long','rail',((0,1000),(1000,1000)))
  lengths=route_lengths(route)
  surface=lambda x,y:'land' if x<250 or x>750 else 'deck'
  a=approach_anchor(route,lengths,480,-1,surface)
  b=approach_anchor(route,lengths,520,1,surface)
  self.assertEqual((a['distance'],b['distance']),(240.,760.))
  self.assertEqual(a['surface'],'land');self.assertFalse(a['route_terminal'])

 def test_off_route_tangent_does_not_invent_a_path(self):
  route=Route('bend','rail',((1000,1000),(1020,1000),(1020,1040)))
  surface=lambda x,y:'water' if x>1030 else 'land'
  classify=lambda x,y,r:'water' if x>1030 else None
  result=bridge_approach_audit((route,),(deck(),),classify,surface)[0]
  self.assertTrue(result['passed'])
  exit=result['tangent_reviews'][1]
  self.assertEqual(exit['status'],'off_route_tangent')
  self.assertEqual(exit['distance_to_route'],35.)
  self.assertEqual(result['paths'][0]['exit']['xy'],(1020.,1040.))

 def test_actual_wet_approach_fails(self):
  route=Route('straight','rail',((1000,1000),(1100,1000)))
  surface=lambda x,y:'water' if x>1030 else 'land'
  classify=lambda x,y,r:'water' if x>1030 else None
  result=bridge_approach_audit((route,),(deck(),),classify,surface)[0]
  self.assertFalse(result['passed'])
  self.assertEqual(result['tangent_reviews'][1]['status'],'unsafe_route_tangent')
  self.assertGreater(result['paths'][0]['blocked'],0)

 def test_unsupported_terminal_fails_even_without_collision(self):
  route=Route('terminal','rail',((1000,1000),(1100,1000)))
  surface=lambda x,y:'water' if x>1030 else 'land'
  result=bridge_approach_audit((route,),(deck(),),clear,surface)[0]
  self.assertFalse(result['passed'])
  self.assertEqual(result['paths'][0]['blocked'],0)
  self.assertEqual(result['paths'][0]['exit']['surface'],'water')

 def test_horse_collision_is_not_hidden_by_foot_pass(self):
  route=Route('straight','rail',((1000,1000),(1100,1000)))
  classify=lambda x,y,r:'building' if r==16 and 1040<=x<=1050 else None
  result=bridge_approach_audit((route,),(deck(),),classify,land)[0]
  self.assertFalse(result['passed'])
  path=result['paths'][0]
  self.assertEqual(path['actor_profiles']['11']['blocked'],0)
  self.assertGreater(path['actor_profiles']['16']['blocked'],0)
  self.assertIn('crop_segment',path['first_failures'][0])

 def test_road_deck_cannot_attach_to_rail(self):
  rail=Route('rail_only','rail',((1000,1000),(1100,1000)))
  result=bridge_approach_audit((rail,),(deck('road'),),clear,land)[0]
  self.assertFalse(result['passed']);self.assertEqual(result['paths'],[])

 def test_coarse_approach_sampling_cannot_pass(self):
  route=Route('fixture','rail',((1000,1000),(1100,1000)))
  result=bridge_approach_audit((route,),(deck(),),clear,land,step=90)[0]
  self.assertFalse(result['passed'])

 def test_bad_approach_or_missing_review_blocks_physical_acceptance(self):
  report={'graph':{'wagon_components':1,'disconnected_or_missing_road_core_ids':[]},
          'waystations':[],'physical_collision':{},'crossings':[{'id':'bridge'}]}
  self.assertIn('missing bridge approach validation: bridge',acceptance_failures(report))
  report['crossings'][0]['approach_validation']={'passed':False}
  self.assertIn('unvalidated bridge approach: bridge',acceptance_failures(report))
  report['crossings'][0]['approach_validation']['passed']=True
  self.assertFalse(acceptance_failures(report))

 def test_invalid_anchor_parameters_fail_instead_of_looping(self):
  route=Route('fixture','rail',((1000,1000),(1100,1000)))
  for kwargs in ({'step':0},{'direction':0},{'guard':float('inf')}):
   args=dict(direction=1,surface=land);args.update(kwargs)
   with self.assertRaises(ValueError):approach_anchor(route,route_lengths(route),10,**args)


if __name__=='__main__':unittest.main()
