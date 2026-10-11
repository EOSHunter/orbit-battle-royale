"""Grass clump: pale alien grass, thin solid blades arching out of a tuft.
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (top-left grasses) and
the golden meadow grass of 38-the-spine.png.

About 1.3 m across and 0.8 m tall. Blades are narrow three-sided ribbons
(no alpha cards) in pale sage with a few dry ochre blades and a handful of
faint cyan seed tips. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def build():
    rng = random.Random(7)
    m = E.Model("veg-grass-clump", category="vegetation", bevel=0.002, cage=0.008)
    n = 42
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        r0 = rng.uniform(0.0, 0.16)
        L = rng.uniform(0.45, 0.95)
        out = rng.uniform(0.25, 0.75)          # how far the blade leans out
        bx, bf = r0 * math.cos(a), r0 * math.sin(a)
        dx, df = math.cos(a), math.sin(a)
        pts = []
        for k, t in enumerate((0.0, 0.35, 0.7, 1.0)):
            # Arch up and out, drooping near the tip.
            reach = out * L * (t ** 1.4)
            up = L * (math.sin(t * math.pi * 0.62) / math.sin(math.pi * 0.62)) * (1 - 0.35 * out * t * t)
            pts.append((bx + dx * reach, bf + df * reach, -0.04 + up))
        w = rng.uniform(0.011, 0.017)
        mat = "grass_dry" if rng.random() < 0.18 else "grass_pale"
        E.sweep(m, pts, [w, w * 0.9, w * 0.55, 0.0], mat, sides=3, flat=0.28, tip=True,
                normal=(dx, df, 0.3), phase=math.pi / 2)
    # A few seed stalks with faint glowing tips.
    for i in range(5):
        a = rng.uniform(0, 2 * math.pi)
        L = rng.uniform(0.75, 1.0)
        top = (math.cos(a) * 0.22 * L, math.sin(a) * 0.22 * L, L)
        E.sweep(m, [(0, 0, -0.03), (top[0] * 0.5, top[1] * 0.5, L * 0.55), top], [0.006, 0.005, 0.004], "grass_pale", sides=3)
        E.bud(m, top, (top[0] * 1.05, top[1] * 1.05, L + 0.06), 0.014, "glow_cyan")
    return m.finish(BUDGET, texture_size=512)
