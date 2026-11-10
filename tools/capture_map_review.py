#!/usr/bin/env python3
"""Silent fixed-camera screenshots and Xvfb render measurements.

Run under Xvfb. Pillow is optional development tooling for PNG capture;
--metrics-only requires only the game's standard-library dependencies.
Measurements describe this process/display, not the player's hardware FPS.
"""
import argparse
import json
import math
import os
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))


def git(*args):
    result=subprocess.run(['git',*args],cwd=ROOT,capture_output=True,text=True,check=True)
    return result.stdout.strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--samples',type=int,default=10)
    parser.add_argument('--metrics-only',action='store_true')
    args=parser.parse_args()
    if args.samples<2:parser.error('--samples must be at least 2')
    os.environ['DUST_AND_DEBT_SILENT']='1'
    import tkinter as tk
    started=time.perf_counter()
    import game
    import natural_terrain
    from new_austellia import TOWN_BY_ID,BRIDGE_DECKS,ROADS
    from frontier_destinations import DESTINATION_BY_ID
    from tools.audit_routes import audit
    import_seconds=time.perf_counter()-started
    capture=None
    if not args.metrics_only:
        from PIL import ImageGrab
        capture=ImageGrab.grab
    camp=DESTINATION_BY_ID['camp_everwood']
    fish=DESTINATION_BY_ID['fish_northstar_e']
    a,b=natural_terrain.RIDGES[0][1][:2]
    ridge_y=a[1]+(10200-a[0])*(b[1]-a[1])/(b[0]-a[0])
    crossing=next(d for d in BRIDGE_DECKS if d.water=='Blackwater Town Crossing')
    desert_a,desert_b=ROADS[7][3:5]
    scenes=(
        ('starter_seam','Cinder Creek eastern/southern seam',(game.OLD_WW-100,game.OLD_WH-100)),
        ('grass_junction','Larkfield grassland junction',TOWN_BY_ID['larkfield'][2:4]),
        ('desert_road','Dustwell desert wagon approach',TOWN_BY_ID['dustwell'][2:4]),
        ('desert_outskirts','Copper Sands wagon road',tuple((a+b)/2 for a,b in zip(desert_a,desert_b))),
        ('forest_trail','Everwood branch trail',camp.route[1]),
        ('river_bridge','Blackwater town bridge',(crossing.x,crossing.y)),
        ('fishing_bank','Northstar east fishing bank',(fish.x,fish.y)),
        ('camp_clearing','Everwood named camp',(camp.x,camp.y)),
        ('legacy_grid_ridge','Graystone ridge at former grid line',(10200,ridge_y)),
    )
    args.output.mkdir(parents=True,exist_ok=True)
    data={'source_commit':git('rev-parse','HEAD'),
          'game_sources_dirty':bool(git('diff','--','game.py','frontier_world.py','new_austellia.py','natural_terrain.py')),
          'geometry_sha256':audit()['source']['geometry_sha256'],
          'seed':1889,'samples_per_view':args.samples,'warmup_frames':1,
          'viewport':[game.VW,game.VH],
          'timing_scope':'Game.render + Tk.update_idletasks; screenshot encoding excluded',
          'p95_method':'nearest rank','python':sys.version.split()[0],
          'display':os.environ.get('DISPLAY'),'png_capture':bool(capture),
          'game_import_seconds':round(import_seconds,6),
          'rocks':len(natural_terrain.ROCKS),
          'solid_rocks':sum(rock[3] for rock in natural_terrain.ROCKS),'views':[]}
    root=None;g=None
    with tempfile.TemporaryDirectory() as tmp:
        try:
            game.SAVE=str(Path(tmp)/'save.json')
            random.seed(1889)
            root=tk.Tk()
            if root.winfo_screenwidth()<game.VW or root.winfo_screenheight()<game.VH:
                raise RuntimeError('Virtual screen is smaller than the game; use xvfb-run -s \"-screen 0 1280x1024x24\"')
            started=time.perf_counter()
            g=game.Game(root);g.new_game();g.dialog=None;g.toast=[]
            g.clock=8.
            for timer in root.tk.splitlist(root.tk.call('after','info')):root.after_cancel(timer)
            root.geometry(str(game.VW)+'x'+str(game.VH)+'+0+0')
            root.update()
            data['game_init_seconds']=round(time.perf_counter()-started,6)
            for detail in ('normal','low'):
                g.graphics_quality=detail
                for key,title,(x,y) in scenes:
                    g.x,g.y=(x+140,y+180) if key=='legacy_grid_ridge' else (x,y)
                    g.camx=max(0,min(game.WW-game.VW,int(x-game.VW/2)))
                    g.camy=max(0,min(game.WH-game.VH,int(y-game.VH/2)))
                    g.render();root.update_idletasks()
                    times=[];counts=[]
                    for _ in range(args.samples):
                        started=time.perf_counter()
                        g.render();root.update_idletasks()
                        times.append((time.perf_counter()-started)*1000)
                        counts.append(len(g.canvas.find_all()))
                    view={'id':key,'title':title,'detail':detail,'world_xy':[x,y],
                          'camera':[g.camx,g.camy],'player_xy':[g.x,g.y],
                          'focus_solid_foot':g.solid(x,y,11),
                          'focus_solid_horse':g.solid(x,y,16),
                          'p50_ms':round(statistics.median(times),3),
                          'p95_ms':round(sorted(times)[math.ceil(.95*len(times))-1],3),
                          'max_canvas_items':max(counts),
                          'frame_samples_ms':[round(t,3) for t in times]}
                    if capture:
                        filename=key+'_'+detail+'.png'
                        x0,y0=g.canvas.winfo_rootx(),g.canvas.winfo_rooty()
                        capture(bbox=(x0,y0,x0+game.VW,y0+game.VH),
                                xdisplay=os.environ.get('DISPLAY')).save(args.output/filename)
                        view['capture']=filename
                    data['views'].append(view)
                    print(detail,key,view['p50_ms'],view['p95_ms'],view['max_canvas_items'],flush=True)
            data['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        finally:
            if g is not None:g.audio.stop()
            if root is not None:root.destroy()
    (args.output/'metrics.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Wrote',args.output/'metrics.json',flush=True)


if __name__=='__main__':main()
