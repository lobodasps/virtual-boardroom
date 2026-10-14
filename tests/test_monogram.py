#!/usr/bin/env python3
"""A director whose monogram changed (SM -> SP) with one old SM-tagged item and one new SP-tagged item.
Checks the plugin's citation rule (materials.classify_cite, next_tag) and, end to end, check_citations.py on a
scratch workspace: [SM1], [SP1] and the legacy [SM:file] resolve, [SM9] is unknown, [CO2] is not a citation.
tests/test_monogram.mjs runs the same fixture through the app."""
import contextlib, io, json, os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check_citations, materials, spec

F = json.load(open(os.path.join(ROOT, "tests", "fixtures", "data", "monogram.json"), encoding="utf-8")); D = F["director"]
fails = n = 0
def check(name, ok):
    global fails, n
    n += 1; fails += not ok; print(("ok   " if ok else "FAIL ") + name)
tags = {it["tag"] for it in F["items"]}; monos = {D["mono"], *D["formerMonos"]}
for tok, want in F["tokens"]: check(f"classify [{tok}] -> {want}", materials.classify_cite(tok, tags, monos) == want)
check(f"next tag is {F['next_tag']}", materials.next_tag(D["mono"], F["items"]) == F["next_tag"])
with tempfile.TemporaryDirectory() as br:
    folder = os.path.join(br, "directors", "long-horizon"); os.makedirs(os.path.join(folder, "data"))
    with open(os.path.join(folder, "persona.md"), "w", encoding="utf-8") as f:
        f.write(spec.render_persona({"id": D["id"], "title": "Pathfinder", "mono": D["mono"], "formerMonos": D["formerMonos"]}))
    for it in F["items"]:
        with open(os.path.join(folder, "data", it["file"]), "w", encoding="utf-8") as f: f.write(it["text"])
    materials.save_manifest(folder, [{"tag": it["tag"], "file": it["file"], "name": it["name"], "chars": len(it["text"])} for it in F["items"]])
    check("persona round-trips former_monos", spec.parse_persona(open(os.path.join(folder, "persona.md")).read())["formerMonos"] == D["formerMonos"])
    sess = os.path.join(br, "sessions", "s1"); os.makedirs(os.path.join(sess, "transcript"))
    with open(os.path.join(sess, "transcript", "01-opening-maverick.md"), "w", encoding="utf-8") as f:
        f.write('<!-- vb-turn {"stage":"opening","speaker":"maverick"} -->\n' + F["transcript"])
    with contextlib.redirect_stdout(io.StringIO()): out = check_citations.check(sess, br)
    check(f"check_citations counts {F['expected_check']}", out["counts"] == F["expected_check"])
    check("the unknown citation is [SM9]", [x.get("citation") for x in out["findings"] if x["type"] == "UNKNOWN"] == ["SM9"])
print(f"monogram change (plugin): {n - fails}/{n} cases pass"); sys.exit(1 if fails else 0)
