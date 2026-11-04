#!/usr/bin/env python3
"""Regression tests for fair bandit spawns, 16x world, streaming, and saves.
Usage: xvfb-run -a python3 tests/frontier_hotfix_test.py
"""
import json
import os
import sys
import tempfile
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import game

def main():
    assert (game.WW, game.WH) == (19200, 12800)
    assert game.WW * game.WH == 16 * game.OLD_WW * game.OLD_WH
    with tempfile.TemporaryDirectory() as temp:
        game.SAVE = os.path.join(temp, "save.json")
        root = tk.Tk()
        root.withdraw()
        g = game.Game(root)
        g.new_game()
        g.dialog = None
        assert g.safe_timer >= 49
        assert g.in_safe_settlement(g.x, g.y)
        bandits = [a for a in g.actors if a.kind == "bandit"]
        assert bandits
        assert all(not g.in_safe_settlement(a.x, a.y) for a in bandits)
        assert all((a.x-g.x)**2+(a.y-g.y)**2 >= 950**2 for a in bandits)
        # Regression: random drifters should not fire on a new player.
        g.update_ai(.1)
        assert not any(not bullet[5] for bullet in g.bullets)
        # Manual save writes a file that can be independently read.
        g.x, g.y = 12345., 8765.
        g.money = 143
        assert g.save(manual=True)
        assert g.last_save_ok
        with open(game.SAVE, encoding="utf-8") as handle:
            disk = json.load(handle)
        assert disk["x"] == 12345 and disk["y"] == 8765
        assert disk["money"] == 143
        assert disk["save_version"] == game.VERSION
        g.camx, g.camy = 12000, 8400
        g.draw_far_terrain()
        g.render()
        g.map_open = True
        g.render()
        reloaded = game.Game(root)
        reloaded.continue_game()
        assert (reloaded.x, reloaded.y, reloaded.money) == (12345.,8765.,143)
        assert reloaded.safe_timer > 0
        root.destroy()
    print("OK: large world, spawn safety, manual save, reload, distant rendering")

if __name__ == "__main__":
    main()
