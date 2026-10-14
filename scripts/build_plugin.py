#!/usr/bin/env python3
"""Regenerate the plugin's spec-derived files.

Usage: build_plugin.py [--check]

- templates/directors/<slug>/persona.md  <- spec/directors/<slug>.md (voting directors), plus data/README.md and data/shared/.gitkeep
- skills/*/SKILL.md and agents/*.md: the text between
      <!-- SPEC:<prompt> -->            or  <!-- SPEC:<prompt> quote -->   (rendered as a > blockquote)
      <!-- /SPEC:<prompt> -->
  is replaced with spec/prompts/<prompt>.md (or <prompt>.<part>). Run-time {{placeholders}} become the prompt's
  plugin-defaults, or <readable name>.
--check reports stale files and exits 1 instead of writing. Standard library only.
"""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec

R = spec.ROOT
MARK = re.compile(r"(<!-- SPEC:([A-Za-z0-9_.-]+)( quote)? -->\n)(.*?)(<!-- /SPEC:\2 -->)", re.S)
README = """# Data for the {title}

Put files here that this director should bring to every session. They are private to this director.
Put files in `shared/` to make them visible to the whole board.

Directors read text, Markdown, CSV, JSON and PDF directly. Convert Word and Excel files first
(`/virtual-boardroom:director attach` does this for you).
"""


def inject(text, prompts, defaults, where):
    def rep(m):
        key = m.group(2)
        if key not in prompts: raise SystemExit(f"{where}: no spec prompt named '{key}'")
        body = spec.plugin_text(prompts, defaults, key).strip()
        if m.group(3): body = "\n".join(("> " + l) if l.strip() else ">" for l in body.splitlines())
        return m.group(1) + body + "\n" + m.group(5)
    return MARK.sub(rep, text)


def outputs():
    rules = spec.load_rules(); prompts, defaults = spec.load_prompts(rules); out = {}
    for d in spec.load_directors():
        if d["nonVoting"]: continue
        base = os.path.join(R, "templates", "directors", d["slug"])
        out[os.path.join(base, "persona.md")] = spec.director_file(d["slug"])
        readme = os.path.join(base, "data", "README.md")
        out[readme] = README.format(title=d["title"], mono=d["mono"])
        out[os.path.join(base, "data", "shared", ".gitkeep")] = ""
    for p in sorted(glob.glob(os.path.join(R, "skills", "*", "SKILL.md")) + glob.glob(os.path.join(R, "agents", "*.md"))):
        with open(p, encoding="utf-8") as f: cur = f.read()
        if "<!-- SPEC:" in cur: out[p] = inject(cur, prompts, defaults, os.path.relpath(p, R))
    return out


def build(check=False):
    stale = []
    for p, new in outputs().items():
        cur = None
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f: cur = f.read()
        if cur == new: continue
        stale.append(os.path.relpath(p, R))
        if not check:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f: f.write(new)
    return stale


if __name__ == "__main__":
    check = "--check" in sys.argv
    stale = build(check)
    if check and stale: print("Stale: " + ", ".join(stale)); sys.exit(1)
    print(("Updated " + ", ".join(stale)) if stale else "Plugin is up to date with spec/.")
