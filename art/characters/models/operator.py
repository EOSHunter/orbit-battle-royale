"""Operator: the playable expedition-suit character (5k-15k triangles), rigged and animated.

See _suit.py for the design, skeleton and animation clips.
"""

import importlib.util
import os

from kit import Model

# Loaded by path: this folder is not on sys.path (operator.py would shadow the stdlib).
_spec = importlib.util.spec_from_file_location("_suit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_suit.py"))
op = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(op)

BUDGET = (5000, 15000)


def build():
    op.use_palette("navy")
    m = Model("operator", category="characters", bevel=0.004, cage=0.008)
    op.build_operator(m, lod="player")
    m.marker("eye", f=0.12, u=1.68)
    return m.finish(BUDGET, texture_size=2048, before_export=lambda lows: op.rig(lows))
