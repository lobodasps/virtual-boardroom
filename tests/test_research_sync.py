#!/usr/bin/env python3
"""Fail if the research prompt the app sends to a chat differs from what the plugin's researchers and convene use.

Compares, text for text: the app's generated PROMPTS["research"], ["research.output"], ["research.merge"],
["research.brief"] and ["research.cross"] with agents/market-researcher.md and the SPEC:research.* blocks in
skills/convene/SKILL.md, and maxTurns with rules.json research.max_turns. Standard library only.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import spec

read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()
app, agent, convene = read("app", "strategy-boardroom.html"), read("agents", "market-researcher.md"), read("skills", "convene", "SKILL.md")
block = re.search(r"/\* SPEC:PROMPTS:BEGIN \*/\nconst PROMPTS = \{\n(.*?)\n\};\n/\* SPEC:PROMPTS:END \*/", app, re.S).group(1)
P = {}
for line in block.splitlines():
    P.update(json.loads("{" + line.rstrip(",").replace("<\\/", "</") + "}"))
_, defaults = spec.load_prompts()
plugin_view = lambda key: spec.plugin_text(P, defaults, key)  # the app's template as the plugin renders it
quoted = lambda name: "\n".join(re.sub(r"^> ?", "", l) for l in re.search(r"<!-- SPEC:%s quote -->\n(.*?)<!-- /SPEC:%s -->" % (re.escape(name), re.escape(name)), convene, re.S).group(1).strip().splitlines())
body = agent.split("-->", 1)[1]
main, _, output = body.partition("\n## Output\n")
checks = [
    ("researcher instructions (app vs agents/market-researcher.md)", P["research"], main.strip()),
    ("researcher output format (app vs agent)", P["research.output"], output.strip()),
    ("maxTurns (agent frontmatter vs rules.json)", str(spec.load_rules()["research"]["max_turns"]), re.search(r"^maxTurns:\s*(\d+)", agent, re.M).group(1)),
    ("merge rules (app vs convene)", plugin_view("research.merge"), quoted("research.merge")),
    ("market brief (app vs convene)", plugin_view("research.brief"), quoted("research.brief")),
    ("cross-cutting brief (app vs convene)", plugin_view("research.cross"), quoted("research.cross")),
    ("app chat request uses the researcher instructions", "yes", "yes" if 'researcher:P("research")' in app and 'merge:P("research.merge")' in app else "no"),
]
fails = 0
for name, a, b in checks:
    ok = a == b; fails += not ok
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        import difflib
        print("\n".join("     " + l for l in list(difflib.unified_diff(a.splitlines(), b.splitlines(), "app", "plugin", lineterm=""))[:20]))
print(f"research prompt sync: {len(checks) - fails}/{len(checks)} checks pass")
sys.exit(1 if fails else 0)
