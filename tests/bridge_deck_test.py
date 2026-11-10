#!/usr/bin/env python3
"""Bridge art/collision parity, finite rail spans, culling and water safety."""
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import new_austellia as atlas
from tools.audit_routes import acceptance_failures


class Canvas:
 def __init__(self):self.polygons=[];self.lines=[]
 def create_polygon(self,*coords,**style):self.polygons.append((coords,style))
 def create_line(self,*coords,**style):self.lines.append((coords,style))


class BridgeDeckTest(unittest.TestCase):
 def test_heading_normalized_and_corners_match_collision(self):
  deck=atlas.bridge_deck((500,400,3,4,'Fixture','road',100))
  self.assertAlmostEqual(math.hypot(deck.dx,deck.dy),1)
  self.assertEqual(deck.half_length,220)
  self.assertEqual(deck.half_width,82)
  for x,y in deck.corners:
   self.assertAlmostEqual(abs((x-deck.x)*deck.dx+(y-deck.y)*deck.dy),deck.half_length)
   self.assertAlmostEqual(abs(-(x-deck.x)*deck.dy+(y-deck.y)*deck.dx),deck.half_width)
  with self.assertRaises(ValueError):atlas.bridge_deck((0,0,0,0,'Fixture','rail',100))

 def test_live_deck_boundaries_have_no_hidden_margin(self):
  for deck in atlas.BRIDGE_DECKS:
   with self.subTest(water=deck.water,kind=deck.kind):
    with patch.object(atlas,'BRIDGE_DECKS',(deck,)):
     for along,across,inside in ((0,0,True),(.999*deck.half_length,.999*deck.half_width,True),
                                 (-.999*deck.half_length,-.999*deck.half_width,True),
                                 (deck.half_length+.01,0,False),
                                 (-deck.half_length-.01,0,False),
                                 (0,deck.half_width+.01,False),(0,-deck.half_width-.01,False)):
      x=deck.x+deck.dx*along-deck.dy*across
      y=deck.y+deck.dy*along+deck.dx*across
      self.assertEqual(atlas.bridge_at(x,y),inside)

 def test_painted_polygon_equals_shared_footprint(self):
  for deck in atlas.BRIDGE_DECKS:
   canvas=Canvas();camx,camy=deck.x-100,deck.y-100
   atlas.draw_bridge_decks(canvas,camx,camy,200,200,(deck,))
   self.assertEqual(len(canvas.polygons),1)
   coords,style=canvas.polygons[0]
   expected=tuple(v for x,y in deck.corners for v in (x-camx,y-camy))
   self.assertEqual(coords,expected)
   self.assertEqual(style['tags'],('bridge_deck',))
   self.assertEqual(style['outline'],'')

 def test_long_deck_culls_by_extent_not_center(self):
  deck=atlas.BridgeDeck(2000,50,1,0,1800,38,'Fixture','rail')
  canvas=Canvas()
  atlas.draw_bridge_decks(canvas,0,0,300,100,(deck,))
  self.assertEqual(len(canvas.polygons),1,'Visible end of an offscreen bridge must remain drawn')
  canvas=Canvas()
  atlas.draw_bridge_decks(canvas,5000,0,300,100,(deck,))
  self.assertFalse(canvas.polygons or canvas.lines)

 def test_angled_rail_span_reaches_banks_without_parallel_megabridge(self):
  with patch.object(atlas,'WATERWAYS',(('Fixture',((-1000,0),(1000,0)),100),)):
   deck=atlas.bridge_deck((0,0,.8,.6,'Fixture','rail',100))
   self.assertAlmostEqual(deck.half_length,100/.6+120)
   self.assertLess(deck.half_width,atlas.bridge_deck((0,0,.8,.6,'Fixture','road',100)).half_width)
   parallel=atlas.bridge_deck((0,0,1,.01,'Fixture','rail',100))
   self.assertEqual(parallel.half_length,220,'Parallel riverbeds require detours')

 def test_decks_never_open_lakes_or_gulf(self):
  for point in (atlas.P(505,146),atlas.P(900,1020)):
   deck=atlas.BridgeDeck(*point,1,0,100,82,'Fixture','road')
   with patch.object(atlas,'BRIDGE_DECKS',(deck,)):
    self.assertTrue(atlas.bridge_at(*point))
    self.assertTrue(atlas.is_water(*point))

 def test_mapped_rail_stations_keep_access(self):
  ids=('galloway','saints_hollow','roan_creek','blackwater_crossing','larkfield',
       'harpers_landing','valleyford','dustwell','riversend','saint_brigids','bayou_haven')
  for key in ids:
   x,y=atlas.TOWN_BY_ID[key][2:4]
   distance=min(atlas.distance_to_segment(x,y,a,b) for route in atlas.RAILS
                for a,b in zip(route,route[1:]))
   self.assertLess(distance,90,key)

 def test_rail_clearance_is_an_explicit_required_gate(self):
  report={'graph':{'wagon_components':1,'disconnected_or_missing_road_core_ids':[]},
          'waystations':[], 'physical_collision':{
           'rail':{'kind':'rail','sample_step':10,'edges_sampled':True,'blocked':1}}}
  self.assertFalse(acceptance_failures(report))
  self.assertTrue(acceptance_failures(report,include_rail=True))


if __name__=='__main__':unittest.main()
