"""First-person arms: the operator's forearms, gloves and sleeves, rigged with the
operator's arm bones so weapon and healing animations can drive them later.
Concept: codex/concepts/v0.2/03-first-person-arms.png. Part of the character budget.
"""

import importlib.util
import os

from kit import Model

_spec = importlib.util.spec_from_file_location("_suit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_suit.py"))
op = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(op)

BUDGET = (800, 5000)
ARM_BONES = {"UpperChest", "LeftShoulder", "RightShoulder", "LeftUpperArm", "RightUpperArm",
             "LeftLowerArm", "RightLowerArm", "LeftHand", "RightHand"}


def build():
    op.use_palette("navy")
    m = Model("first-person-arms", category="characters", bevel=0.003, cage=0.006)
    op.build_operator(m, lod="arms", arms_only=True)
    return m.finish(BUDGET, texture_size=1024, before_export=lambda lows: op.rig(lows, with_animations=False, only=ARM_BONES))
