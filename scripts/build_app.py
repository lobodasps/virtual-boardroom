#!/usr/bin/env python3
"""Rewrite the generated blocks in app/strategy-boardroom.html from spec/.

Usage: build_app.py [--check]

Blocks (the app's code reads board, rules and prompts only from these):
  /* SPEC:BOARD:BEGIN */ ... /* SPEC:BOARD:END */            const BOARD = [...], const COLOR_HEX = {...}
  /* SPEC:RULES:BEGIN */ ... /* SPEC:RULES:END */            const RULES = {...}, const SYNONYMS = [...] (spec/synonyms.json)
  /* SPEC:PROMPTS:BEGIN */ ... /* SPEC:PROMPTS:END */        const PROMPTS = {...}
  /* SPEC:COLORS:BEGIN */ ... /* SPEC:COLORS:END */          light --c-* CSS variables
  /* SPEC:COLORS-DARK:BEGIN */ ... /* SPEC:COLORS-DARK:END */  dark --c-* CSS variables (every occurrence)
--check reports stale blocks and exits 1 instead of writing. Standard library only.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec

APP = os.path.join(spec.ROOT, "app", "strategy-boardroom.html")


def js(v):
    s = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def board_js(directors, rules):
    rows = []
    for d in directors:
        o = {"id": d["id"], "title": d["title"], "mono": d["mono"], "color": "--c-" + d["id"]}
        if d["nonVoting"]:
            o.update(nonVoting=True, lens=d["lens"])
        else:
            o.update(pestle=", ".join(d["pestle"]), lens=d["lens"], mandate=d["mandate"], presses="\n".join(d["presses"]),
                     redLine=d["redLine"], thresholds=d["thresholds"], blindSpots=d["blindSpots"], tone=d["tone"],
                     opponents=d["opponents"], active=d["active"])
        rows.append("  " + js(o))
    hexes = {"--c-" + d["id"]: d["color"] for d in directors}
    hexes.update({"--c-" + c["name"]: {"light": c["light"], "dark": c["dark"]} for c in rules.get("custom_palette", [])})
    return "const BOARD = [\n" + ",\n".join(rows) + "\n];\nconst COLOR_HEX = " + js(hexes) + ";"


def obj_js(name, obj):
    return f"const {name} = {{\n" + ",\n".join(f"  {js(k)}:{js(v)}" for k, v in obj.items()) + "\n};"


def colors_css(directors, rules, which):
    a = [f"--c-{d['id']}:{d['color'].get(which, '')};" for d in directors]
    b = [f"--c-{p['name']}:{p[which]};" for p in rules.get("custom_palette", [])]
    return "  " + " ".join(a) + "\n  " + " ".join(b)


def blocks():
    rules = spec.load_rules(); directors = spec.load_directors(); prompts, _ = spec.load_prompts(rules)
    return {"BOARD": board_js(directors, rules), "RULES": obj_js("RULES", rules) + "\nconst SYNONYMS = " + js(spec.load_synonyms()) + ";", "PROMPTS": obj_js("PROMPTS", dict(sorted(prompts.items()))),
            "COLORS": colors_css(directors, rules, "light"), "COLORS-DARK": colors_css(directors, rules, "dark")}


def render(text):
    for name, body in blocks().items():
        pat = re.compile(r"(/\* SPEC:%s:BEGIN \*/\n)(.*?)(\n[ \t]*/\* SPEC:%s:END \*/)" % (re.escape(name), re.escape(name)), re.S)
        if not pat.search(text): raise SystemExit(f"Marker SPEC:{name} not found in {APP}")
        text = pat.sub(lambda m: m.group(1) + body + m.group(3), text)
    return text


def build(check=False):
    with open(APP, encoding="utf-8") as f: cur = f.read()
    new = render(cur)
    if new == cur: return []
    if not check:
        with open(APP, "w", encoding="utf-8") as f: f.write(new)
    return [os.path.relpath(APP, spec.ROOT)]


if __name__ == "__main__":
    check = "--check" in sys.argv
    stale = build(check)
    if check and stale: print("Stale: " + ", ".join(stale)); sys.exit(1)
    print(("Updated " + ", ".join(stale)) if stale else "App is up to date with spec/.")
