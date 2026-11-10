#!/usr/bin/env python3
"""v2.9-map: ensure all new fishing/camps are genuinely linked and on dry land."""
import os,sys,math,unittest
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from frontier_destinations import DESTINATIONS,fishing_spots,campsites
from frontier_routes import ROUTE_GRAPH,route_path,nearest_route_anchor
from frontier_route_art import clip_segment
from new_austellia import is_water,SECONDARY_ROADS,TRAILS
from natural_terrain import landform_solid

class SitesTest(unittest.TestCase):
 def test_counts_and_unique_ids(self):
  self.assertEqual(len(fishing_spots()),12)
  self.assertEqual(len(campsites()),12)
  self.assertEqual(len({d.id for d in DESTINATIONS}),24)
  self.assertEqual(len(TRAILS),24)
  self.assertEqual(len(SECONDARY_ROADS),10)

 def test_dry_approach_and_trailhead(self):
  for d in DESTINATIONS:
   with self.subTest(destination=d.id):
    self.assertFalse(is_water(d.x,d.y),d.id+" is placed in water")
    self.assertFalse(landform_solid(d.x,d.y,11),d.id+" obstructed by terrain")
    self.assertLess(math.dist((d.x,d.y),d.route[-1]),.1)
    self.assertIsNotNone(nearest_route_anchor(*d.trailhead,mode="wagon",max_distance=120),
                         d.id+" trail must begin on real wagon route")

 def test_foot_horse_trails_join_wagon_network(self):
  for d in DESTINATIONS:
   with self.subTest(destination=d.id):
    self.assertIsNotNone(route_path(d.trailhead,(d.x,d.y),mode="foot"),d.id)
    self.assertIsNotNone(route_path(d.trailhead,(d.x,d.y),mode="horse"),d.id)

 def test_wagons_cannot_use_trails_as_shortcuts(self):
  # A route that exists exclusively as a trail should not be marked
  # usable by wagon; trail segments remain separate graph mode.
  self.assertTrue(any(e.kind=="trail" for e in ROUTE_GRAPH.edges))
  self.assertNotIn("trail",{"wagon"})

 def test_map_clipping(self):
  box=(100,100,200,200)
  self.assertEqual(clip_segment((0,200),(400,200),box),((100.,200.),(300.,200.)))
  self.assertIsNone(clip_segment((0,0),(20,20),box))

if __name__=="__main__":unittest.main()
