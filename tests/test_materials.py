#!/usr/bin/env python3
"""scripts/materials.py plan() must match the app's planMaterials() (tests/test_data.mjs runs the same cases)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import materials, spec

R = spec.load_rules(); OWN, SHARED = R["OWN_BUDGET"], R["SHARED_BUDGET"]
it = lambda tag, n, **kw: {"tag": tag, "chars": n, "added_at": kw.pop("added_at", "1"), **kw}
tags = lambda l: [a["tag"] for a in l]
note, big = it("PW1", 5000, pinned=True), it("PW2", 200000)
cases = [
    ("tools: pinned note in full, file only searchable", lambda: (p := materials.plan([note, big], OWN, True)) and tags(p["full"]) == ["PW1"] and p["cut"] == [] and tags(p["indexed"]) == ["PW2"]),
    ("no tools: note in full, only the file is cut", lambda: (p := materials.plan([note, big], OWN, False)) and tags(p["full"]) == ["PW1"] and [(a["tag"], k) for a, k in p["cut"]] == [("PW2", OWN - 5000)] and p["indexed"] == []),
    ("unpinned smallest first", lambda: tags(materials.plan([it("A1", 20000), it("A2", 4000), it("A3", 9000)], OWN, True)["full"]) == ["A2", "A3"]),
    ("pinned over budget", lambda: (p := materials.plan([it("B1", 20000, pinned=True, added_at="1"), it("B2", 20000, pinned=True, added_at="2")], OWN, True))
        and tags(p["full"]) == ["B1"] and [(a["tag"], k) for a, k in p["cut"]] == [("B2", 10000)] and tags(p["indexed"]) == ["B2"] and p["over_pinned"]),
    ("shared budget", lambda: tags(materials.plan([it("S1", 35000, shared=True)], SHARED, True)["full"]) == ["S1"]),
]
fails = 0
for name, fn in cases:
    ok = bool(fn()); fails += not ok; print(("ok   " if ok else "FAIL ") + name)
print(f"materials.plan: {len(cases) - fails}/{len(cases)} cases pass"); sys.exit(1 if fails else 0)
