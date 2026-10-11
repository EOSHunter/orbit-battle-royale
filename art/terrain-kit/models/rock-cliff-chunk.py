"""Cliff chunk: a large modular cliff piece with columnar jointing.
Concept: codex/concepts/v0.2/38-the-spine.png and 29-ringfall-terrain-overview.png
(fluted gray canyon walls with flat grassy tops).

About 8 m wide (x), 4.5 m deep, 9 m tall. Stack and overlap several (rotate
about u, mirror, scale 0.8-1.3) to build canyon walls and plateau edges; the
back is as finished as the front so it also works as a standalone crag.
Sheer faceted faces cut by near-vertical planes, flat ledged tops with moss,
vertical fluting and fine fractures baked from high-resolution twins.
Origin at the base center.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)


def build():
    m = E.Model("rock-cliff-chunk", category="terrain-kit", bevel=0.02, cage=0.1)
    common = dict(top_mat="moss", top_prob=0.95, top_thresh=0.75, columns=0.07, columns_freq=7.0, strata=0.03,
                  strata_freq=3.0, cut_z=(-0.12, 0.12), bumps=0.05, floor=-0.85)
    # Main wall mass: tall, cut into sheer facets, flat-topped.
    E.rock_pair(m, (0, 0, 4.3), (3.4, 2.1, 4.8), "rock_gray", seed=21, subdiv=3, cuts=14, cut_depth=0.42,
                flat_top=0.82, fine=0.018, fine_freq=9.0, **common)
    # Lower buttress blocks stepping down either side, and a capstone ledge.
    E.rock_pair(m, (2.9, 0.5, 2.1), (1.7, 1.6, 2.5), "rock_gray", seed=23, subdiv=2, cuts=9, cut_depth=0.4,
                flat_top=0.7, fine=0.03, fine_freq=7.0, **common)
    E.rock_pair(m, (-2.9, -0.4, 1.6), (1.6, 1.5, 2.0), "rock_gray", seed=29, subdiv=2, cuts=9, cut_depth=0.4,
                flat_top=0.65, fine=0.03, fine_freq=7.0, **common)
    cap = dict(common, floor=-0.6)
    E.rock_pair(m, (-0.8, 0.4, 8.5), (2.0, 1.6, 0.9), "rock_gray", seed=31, subdiv=2, cuts=8, cut_depth=0.4,
                flat_top=0.5, fine=0.03, fine_freq=6.0, **cap)
    return m.finish(BUDGET, texture_size=1024)
