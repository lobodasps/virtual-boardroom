#!/usr/bin/env python3
"""Manage a director's briefing materials manifest (data/index.json) and plan what the director reads in full.

Usage:
  materials.py index <director-folder>                  create or update data/index.json from the files present
  materials.py add <director-folder> <file-in-data> [--name N] [--as-of YYYY-MM] [--pin]
                                                        register a file already copied into data/ or data/shared/
  materials.py pin <director-folder> <TAG> [--off]      pin or unpin an item
  materials.py plan <director-folder> [--shared-only] [--budget N] [--no-tools]
                                                        print the reading plan for a director task (Markdown)
  materials.py tags <boardroom-dir>                     print every tag as JSON {tag: {director, file, path}}

The manifest is a list of {tag, file, name, chars, shared, pinned, as_of, added_at} (spec/schema.md). Tags are
<MONO><n>, numbered in order of attachment and never reused. The plan mirrors planMaterials() in the app: pinned
items first (oldest first) up to the budget, then unpinned (smallest first); what doesn't fit is searchable with
Grep/Read (or cut, with --no-tools). Standard library only.
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec

SKIP = {"README.md", "index.json", ".gitkeep", ".DS_Store"}


def persona(folder):
    p = os.path.join(folder, "persona.md")
    if not os.path.isfile(p): raise SystemExit(f"No persona.md in {folder}")
    with open(p, encoding="utf-8") as f: return spec.parse_persona(f.read(), os.path.basename(os.path.normpath(folder)))


def manifest_path(folder): return os.path.join(folder, "data", "index.json")


def load_manifest(folder):
    try:
        with open(manifest_path(folder), encoding="utf-8") as f: m = json.load(f)
        return m if isinstance(m, list) else []
    except FileNotFoundError: return []


def save_manifest(folder, items):
    os.makedirs(os.path.join(folder, "data"), exist_ok=True)
    with open(manifest_path(folder), "w", encoding="utf-8") as f: json.dump(items, f, indent=2)


def chars(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f: return len(f.read())
    except OSError: return 0


def next_tag(mono, items):
    n = 0
    for it in items:
        m = re.fullmatch(re.escape(mono) + r"(\d+)", str(it.get("tag", "")))
        if m: n = max(n, int(m.group(1)))
    return f"{mono}{n + 1}"


def entry(folder, mono, items, rel, name=None, as_of="", pinned=False):
    p = os.path.join(folder, "data", rel)
    added = datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"tag": next_tag(mono, items), "file": rel.replace(os.sep, "/"), "name": name or os.path.basename(rel), "chars": chars(p),
            "shared": rel.replace(os.sep, "/").startswith("shared/"), "pinned": bool(pinned), "as_of": as_of, "added_at": added}


def data_files(folder):
    base = os.path.join(folder, "data"); out = []
    for root, _, files in os.walk(base):
        for f in files:
            if f in SKIP or f.startswith("."): continue
            out.append(os.path.relpath(os.path.join(root, f), base))
    return sorted(out, key=lambda r: os.path.getmtime(os.path.join(base, r)))


def index(folder):
    """Add unlisted files (oldest first), refresh chars and shared, keep tags. Never removes an entry."""
    mono = persona(folder)["mono"]; items = load_manifest(folder); known = {it.get("file"): it for it in items}
    for rel in data_files(folder):
        key = rel.replace(os.sep, "/")
        if key in known:
            known[key]["chars"] = chars(os.path.join(folder, "data", rel)); known[key]["shared"] = key.startswith("shared/")
        else:
            it = entry(folder, mono, items, rel); items.append(it); known[key] = it
    for it in items: it["missing"] = not os.path.exists(os.path.join(folder, "data", it.get("file", "")))
    for it in items:
        if not it["missing"]: it.pop("missing")
    save_manifest(folder, items)
    return items


def plan(items, budget, tools=True):
    """Same rule as planMaterials() in the app. items carry 'chars'; returns full, cut [(item, keep)], indexed."""
    ln = lambda a: a.get("chars") or 0
    full, cut, indexed, left = [], [], [], budget
    pinned = sorted([a for a in items if a.get("pinned")], key=lambda a: a.get("added_at") or "")
    rest = sorted([a for a in items if not a.get("pinned")], key=ln)
    for a in pinned:
        if ln(a) <= left: full.append(a); left -= ln(a)
        else:
            if left > 0: cut.append((a, left))
            left = 0
            if tools: indexed.append(a)
    if tools:
        for a in rest:
            if ln(a) <= left: full.append(a); left -= ln(a)
            else: indexed.append(a)
    else:
        for i, a in enumerate(rest):
            share = left // (len(rest) - i)
            if ln(a) <= share: full.append(a); left -= ln(a)
            else:
                if share > 0: cut.append((a, share))
                left -= share
    pc = sum(ln(a) for a in pinned)
    return {"full": full, "cut": cut, "indexed": indexed, "pinned_chars": pc, "over_pinned": pc > budget}


def plan_markdown(folder, shared_only=False, budget=None, tools=True):
    R = spec.load_rules(); p = persona(folder)
    items = [it for it in (load_manifest(folder) or index(folder)) if not it.get("missing") and (it.get("shared") or not shared_only)]
    budget = budget or (R["SHARED_BUDGET"] if shared_only else R["OWN_BUDGET"])
    pl = plan(items, budget, tools); base = os.path.join(folder, "data")
    line = lambda a: f"- `[{a['tag']}]` {a.get('name')} — `{os.path.join(base, a['file'])}` ({a.get('chars', 0):,} characters{', shared' if a.get('shared') else ''})"
    out = [f"Materials of the {p['title']} (cite by tag, e.g. [{items[0]['tag'] if items else p['mono'] + '1'}]):"]
    pin_full = [a for a in pl["full"] if a.get("pinned")]; other_full = [a for a in pl["full"] if not a.get("pinned")]
    if pin_full: out += ["Read these in full first (pinned):"] + [line(a) for a in pin_full]
    if other_full: out += ["Read these in full too (they fit in the budget):"] + [line(a) for a in other_full]
    if pl["cut"]: out += ["Read only the first part of these (budget limit):"] + [line(a) + f", first {k:,} characters" for a, k in pl["cut"]]
    if pl["indexed"]: out += ["Search these with Grep and Read only the passages you need:"] + [line(a) for a in pl["indexed"]]
    if pl["over_pinned"]: out.append(f"(Pinned items alone exceed {budget:,} characters; the newest pinned items were cut.)")
    if not items: out.append("(No materials.)")
    return "\n".join(out)


def all_tags(boardroom):
    """{tag: {director, mono, file, path}} for every director under boardroom/directors, including legacy MONO:file keys."""
    out = {}; d = os.path.join(boardroom, "directors")
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        folder = os.path.join(d, name)
        if not os.path.isfile(os.path.join(folder, "persona.md")): continue
        p = persona(folder)
        for it in load_manifest(folder):
            info = {"director": p["id"], "mono": p["mono"], "file": it.get("file"), "path": os.path.join(folder, "data", it.get("file", ""))}
            out[it.get("tag")] = info
            out[f"{p['mono']}:{os.path.basename(it.get('file', ''))}"] = info
    return out


def main(a):
    if len(a) < 2: print(__doc__); sys.exit(1)
    cmd, folder = a[0], a[1]; opt = lambda k: a[a.index(k) + 1] if k in a else None
    if cmd == "index":
        for it in index(folder): print(f"{it['tag']:<6} {it['file']}{'  (missing)' if it.get('missing') else ''}")
    elif cmd == "add":
        rel = a[2]; items = load_manifest(folder); mono = persona(folder)["mono"]
        if any(it.get("file") == rel for it in items): raise SystemExit(f"{rel} is already listed")
        it = entry(folder, mono, items, rel, opt("--name"), opt("--as-of") or "", "--pin" in a); items.append(it); save_manifest(folder, items)
        print(json.dumps(it))
    elif cmd == "pin":
        items = load_manifest(folder); hit = [it for it in items if it.get("tag") == a[2]]
        if not hit: raise SystemExit(f"No item tagged {a[2]}")
        hit[0]["pinned"] = "--off" not in a; save_manifest(folder, items); print(json.dumps(hit[0]))
    elif cmd == "plan":
        b = opt("--budget"); print(plan_markdown(folder, "--shared-only" in a, int(b) if b else None, "--no-tools" not in a))
    elif cmd == "tags":
        print(json.dumps(all_tags(folder), indent=2))
    else: print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
