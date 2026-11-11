#!/usr/bin/env python3
"""The preserved starter exit shares one source across world, maps and graph."""
import os
from pathlib import Path
import sys
import tempfile
import tkinter as tk
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DUST_AND_DEBT_SILENT','1')
import game
import new_austellia as atlas
import frontier_world as world
from frontier_routes import ROUTE_SOURCES
from frontier_route_art import draw_scaled_routes,draw_starter_spur,clip_segment


class Canvas:
 def __init__(self):self.items=[]
 def __getattr__(self,name):
  if name.startswith('create_'):
   return lambda *coords,**style:self.items.append((name,coords,style))
  raise AttributeError(name)
 def spur(self):return [x for x in self.items if 'starter_spur' in x[2].get('tags',())]


class StarterGeometryTest(unittest.TestCase):
 def test_shared_source_and_existing_connector(self):
  self.assertIs(world.START_SPUR,atlas.START_SPUR)
  route=next(r for r in ROUTE_SOURCES if r.id=='starter_spur')
  self.assertIs(route.vertices,atlas.START_SPUR)
  self.assertEqual(dict(atlas.SECONDARY_ROADS)['cinder_creek_approach'][0],atlas.START_SPUR[-1])
  self.assertEqual(atlas.START_SPUR,((4650,2980),(6000,4300)))

 def test_world_strokes_keep_positions_and_styles(self):
  c=Canvas();draw_starter_spur(c,4300,2800,960,600)
  items=c.spur();self.assertEqual(len(items),2)
  self.assertEqual(items[0][1],(350,180,1700,1500))
  self.assertEqual(items[1][1],items[0][1])
  self.assertEqual((items[0][2]['width'],items[1][2]['width']),(38,2))
  self.assertEqual(items[1][2]['dash'],(12,16))

 def test_scaled_clip_with_both_endpoints_offscreen(self):
  view=(5000,3300,500,500);rect=(10,20,100,100)
  for detail in ('normal','low'):
   c=Canvas();draw_scaled_routes(c,view,rect,detail)
   lines=c.spur();self.assertEqual(len(lines),1)
   hit=clip_segment(*atlas.START_SPUR,view)
   expected=tuple(v for p in hit for v in (10+(p[0]-5000)/5,20+(p[1]-3300)/5))
   self.assertEqual(lines[0][1],expected)
   self.assertTrue(all(10<=x<=110 for x in lines[0][1][::2]))
   self.assertTrue(all(20<=y<=120 for y in lines[0][1][1::2]))

 def test_world_and_scaled_cull_unrelated_views(self):
  c=Canvas();draw_starter_spur(c,30000,20000,960,600)
  self.assertFalse(c.spur())
  draw_scaled_routes(c,(30000,20000,1000,1000),(0,0,100,100))
  self.assertFalse(c.spur())

 def test_vector_atlas_uses_shared_scaled_layer_once(self):
  c=Canvas();atlas.draw_atlas(c,(0,0,60000,40960),world.MAP_RECT)
  self.assertEqual(len(c.spur()),1)


class StarterGameTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();game.SAVE=str(Path(cls.temp.name)/'save.json')
  cls.root=tk.Tk();cls.root.withdraw();cls.g=game.Game(cls.root);cls.g.new_game();cls.g.dialog=None
 @classmethod
 def tearDownClass(cls):
  cls.g.audio.stop();cls.root.destroy();cls.temp.cleanup()

 def test_world_minimap_and_both_atlas_backgrounds(self):
  g=self.g;g.x,g.y=5000,3500;g.camx,g.camy=4300,2800
  g.canvas.delete('all');g.draw_far_terrain()
  self.assertEqual(len(g.canvas.find_withtag('starter_spur')),2)
  g.canvas.delete('all');g.draw_minimap(0,0,187,190)
  ids=g.canvas.find_withtag('starter_spur');self.assertEqual(len(ids),1)
  view=(1800.,700.,6400.,5600.);rect=(10,27,167,152)
  expected=[v for p in atlas.START_SPUR for v in world.point_on_map(*p,view,rect)]
  for a,b in zip(g.canvas.coords(ids[0]),expected):self.assertAlmostEqual(a,b)
  original=g.austellia_image
  try:
   bitmap=tk.PhotoImage(master=self.root,width=610,height=457)
   for image in (None,bitmap):
    g.austellia_image=image
    for zoom in (False,True):
     g.map_zoom=zoom;g.map_center=[5000,3500]
     g.canvas.delete('all');g.draw_map()
     self.assertEqual(len(g.canvas.find_withtag('starter_spur')),1,(bool(image),zoom))
  finally:g.austellia_image=original


if __name__=='__main__':unittest.main()
