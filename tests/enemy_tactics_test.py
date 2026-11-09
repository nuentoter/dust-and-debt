#!/usr/bin/env python3
"""v2.8 enemy tactics smoke and integration regression."""
import os,sys,tempfile,tkinter as tk,math
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from enemy_tactics import ARCHETYPES,archetype,morale,should_surrender,movement,cover_goal
import game

def main():
 assert len(ARCHETYPES)>=5
 raider=game.Actor(100,100,'bandit','Drifter',100,100,80)
 hunter=game.Actor(150,100,'bounty_target','Vulture Jack',145,145,86)
 boss=game.Actor(200,100,'mission_crow','Crow',240,240,105)
 assert archetype(boss)=='boss'
 assert not should_surrender(boss,0,True)
 assert not should_surrender(hunter)
 hunter.hp=40
 assert should_surrender(hunter)
 assert morale(hunter)<morale(raider)
 assert movement(raider,300,0,300)[0]>0
 assert movement(raider,70,0,70)[0]<0
 cover=cover_goal(game.Actor(0,0,'bandit','Lookout'),100,0,[(40,35,18,True)])
 assert cover is None or len(cover)==2
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None;g.safe_timer=0
  # The wounded named bounty can be captured alive, and mission enemies
  # remain exempt from nonlethal surrender to avoid story softlocks.
  g.contract={'name':'Vulture Jack','location':[6500,6500],'reward':60,'status':'hunting','finished':False}
  hunter.hp=40;g.actors.append(hunter)
  assert g.check_surrender(hunter)
  assert g.bounty_state()=='surrendered'
  assert not g.check_surrender(boss)
  # A free-roam hostile warns and aims before creating a shot.
  enemy=game.Actor(760,610,'bandit','Roadside Outlaw',100,100,72)
  g.actors.append(enemy)
  g.x,g.y=610,610
  g.law_status='PEACE';g.safe_timer=0
  g.actors=[a for a in g.actors if a is enemy or a is hunter]
  g.actors.remove(hunter)
  g.update_ai(.05)
  assert getattr(enemy,'aim_timer',0)>0,'Enemy should telegraph shot'
  assert not g.bullets,'No immediate hostile projectile before warning'
  g.update_ai(.95)
  assert g.bullets or not g.line_of_fire(enemy.x,enemy.y,g.x,g.y)
  # The original Crow mission remains alive after damage, no surrender state.
  boss.hp=45
  assert not g.check_surrender(boss)
  g.audio.stop();root.destroy()
 print('OK: enemy profiles, wounded morale, story exemption, shot telegraph')

if __name__=='__main__':main()
