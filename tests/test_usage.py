#!/usr/bin/env python3
"""spec.plan_for and spec.estimate_usage on tests/fixtures/data/usage.json; tests/test_usage.mjs runs the app's buildPlan/estimateUsage."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import spec

R = spec.load_rules(); F = json.load(open(os.path.join(ROOT, "tests", "fixtures", "data", "usage.json"), encoding="utf-8")); fails = n = 0
for c in F["plans"]:
    got = spec.plan_for(c["depth"], c["ratify"], c.get("rounds"), R); ok = got == c["expected"]; n += 1; fails += not ok
    print(("ok   " if ok else "FAIL ") + f"plan {c['depth']}{' + ratify' if c['ratify'] else ''}{' (' + str(c['rounds']) + ' rounds)' if 'rounds' in c else ''}")
for c in F["usage"]:
    r = spec.estimate_usage(c["input"], R); got = {k: r[k] for k in c["expected"]}; ok = got == c["expected"]; n += 1; fails += not ok
    print(("ok   " if ok else "FAIL ") + "usage: " + c["name"] + ("" if ok else f"  got {got}"))
print(f"plan_for/estimate_usage: {n - fails}/{n} cases pass"); sys.exit(1 if fails else 0)
