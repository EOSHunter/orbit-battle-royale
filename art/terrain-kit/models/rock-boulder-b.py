"""Boulder B: a flat, layered sandstone-gray slab boulder with a broken step.
Concept: codex/concepts/v0.2/38-the-spine.png (layered plateau rock) and
29-ringfall-terrain-overview.png.

About 3.4 x 2.6 m and 1.3 m tall: crouch cover and a step-up ledge. Strata
ledges in the silhouette, finer bedding lines and pitting baked from a
high-resolution twin, moss on the flat tops. Origin at the base center.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def build():
    m = E.Model("rock-boulder-b", category="terrain-kit", bevel=0.01, cage=0.06)
    E.rock_pair(m, (0, 0, 0.42), (1.7, 1.25, 0.75), "rock_tan", seed=13, subdiv=3, cuts=8, cut_depth=0.3, bumps=0.08,
                floor=-0.55, bias_up=0.8, strata=0.1, strata_freq=7.0, top_mat="moss", top_prob=0.9, top_thresh=0.7,
                fine=0.03, fine_freq=6.0, rot_u=-15)
    E.rock_pair(m, (-1.0, 0.8, 0.2), (0.9, 0.7, 0.38), "rock_tan", seed=17, subdiv=2, cuts=6, cut_depth=0.3, bumps=0.08,
                floor=-0.5, bias_up=0.8, strata=0.1, strata_freq=6.0, top_mat="moss", top_prob=0.9, top_thresh=0.7,
                fine=0.035, fine_freq=5.0, rot_u=25)
    return m.finish(BUDGET, texture_size=1024)
