"""Glass shard cluster: jagged black volcanic glass from the Glass Basin.
Concept: codex/concepts/v0.2/35-glass-basin.png (sharp black glass outcrops).

About 3.2 x 2.6 m, up to 2.4 m tall. Leaning, faceted obsidian shards (some
snapped off with slanted broken tops) bursting from a fractured glass base.
Glossy black with paler chipped edges. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def build():
    rng = random.Random(127)
    m = E.Model("glass-shard-cluster", category="terrain-kit", bevel=0.006, cage=0.03)
    E.rock_pair(m, (0, 0, 0.12), (1.5, 1.2, 0.4), "obsidian", seed=3, subdiv=2, cuts=9, cut_depth=0.4, bumps=0.2,
                floor=-0.3, fine=0.03, fine_freq=8.0)
    E.rock_pair(m, (1.1, 0.7, 0.15), (0.6, 0.5, 0.45), "basalt", seed=5, subdiv=1, cuts=4, cut_depth=0.3, bumps=0.2,
                floor=-0.3, fine=0.04, fine_freq=6.0, top_mat="moss", top_prob=0.5, top_thresh=0.8)
    specs = [(0.0, 0.0, 2.4, 0.42), (0.55, -0.3, 1.7, 0.32), (-0.6, 0.25, 1.9, 0.34), (-0.25, -0.55, 1.2, 0.26),
             (0.85, 0.35, 1.1, 0.24), (-1.05, -0.2, 1.0, 0.22), (0.3, 0.6, 1.4, 0.26), (-0.5, 0.75, 0.8, 0.2),
             (1.25, -0.5, 0.7, 0.18), (-1.3, 0.5, 0.6, 0.17), (0.2, -0.95, 0.65, 0.18), (1.5, 0.1, 0.45, 0.14)]
    for i, (x, f, h, r) in enumerate(specs):
        d = math.hypot(x, f) or 1.0
        lean = (x / d * rng.uniform(0.15, 0.4) * min(1.0, d * 1.5), f / d * rng.uniform(0.15, 0.4) * min(1.0, d * 1.5))
        E.shard(m, (x, f, 0.2), h, r, "obsidian", seed=200 + i, sides=rng.choice((4, 5, 5, 6)), lean=lean,
                top_cut=rng.uniform(0.18, 0.35) if i in (2, 4, 9) else 0.0, sink=0.35)
    return m.finish(BUDGET, texture_size=1024)
