"""Glass spire: a tall jagged black glass formation from the Glass Basin.
Concept: codex/concepts/v0.2/35-glass-basin.png (spiky obsidian spires) and
29-ringfall-terrain-overview.png.

About 11 m tall on a 5 x 4.5 m footprint: a landmark and long-range cover.
A main twisting faceted spire with stepped facet breaks, leaning secondary
blades, snapped stubs and a fractured base. Origin at the base center.
"""

import math
import os
import random
import sys

import bmesh

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def spire(m, rng, base, height, radius, sides, levels, lean, twist=0.35, mat="obsidian"):
    """Faceted spire: irregular rings narrowing in steps (facet breaks) to an off-center point."""
    bx, bf, bu = base
    angs = [2 * math.pi * k / sides + rng.uniform(-0.3, 0.3) for k in range(sides)]
    rad = [rng.uniform(0.75, 1.15) for _ in range(sides)]
    bm = bmesh.new()
    rings = []
    for li in range(levels):
        t = li / levels
        h = -0.5 + t * height
        shrink = (1 - t) ** 0.9
        # Facet break: every other level steps in sharply and twists.
        step = 0.82 if li % 2 else 1.0
        rot = twist * t + rng.uniform(-0.08, 0.08)
        ring = []
        for k, a in enumerate(angs):
            rr = radius * shrink * step * rad[k] * rng.uniform(0.92, 1.06)
            ring.append(bm.verts.new(E.V((bx + lean[0] * h + rr * math.cos(a + rot), bf + lean[1] * h + rr * math.sin(a + rot), bu + h))))
        rings.append(ring)
    apex = bm.verts.new(E.V((bx + lean[0] * height, bf + lean[1] * height, bu + height - 0.5)))
    for li in range(levels - 1):
        a, b = rings[li], rings[li + 1]
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new((a[k], a[j], b[j], b[k]))
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new((rings[-1][k], rings[-1][j], apex))
    bm.faces.new(list(reversed(rings[0])))
    return E._finish_bm(m, bm, mat, "body", "spire", False)


def build():
    rng = random.Random(137)
    m = E.Model("glass-spire", category="terrain-kit", bevel=0.01, cage=0.05)
    spire(m, rng, (0, 0, 0), 11.0, 1.3, 8, 8, (0.06, -0.03))
    spire(m, rng, (1.1, 0.4, 0), 6.5, 0.75, 6, 4, (0.22, 0.08), twist=-0.4)
    spire(m, rng, (-1.0, -0.5, 0), 7.5, 0.8, 6, 4, (-0.18, -0.1), twist=0.5)
    spire(m, rng, (-0.3, 1.1, 0), 4.5, 0.6, 5, 3, (-0.05, 0.3))
    for i, (x, f, h, r) in enumerate(((1.9, -0.8, 2.2, 0.4), (-1.9, 0.7, 1.8, 0.36), (0.6, -1.6, 1.5, 0.3),
                                      (2.2, 1.0, 1.2, 0.28), (-1.5, -1.6, 1.3, 0.3))):
        d = math.hypot(x, f)
        E.shard(m, (x, f, 0.1), h, r, "obsidian", seed=300 + i, sides=5, lean=(x / d * 0.35, f / d * 0.35),
                top_cut=0.3 if i % 2 else 0.0, sink=0.35)
    E.rock_pair(m, (0, 0, 0.1), (2.3, 2.0, 0.6), "obsidian", seed=7, subdiv=2, cuts=10, cut_depth=0.4, bumps=0.2,
                floor=-0.3, fine=0.025, fine_freq=8.0)
    return m.finish(BUDGET, texture_size=1024)
