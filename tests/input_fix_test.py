#!/usr/bin/env python3
"""Regression for sheriff/jail interaction and horse/Dead Eye separation."""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game

class Key:
 def __init__(self,keysym,state=0):
  self.keysym=keysym;self.state=state

def tap(g,key,state=0):
 g.key_down(Key(key,state))
 g.key_up(Key(key,state))

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  sheriff=next(a for a in g.actors if a.name=='Sheriff Bell')
  g.x,g.y=418,505
  assert g.near_door()=='Sheriff', 'Test must overlap the jail entrance'
  assert 0<((g.x-sheriff.x)**2+(g.y-sheriff.y)**2)**.5<64
  # Bare E talks with the sheriff and starts the original story.
  tap(g,'e')
  assert g.interior is None
  assert g.stage==1 and g.dialog and g.enemies_remaining('hollow')==5
  g.dialog=None
  # Event modifier Shift+E enters explicitly, even if shift key wasn't tracked.
  tap(g,'e',1)
  assert g.interior=='Sheriff'
  g.leave_interior()
  # No NPC nearby: bare E must not enter the building on its own.
  g.x,g.y=418,450
  g.dialog=None
  tap(g,'e')
  assert g.interior is None
  # Shift+E remains the only entry command.
  tap(g,'e',1)
  assert g.interior=='Sheriff'
  g.leave_interior()
  # Mounting cannot enable or retain the Dead Eye screen overlay.
  g.x,g.y=g.horse_x,g.horse_y
  g.deadeye_active=True
  tap(g,'h')
  assert g.mounted and not g.deadeye_active
  g.render()
  # Dust weather does not add a giant yellow filter rectangle.
  g.weather_kind=lambda:'dust'
  g.render()
  colored=[]
  for item in g.canvas.find_all():
   if g.canvas.type(item)=='rectangle':
    if g.canvas.itemcget(item,'fill').lower()=='#aa814e':
     colored.append(item)
  assert not colored, 'Dust and Dead Eye should look different'
  root.destroy()
 print('OK: sheriff interaction, Shift+E door, horse Dead Eye, weather visuals')
if __name__=='__main__':main()
