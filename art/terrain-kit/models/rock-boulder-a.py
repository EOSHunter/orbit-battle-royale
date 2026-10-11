"""Boulder A: a big rounded-angular basalt-gray boulder with a smaller companion.
Concept: codex/concepts/v0.2/29-ringfall-terrain-overview.png and the mossy
rocks of 32-ancient-ruins-kit.png.

About 3.2 x 2.4 m and 1.9 m tall: full cover. Faceted silhouette, fine cracks
and pitting baked from a high-resolution twin, moss on the upward faces.
Origin at the base center.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def build():
    m = E.Model("rock-boulder-a", category="terrain-kit", bevel=0.01, cage=0.06)
    E.rock_pair(m, (0, 0, 0.62), (1.35, 1.1, 1.05), "rock_gray", seed=5, subdiv=3, cuts=9, cut_depth=0.32, bumps=0.14,
                floor=-0.55, top_mat="moss", top_prob=0.9, top_thresh=0.6, fine=0.035, fine_freq=6.0, rot_u=10)
    E.rock_pair(m, (1.35, -0.75, 0.3), (0.6, 0.5, 0.45), "rock_gray", seed=9, subdiv=2, cuts=6, cut_depth=0.3, bumps=0.12,
                floor=-0.5, top_mat="moss", top_prob=0.9, top_thresh=0.65, fine=0.04, fine_freq=5.0, rot_u=40)
    return m.finish(BUDGET, texture_size=1024)
