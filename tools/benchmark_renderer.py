#!/usr/bin/env python3
"""Compare legacy and experimental retained Canvas on identical camera states.

Run under xvfb-run -a. No audio playback or saves. Timings are diagnostic,
not FPS claims, and must be checked on the target Archcraft/X11 laptop.
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time
import tkinter as tk
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))


def measure(mode,frames):
    os.environ["DUST_AND_DEBT_RETAINED_CANVAS"]="1" if mode=="retained" else "0"
    os.environ["DUST_AND_DEBT_SILENT"]="1"
    from game import Game
    root=tk.Tk()
    root.withdraw()
    game=None
    try:
        game=Game(root)
        game.screen="playing"
        game.clock=8.
        game.weather_enabled=False
        game.graphics_quality="normal"
        game.x,game.y=4700.,3100.
        times=[]
        counters=[]
        for index in range(frames+2):
            # Warm up for two frames, then alternate stable and scrolling
            # scenes without advancing gameplay simulation.
            if index%4 in (2,3):
                game.camx,game.camy=4220.,2800.
            else:
                game.camx,game.camy=4220.+(index%20)*8,2800.
            start=time.perf_counter()
            game.render()
            root.update_idletasks()
            delta=(time.perf_counter()-start)*1000
            if index>=2:
                times.append(delta)
                if mode=="retained":
                    counters.append(dict(game.canvas.last_frame_stats))
        return {"mode":mode,"samples":len(times),
                "median_ms":round(statistics.median(times),3),
                "min_ms":round(min(times),3),
                "max_ms":round(max(times),3),
                "canvas_items":len(game.canvas.find_all()),
                "retained_counters":counters[:5]}
    finally:
        if game: game.audio.stop()
        root.destroy()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--frames",type=int,default=24)
    parser.add_argument("--mode",choices=("legacy","retained"))
    args=parser.parse_args()
    if args.frames<2:parser.error("--frames must be >= 2")
    if args.mode:
        print(json.dumps(measure(args.mode,args.frames),indent=2))
    else:
        # One clean process per renderer: avoid mode state leaking through
        # imports or shared Tk resource lifetimes.
        results=[]
        for mode in ("legacy","retained"):
            run=subprocess.run([sys.executable,__file__,"--frames",str(args.frames),
                                "--mode",mode],cwd=ROOT,capture_output=True,text=True,
                               check=True)
            results.append(json.loads(run.stdout))
        print(json.dumps(results,indent=2))


if __name__=="__main__":
    main()
