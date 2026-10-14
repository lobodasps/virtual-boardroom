#!/usr/bin/env python3
"""spec.expand_query (plugin) on tests/fixtures/data/expand.json; tests/test_expand.mjs runs the app's expandQuery on the same cases."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import spec

G = spec.load_synonyms(); fails = 0
cases = json.load(open(os.path.join(ROOT, "tests", "fixtures", "data", "expand.json"), encoding="utf-8"))["cases"]
for c in cases:
    r = spec.expand_query(c["query"], G + c.get("extra_groups", []), c["max"])
    ok = r["added"] == c["expected"] and r["text"] == c["query"] + ((" " + " ".join(c["expected"])) if c["expected"] else "")
    fails += not ok; print(("ok   " if ok else "FAIL ") + c["name"] + ("" if ok else f"  got {r['added']}"))
forms = json.load(open(os.path.join(ROOT, "tests", "fixtures", "data", "expand.json"), encoding="utf-8"))["forms"]
for c in forms:
    ok = spec.term_forms(c["term"]) == c["expected"]; fails += not ok; print(("ok   " if ok else "FAIL ") + f"forms of {c['term']!r}" + ("" if ok else f"  got {spec.term_forms(c['term'])}"))
print(f"expand_query/term_forms: {len(cases) + len(forms) - fails}/{len(cases) + len(forms)} cases pass"); sys.exit(1 if fails else 0)
