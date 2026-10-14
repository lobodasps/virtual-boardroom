#!/usr/bin/env python3
"""scripts/materials.py card functions on tests/fixtures/data/cards.json; tests/test_cards.mjs runs the app's on the same file."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import materials, spec

R = spec.load_rules(); prompts, _ = spec.load_prompts(R); MARK = prompts["summary-card.rest_marker"]
F = json.load(open(os.path.join(ROOT, "tests", "fixtures", "data", "cards.json"), encoding="utf-8"))
build = lambda parts: "".join(p["repeat"] * p["times"] if "repeat" in p else p["text"] for p in parts)
fails = n = 0
def check(name, ok):
    global fails, n
    n += 1; fails += not ok; print(("ok   " if ok else "FAIL ") + name)
for c in F["source"]:
    r = materials.card_source(build(c["parts"]), R, MARK); e = c["expected"]
    ok = r["truncated"] == e["truncated"] and r["headings"] == e["headings"]
    if "length" in e: ok = ok and len(r["text"]) == e["length"] and r["text"].endswith(e["ends_with"])
    if "heading_lines" in e: ok = ok and r["text"].endswith(MARK + "\n" + "\n".join(e["heading_lines"])) and r["text"].startswith("a" * R["cards"]["source_chars"] + "\n\n")
    check("source: " + c["name"], ok)
for c in F["validate"]:
    r = materials.validate_card(c["card"], R); e = c["expected"]
    ok = r["ok"] == e["ok"] and (r["issues"] == e["issues"] if "issues" in e else r["issues"][0].startswith(e["issues_start"]))
    check("validate: " + c["name"], ok)
for c in F["parts"]:
    txt = build(c["parts"]); e = c["expected"]
    check("parts: " + c["name"], [len(x) for x in materials.card_parts(txt, R)] == e["lengths"] and "".join(materials.card_parts(txt, R)) == txt.replace("\r", "")
          and materials.card_calls(txt, R, True) == e["calls_whole"] and materials.card_calls(txt, R, False) == e["calls_quick"])
for c in F["synonyms"]:
    check("synonyms: " + c["name"], materials.parse_synonyms(c["card"]) == c["expected"])
print(f"materials.py cards: {n - fails}/{n} cases pass"); sys.exit(1 if fails else 0)
