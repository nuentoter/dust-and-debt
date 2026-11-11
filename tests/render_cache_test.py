#!/usr/bin/env python3
"""Retained renderer object identity, ordering, and live-game smoke tests."""
import os
import sys
import tkinter as tk
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from render_cache import RetainedCanvas


def run():
    root=tk.Tk()
    root.withdraw()
    canvas=RetainedCanvas(root,width=160,height=100)
    try:
        canvas.begin_frame()
        rect=canvas.create_rectangle(2,3,22,24,fill="red")
        label=canvas.create_text(50,12,text="hello",fill="white")
        canvas.end_frame()
        assert canvas.last_frame_stats["created"]==2

        canvas.begin_frame()
        assert canvas.create_rectangle(2,3,22,24,fill="red")==rect
        assert canvas.create_text(50,12,text="hello",fill="white")==label
        canvas.end_frame()
        assert canvas.last_frame_stats["created"]==0
        assert canvas.last_frame_stats["moved"]==0
        assert canvas.last_frame_stats["configured"]==0
        assert canvas.last_frame_stats["reordered"]==0

        canvas.begin_frame()
        assert canvas.create_rectangle(3,3,23,24,fill="blue")==rect
        assert canvas.create_text(50,12,text="next",fill="white")==label
        canvas.end_frame()
        assert canvas.last_frame_stats["moved"]==1
        assert canvas.last_frame_stats["configured"]==2
        assert canvas.coords(rect)==[3.0,3.0,23.0,24.0]
        assert canvas.itemcget(rect,"fill")=="blue"
        assert canvas.itemcget(label,"text")=="next"

        # A changed option set must not inherit obsolete state.
        canvas.begin_frame()
        replacement=canvas.create_line(1,2,12,20,fill="gold",dash=(2,3))
        canvas.end_frame()
        assert replacement!=rect
        assert len(canvas.find_all())==1
        canvas.begin_frame()
        plain=canvas.create_line(1,2,12,20,fill="gold")
        canvas.end_frame()
        assert plain!=replacement
        assert canvas.itemcget(plain,"dash")==""

        # A new item inserted at the front must keep painter order.
        canvas.begin_frame()
        front=canvas.create_oval(0,0,20,20,fill="green")
        rear=canvas.create_line(1,2,12,20,fill="gold")
        canvas.end_frame()
        assert canvas.find_all()==(front,rear)
        canvas.begin_frame()
        canvas.create_oval(0,0,20,20,fill="green")
        canvas.create_line(1,2,12,20,fill="gold")
        canvas.end_frame()
        assert canvas.last_frame_stats["reordered"]==0
        canvas.clear_retained()
        assert not canvas.find_all()
    finally:
        root.destroy()

    # Exercise actual Game.render early-return and full world paths.
    os.environ["DUST_AND_DEBT_RETAINED_CANVAS"]="1"
    os.environ["DUST_AND_DEBT_SILENT"]="1"
    from game import Game
    root=tk.Tk()
    root.withdraw()
    game=None
    try:
        game=Game(root)
        assert isinstance(game.canvas,RetainedCanvas)
        game.render()
        count=len(game.canvas.find_all())
        assert count>0
        game.render()
        assert len(game.canvas.find_all())==count
        assert game.canvas.last_frame_stats["created"]==0
        game.screen="playing"
        game.render()
        assert len(game.canvas.find_all())>0
        game.render()
        assert len(game.canvas.find_all())>0
        game.screen="title"
        game.render()
        assert len(game.canvas.find_all())>0
    finally:
        if game:game.audio.stop()
        root.destroy()
    print("Retained Canvas tests OK")


if __name__=="__main__":
    run()
