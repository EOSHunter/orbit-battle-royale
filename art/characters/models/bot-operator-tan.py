"""Bot operator, tan variant: a light build of the operator for bots (1k-3k triangles).

Same skeleton, silhouette and animation clips as the player operator (see _suit.py),
with fewer sides, fewer pouches and a smaller texture so 59 bots stay cheap.
"""

import importlib.util
import os

from kit import Model

_spec = importlib.util.spec_from_file_location("_suit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_suit.py"))
op = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(op)

BUDGET = (1000, 3000)


def build():
    op.use_palette("tan")
    m = Model("bot-operator-tan", category="characters", bevel=0.005, cage=0.008)
    op.build_operator(m, lod="bot")
    m.marker("eye", f=0.12, u=1.68)
    return m.finish(BUDGET, texture_size=512, before_export=lambda lows: op.rig(lows))
