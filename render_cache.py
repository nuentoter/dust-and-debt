"""Optional retained Tk Canvas backend for Dust & Debt.

Recycles Canvas items between complete frames when their drawing operation and
option names match. Reissues only changed coordinates/options, and preserves the
original painter's stacking order. No additional runtime dependencies.

This is opt-in while profiling and real-hardware acceptance are pending.
"""
import tkinter as tk


class RetainedCanvas(tk.Canvas):
    """Drop-in Canvas for the create_* primitives used by the game."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._previous = []
        self._current = []
        self._recording = False
        self.last_frame_stats = {}

    def begin_frame(self):
        if self._recording:
            raise RuntimeError("Nested retained Canvas frame")
        self._recording = True
        self._current = []
        self.last_frame_stats = dict(created=0, reused=0, moved=0,
                                     configured=0, deleted=0, reordered=0)

    def _draw(self, kind, coords, options):
        original = getattr(super(), "create_" + kind)
        if not self._recording:
            return original(*coords, **options)
        index = len(self._current)
        old = self._previous[index] if index < len(self._previous) else None
        # Do not retain an item with obsolete option names (e.g. an old dash
        # pattern); Tk would otherwise preserve settings absent this frame.
        if old and old[0] == kind and old[3].keys() == options.keys():
            item = old[1]
            if old[2] != coords:
                super().coords(item, *coords)
                self.last_frame_stats["moved"] += 1
            if old[3] != options:
                super().itemconfigure(item, **options)
                self.last_frame_stats["configured"] += 1
            self.last_frame_stats["reused"] += 1
        else:
            item = original(*coords, **options)
            self.last_frame_stats["created"] += 1
        self._current.append((kind, item, coords, dict(options)))
        return item

    def create_rectangle(self, *coords, **options):
        return self._draw("rectangle", coords, options)

    def create_oval(self, *coords, **options):
        return self._draw("oval", coords, options)

    def create_line(self, *coords, **options):
        return self._draw("line", coords, options)

    def create_polygon(self, *coords, **options):
        return self._draw("polygon", coords, options)

    def create_arc(self, *coords, **options):
        return self._draw("arc", coords, options)

    def create_text(self, *coords, **options):
        return self._draw("text", coords, options)

    def create_image(self, *coords, **options):
        return self._draw("image", coords, options)

    def end_frame(self):
        if not self._recording:
            raise RuntimeError("No retained Canvas frame active")
        old_ids = [entry[1] for entry in self._previous]
        new_ids = [entry[1] for entry in self._current]
        new_set = set(new_ids)
        for item in old_ids:
            if item not in new_set:
                super().delete(item)
                self.last_frame_stats["deleted"] += 1
        # New items are created at the top of the stack. Reestablish exact
        # painter order only if the sequence of item identities has changed.
        if old_ids != new_ids:
            for item in new_ids:
                super().tag_raise(item)
            self.last_frame_stats["reordered"] = len(new_ids)
        self._previous = self._current
        self._current = []
        self._recording = False

    def clear_retained(self):
        if self._recording:
            raise RuntimeError("Cannot clear retained items during a frame")
        super().delete("all")
        self._previous = []

