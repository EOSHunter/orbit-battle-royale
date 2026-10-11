"""Ruin rubble: a pile of broken carved blocks and stones.
Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png (block piles, bottom right).

About 3 x 2.5 m, 1.2 m high: cover-height prop. Some blocks still carry their
glyph channels and medallions; mossy tops, small stones around the base.
Origin at the base center.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)
S = "ruin_slate"


def carved(m, rng, center, size, rot, seed, glyph=True):
    """A block with masonry and a glyph fragment on its faces, then tumbled."""
    sx, sf, su = size
    cx, cf, cu = center

    def make():
        b = E.block(m, (cx, cf, cu), size, S, bevel=0.06, jitter=0.012, seed=seed)
        for s in (-1, 1):
            sk = []
            if glyph:
                a = cx + s * sx * 0.18
                sk = E.glyph_column(m, "f", s, cf + s * sf / 2, a, cu - su / 2 + 0.08, cu + su / 2 - 0.08,
                                    rings=(cu,) if s < 0 else (), stone=S, r=min(0.28, su * 0.32))
            elif s > 0:
                tr = [(cx - sx / 2 + 0.06, cu + su * 0.1), (cx - sx * 0.1, cu + su * 0.1), (cx - sx * 0.1, cu - su / 2 + 0.06)]
                E.strip(m, "f", s, cf + s * sf / 2, tr, 0.04, -0.004, 0.03, "glow_glyph")
            E.masonry(m, "f", s, cf + s * sf / 2, cx - sx / 2, cx + sx / 2, cu - su / 2, cu + su / 2, rng, E.SLATE,
                      course=(su, su), length=(0.5, 1.0), skip=sk, margin=0.04, crack_prob=0.5)
            E.masonry(m, "x", s, cx + s * sx / 2, cf - sf / 2, cf + sf / 2, cu - su / 2, cu + su / 2, rng, E.SLATE,
                      course=(su, su), length=(sf, sf), margin=0.04, crack_prob=0.6)
        return b

    b = E.transformed(m, make, rotate=rot, pivot=center)
    E.paint_up(b, "moss", prob=0.8, seed=seed)
    return b


def build():
    rng = random.Random(111)
    m = E.Model("ruin-rubble", category="ruins-kit", bevel=0.02, cage=0.05)
    carved(m, rng, (-0.4, 0.1, 0.35), (1.5, 0.75, 0.7), (2, -4, 12), 1)
    carved(m, rng, (0.75, -0.35, 0.3), (1.0, 0.8, 0.6), (-6, 5, -28), 2)
    carved(m, rng, (0.1, 0.25, 0.95), (1.1, 0.6, 0.55), (8, 18, 20), 3)
    carved(m, rng, (-1.2, -0.55, 0.22), (0.7, 0.6, 0.45), (14, -10, 50), 4, glyph=False)
    carved(m, rng, (1.25, 0.65, 0.25), (0.6, 0.6, 0.5), (-12, 10, 70), 5, glyph=False)
    # A broken drum of a pillar and loose stones.
    E.block(m, (-0.3, -0.85, 0.2), (0.5, 0.42, 0.4), S, bevel=0.05, jitter=0.04, seed=6, rot=(20, -14, 30), top_mat="moss", top_prob=0.7)
    for i in range(7):
        x, f = rng.uniform(-1.6, 1.6), rng.choice((-1, 1)) * rng.uniform(0.7, 1.2)
        r = rng.uniform(0.1, 0.22)
        E.rock(m, (x, f, r * 0.4), (r * 1.2, r, r * 0.8), rng.choice(["ruin_slate", "ruin_slate_dark"]), seed=20 + i, subdiv=1,
               cuts=3, floor=-0.4, top_mat="moss", top_prob=0.5)
    return m.finish(BUDGET, texture_size=1024)
