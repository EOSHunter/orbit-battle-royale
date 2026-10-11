"""Build every scripted model and report triangle counts against the budgets.

    blender -b --factory-startup --python art/tools/build_models.py -- [filter ...]

Each art/<category>/models/<asset-id>.py defines build(), which returns the
triangle count, and BUDGET = (min, max). A filter matches a category or an
asset id; with no filter everything is built. Outputs:
art/<category>/models/<asset-id>.blend and game/assets/models/<category>/<asset-id>.glb.
"""

import glob
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
scripts = sorted(glob.glob(os.path.join(REPO, "art", "*", "models", "*.py")))
results = []
for path in scripts:
    asset_id = os.path.splitext(os.path.basename(path))[0]
    category = os.path.basename(os.path.dirname(os.path.dirname(path)))
    if args and asset_id not in args and category not in args:
        continue
    spec = importlib.util.spec_from_file_location(asset_id.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    budget = getattr(mod, "BUDGET", (500, 1500))
    tris = mod.build()
    results.append((category, asset_id, tris, budget))

print("\nTRIANGLE REPORT")
failed = 0
for category, asset_id, tris, (lo, hi) in results:
    ok = lo <= tris <= hi
    failed += 0 if ok else 1
    print(f"  {'ok  ' if ok else 'FAIL'} {category}/{asset_id}: {tris} (budget {lo}-{hi})")
print(f"BUILT {len(results)} models, {failed} outside budget")
