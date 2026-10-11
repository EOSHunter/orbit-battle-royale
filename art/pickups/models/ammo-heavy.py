"""Heavy ammo box. Concept: codex/concepts/v0.2/19-ammunition-boxes.png.

Same family as ammo-light (shared builder loaded from ammo-light.py): light gray
shell, dark lid and end caps with amber lights, latch with an amber window and
a red caliber band and labels. Origin at the bottom center on the ground.
"""

import importlib.util
import os

_spec = importlib.util.spec_from_file_location("ammo_light_shared", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ammo-light.py"))
_shared = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_shared)

BUDGET = (100, 800)


def build():
    m = _shared.ammo_box("ammo-heavy", L=0.58, W=0.28, H=0.25, band="ammo_red", handle=False, shells=False)
    return m.finish(BUDGET, texture_size=512)
