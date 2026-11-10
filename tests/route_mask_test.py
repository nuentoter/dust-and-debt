#!/usr/bin/env python3
"""Authored corridors protect travel; retired grid lines cannot clear terrain."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import game
import natural_terrain as terrain
from frontier_world import road_at,START_SPUR
from frontier_routes import ROUTE_SOURCES
from new_austellia import travel_road,travel_trail,is_water


class RouteMaskTest(unittest.TestCase):
 def test_unmapped_grid_lines_are_not_route_or_protection_corridors(self):
  instance=object.__new__(game.Game)
  for x,y in ((10200,9000),(15000,4300),(16000,7900)):
   with self.subTest(x=x,y=y):
    self.assertFalse(travel_road(x,y) or travel_trail(x,y))
    self.assertFalse(is_water(x,y))
    self.assertFalse(road_at(x,y))
    self.assertFalse(instance.is_frontier_road(x,y))
    self.assertFalse(terrain.near_protected(x,y))

 def test_old_grid_no_longer_punches_a_hole_through_graystone_ridge(self):
  a,b=terrain.RIDGES[0][1][:2]
  x=10200;y=a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0])
  self.assertFalse(travel_road(x,y) or travel_trail(x,y))
  self.assertFalse(terrain.near_protected(x,y))
  self.assertTrue(terrain.landform_solid(x,y,11))
  self.assertTrue(terrain.landform_solid(x,y,16))

 def test_authored_routes_keep_cover_clearance(self):
  instance=object.__new__(game.Game)
  for route in ROUTE_SOURCES:
   for a,b in zip(route.vertices,route.vertices[1:]):
    count=max(1,math.ceil(math.dist(a,b)/100))
    for i in range(count+1):
     x=a[0]+(b[0]-a[0])*i/count;y=a[1]+(b[1]-a[1])*i/count
     self.assertTrue(terrain.near_protected(x,y),(route.id,x,y))
     if x<4800 and y<3200:continue
     self.assertTrue(instance.is_frontier_road(x,y),(route.id,x,y))
     self.assertFalse(terrain.landform_solid(x,y,16),(route.id,x,y))

 def test_original_parcel_and_starter_spur_keep_their_policy(self):
  for x,y in ((700,610),START_SPUR[0]):
   self.assertFalse(road_at(x,y))
   self.assertTrue(terrain.near_protected(x,y))
  for x,y in ((4900,3250),START_SPUR[1]):
   self.assertTrue(road_at(x,y))
   self.assertFalse(terrain.landform_solid(x,y,16))


if __name__=='__main__':unittest.main()
