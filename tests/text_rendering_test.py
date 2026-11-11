#!/usr/bin/env python3
"""Persistent text fonts and bounded HUD region headings (Xvfb, silent)."""
import os
from pathlib import Path
import sys
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DUST_AND_DEBT_SILENT','1')
import game
from new_austellia import REGIONS,TOWNS
from frontier_world import WAYSTATIONS


class TextRenderingTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();game.SAVE=str(Path(cls.temp.name)/'save.json')
  cls.root=tk.Tk();cls.root.withdraw();cls.g=game.Game(cls.root);cls.g.new_game();cls.g.dialog=None
 @classmethod
 def tearDownClass(cls):
  cls.g.audio.stop();cls.root.destroy();cls.temp.cleanup()

 def test_font_survives_canvas_clear_and_reuses_dynamic_labels(self):
  g=self.g;font=g.text_font(13,True);count=len(g.text_fonts)
  for i in range(10):
   g.canvas.delete('all');g.draw_text(20,20,'Balance '+str(i),13,bold=True)
   self.assertIs(g.text_font(13,True),font)
  self.assertEqual(len(g.text_fonts),count)
  self.assertIn(str(font),self.root.tk.splitlist(self.root.tk.call('font','names')))
  self.assertIsNot(g.text_font(13,False),font)

 def test_named_and_original_tuple_fonts_have_same_geometry(self):
  g=self.g
  for size,bold in ((9,False),(11,True),(13,False),(22,True)):
   for anchor in ('nw','center'):
    g.canvas.delete('all')
    legacy=g.canvas.create_text(100,100,text='Jesse Vale — ★',anchor=anchor,
                                font=(g.font,size,'bold' if bold else 'normal'))
    g.draw_text(100,100,'Jesse Vale — ★',size,bold=bold,anchor=anchor,shadow=False)
    cached=g.canvas.find_all()[-1]
    self.assertEqual(g.canvas.bbox(legacy),g.canvas.bbox(cached),(size,bold,anchor))

 def test_all_named_region_headers_fit_their_available_width(self):
  names={r[0] for r in REGIONS}|{t[1] for t in TOWNS}|{s[1] for s in WAYSTATIONS}
  for name in names:
   heading='12:59 PM  |  '+name.upper()
   text,size=self.g.fit_text(heading,292,bold=True)
   self.assertLessEqual(self.g.text_font(size,True).measure(text),292,name)
   self.assertTrue(text.startswith('12:59 PM'),name)
   self.assertGreaterEqual(size,9)

 def test_short_text_is_unchanged_and_long_text_has_a_safe_fallback(self):
  self.assertEqual(self.g.fit_text('8:00 AM  |  GALLOWAY',292,bold=True),('8:00 AM  |  GALLOWAY',11))
  text,size=self.g.fit_text('A VERY LONG WESTERN REGION '*5,90,bold=True)
  self.assertTrue(text.endswith('…'))
  self.assertLessEqual(self.g.text_font(size,True).measure(text),90)
  self.assertEqual(self.g.fit_text('Long',0,bold=True),('',9))

 def test_real_hud_heading_and_shadow_stay_inside_panel(self):
  g=self.g;g.clock=8.
  for name in ('Cinder Ridge Badlands','Pineheart Trading Post','Sablestone Territory'):
   with patch.object(g,'region_name',return_value=name):
    g.canvas.delete('all');g.draw_hud()
   text,_=g.fit_text('8:00 AM  |  '+name.upper(),292,bold=True)
   labels=[item for item in g.canvas.find_all() if g.canvas.type(item)=='text'
           and g.canvas.itemcget(item,'text')==text]
   self.assertEqual(len(labels),2)
   for item in labels:
    x0,y0,x1,y1=g.canvas.bbox(item)
    self.assertGreaterEqual(x0,640);self.assertLessEqual(x1,938)
    self.assertGreaterEqual(y0,19);self.assertLess(y1,43)


if __name__=='__main__':unittest.main()
