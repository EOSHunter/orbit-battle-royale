"""Basalt columns: a cluster of hexagonal basalt columns of stepped heights.
Concept: codex/concepts/v0.2/35-glass-basin.png and 29-ringfall-terrain-overview.png
(dark volcanic formations around the basin).

About 3.6 x 3 m, up to 3.4 m tall: climbable stepped columns. Tilted chamfered
tops, horizontal joint cracks and chipped edges baked, moss on some tops.
Origin at the base center.
"""

import math
import os
import random
import sys

import bmesh

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def column(m, rng, cx, cf, r, h, mat="basalt"):
    """Hex prism with a tilted top and a chamfer ring: 32 triangles."""
    rot = rng.uniform(0, math.pi / 3)
    tilt = (rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12))
    bm = bmesh.new()
    corners = []
    for k in range(6):
        a = rot + k * math.pi / 3
        rr = r * rng.uniform(0.92, 1.05)
        corners.append((cx + rr * math.cos(a), cf + rr * math.sin(a)))

    def top_h(x, f):
        return h + tilt[0] * (x - cx) + tilt[1] * (f - cf)

    lo = [bm.verts.new(E.V((x, f, -0.3))) for x, f in corners]
    mid = [bm.verts.new(E.V((x, f, top_h(x, f) - 0.07))) for x, f in corners]
    hi = [bm.verts.new(E.V((cx + (x - cx) * 0.86, cf + (f - cf) * 0.86, top_h(x, f) + rng.uniform(-0.02, 0.02)))) for x, f in corners]
    for k in range(6):
        j = (k + 1) % 6
        bm.faces.new((lo[k], lo[j], mid[j], mid[k]))
        bm.faces.new((mid[k], mid[j], hi[j], hi[k]))
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    obj = E._finish_bm(m, bm, mat, "body", "column", False, top_mat="moss", top_thresh=0.9, top_prob=0.35, rng=rng)
    # Joint cracks and chips (baked): thin dark bands around the shaft at random heights.
    for _ in range(int(h / 0.7)):
        u = rng.uniform(0.2, h - 0.3)
        ring = [(cx + (x - cx) * 1.01, cf + (f - cf) * 1.01) for x, f in corners]
        bmc = bmesh.new()
        a = [bmc.verts.new(E.V((x, f, u))) for x, f in ring]
        b = [bmc.verts.new(E.V((x, f, u + 0.025))) for x, f in ring]
        inner = [bmc.verts.new(E.V((cx + (x - cx) * 0.9, cf + (f - cf) * 0.9, u + 0.012))) for x, f in corners]
        for k in range(6):
            j = (k + 1) % 6
            bmc.faces.new((a[k], a[j], b[j], b[k]))
            bmc.faces.new((b[k], b[j], inner[j], inner[k]))
            bmc.faces.new((inner[k], inner[j], a[j], a[k]))
        E._finish_bm(m, bmc, "crack", "body", "joint", True)
    return obj


def build():
    rng = random.Random(117)
    m = E.Model("rock-basalt-columns", category="terrain-kit", bevel=0.01, cage=0.04)
    r = 0.36
    dx = r * math.sqrt(3)
    k = 0
    for row in range(-2, 3):
        for col in range(-2, 3):
            x = col * dx + (row % 2) * dx / 2
            f = row * r * 1.5
            d = math.hypot(x, f * 1.2)
            if d > 1.75:
                continue
            k += 1
            h = max(0.35, 3.3 - d * 1.45 + rng.uniform(-0.45, 0.35))
            column(m, rng, x + rng.uniform(-0.03, 0.03), f + rng.uniform(-0.03, 0.03), r * 0.97, h)
    # Toppled column sections at the foot.
    for i, (x, f, a) in enumerate(((1.6, -1.2, 20), (-1.7, 0.9, -35))):
        E.block(m, (x, f, 0.22), (1.1, 0.55, 0.5), "basalt", bevel=0.06, jitter=0.03, seed=40 + i, rot=(0, 8, a), top_mat="moss", top_prob=0.4)
    return m.finish(BUDGET, texture_size=1024)
