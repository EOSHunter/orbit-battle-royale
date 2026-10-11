"""Ruin floor slab: 4 x 4 m paving module.
Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png (floor tile with ring glyph).

Grid: x -2..2, f -2..2, walking surface at u = 0.4, so slabs tile flush on a
4 m grid. Border stones frame a central slab carved with a faint concentric
ring glyph; one corner stone has sunk and tilted. Origin at the base center.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (250, 1000)
S = "ruin_slate"
H = 0.4


def build():
    rng = random.Random(61)
    m = E.Model("ruin-floor-slab", category="ruins-kit", bevel=0.02, cage=0.06)
    E.block(m, (0, 0, H / 2), (2.9, 2.9, H), S, bevel=0.04, jitter=0.006, seed=1)
    # Border stones: four runs, each split in two, one corner tilted and sunk.
    k = 0
    for s in (-1, 1):
        for (a0, a1) in ((-2.0, -0.3), (-0.3, 1.45)) if s < 0 else ((-1.45, 0.4), (0.4, 2.0)):
            k += 1
            E.block(m, ((a0 + a1) / 2, s * 1.725, H / 2), (a1 - a0 - 0.02, 0.53, H), "ruin_slate_dark", bevel=0.045, jitter=0.008, seed=10 + k)
        for (a0, a1) in ((-1.45, 0.2), (0.2, 2.0)) if s < 0 else ((-2.0, -0.6), (-0.6, 1.45)):
            k += 1
            if s > 0 and a0 < -1.9:
                E.block(m, ((a0 + a1) / 2 + 0.02, s * 1.725 + 0.03, H / 2 - 0.07), (a1 - a0 - 0.05, 0.5, H), "ruin_slate_dark",
                        bevel=0.05, jitter=0.02, seed=10 + k, rot=(4, -5, 3))
                continue
            E.block(m, (s * 1.725, (a0 + a1) / 2, H / 2), (0.53, a1 - a0 - 0.02, H), "ruin_slate_dark", bevel=0.045, jitter=0.008, seed=10 + k)
    # A loose chip lying on the slab.
    E.block(m, (0.95, -0.6, H + 0.05), (0.26, 0.2, 0.12), S, bevel=0.03, jitter=0.02, seed=30, rot=(5, 3, 40))

    # Central slab: pavers around a ring glyph.
    E.masonry(m, "u", 1, H, -1.45, 1.45, -1.45, 1.45, rng, E.SLATE, course=(0.5, 0.9), length=(0.5, 1.1),
              skip=[(-1.0, 1.0, -1.0, 1.0)], margin=0.02, crack_prob=0.35)
    for r_out, r_in, mat, h in ((0.95, 0.82, S, 0.022), (0.8, 0.76, "glow_glyph", 0.008), (0.74, 0.56, S, 0.018),
                                (0.54, 0.5, "glow_glyph", 0.008), (0.48, 0.3, S, 0.022), (0.28, 0.25, "glow_glyph", 0.008)):
        E.face_ring(m, "u", 1, H, 0, 0, r_out, r_in, -0.004, h, mat, segs=32)
    E.face_disc(m, "u", 1, H, 0, 0, 0.22, -0.004, 0.02, S, segs=12)
    E.face_disc(m, "u", 1, H, 0, 0, 0.07, -0.004, 0.024, "glow_glyph", segs=8)
    for i in range(8):
        import math
        a = i * math.pi / 4 + math.pi / 8
        E.strip(m, "u", 1, H, [(0.58 * math.cos(a), 0.58 * math.sin(a)), (0.72 * math.cos(a), 0.72 * math.sin(a))], 0.03, -0.004, 0.012, "crack")
    # Corner squares between the ring and the paver field.
    for sx in (-1, 1):
        for sf in (-1, 1):
            E.face_rect(m, "u", 1, H, sx * 1.0 - 0.18, sx * 1.0 + 0.18, sf * 1.0 - 0.18, sf * 1.0 + 0.18, -0.004, 0.02, "ruin_slate_light")
    # Border pavers and moss in the joints.
    for s in (-1, 1):
        E.masonry(m, "u", 1, H, -2.0, 2.0, s * 1.725 - 0.265, s * 1.725 + 0.265, rng, ["ruin_slate_dark", "ruin_slate"],
                  course=(0.53, 0.53), length=(0.6, 1.2), margin=0.025)
        E.masonry(m, "u", 1, H, s * 1.725 - 0.265, s * 1.725 + 0.265, -1.46, 1.46, rng, ["ruin_slate_dark", "ruin_slate"],
                  course=(0.6, 1.2), length=(0.53, 0.53), margin=0.025)
        for axis in ("f", "x"):
            E.masonry(m, axis, s, s * 2.0, -2.0, 2.0, 0.0, H, rng, ["ruin_slate_dark"], course=(H, H), length=(0.6, 1.3), margin=0.02, crack_prob=0)
    # Moss creeping along the joints at the border: irregular low patches.
    import math
    for _ in range(9):
        a, b = rng.choice((-1, 1)) * rng.uniform(1.42, 1.5), rng.uniform(-1.9, 1.9)
        if rng.random() < 0.5:
            a, b = b, a
        r = rng.uniform(0.07, 0.16)
        pts = [(a + r * rng.uniform(0.5, 1.3) * math.cos(2 * math.pi * k / 8) * (1.8 if abs(a) < 1.4 else 0.6),
                b + r * rng.uniform(0.5, 1.3) * math.sin(2 * math.pi * k / 8) * (0.6 if abs(a) < 1.4 else 1.8)) for k in range(8)]
        E.face_poly(m, "u", 1, H, pts, -0.004, 0.026, rng.choice(["moss", "moss_dark"]))
    return m.finish(BUDGET, texture_size=1024)
