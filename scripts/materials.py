#!/usr/bin/env python3
"""Manage a director's briefing materials manifest (data/index.json) and plan what the director reads in full.

Usage:
  materials.py index <director-folder>                  create or update data/index.json from the files present
  materials.py add <director-folder> <file-in-data> [--name N] [--as-of YYYY-MM] [--pin] [--card-for TAG]
                                                        register a file already copied into data/ or data/shared/;
                                                        --card-for marks it as the (pinned) summary card of item TAG
  materials.py card-source <director-folder> <TAG> [--part N]
                                                        print the text to summarize (first cards.source_chars + headings),
                                                        or part N of the whole file (whole-file mode)
  materials.py card-parts <director-folder> <TAG>       print {chars, parts, calls_quick, calls_whole} for a card
  materials.py check-card <card-file>                   validate a summary card (length, sections); exit 1 if not ok
  materials.py pin <director-folder> <TAG> [--off]      pin or unpin an item
  materials.py plan <director-folder> [--shared-only] [--budget N] [--no-tools]
                                                        print the reading plan for a director task (Markdown)
  materials.py tags <boardroom-dir>                     print every tag as JSON {tag: {director, file, path}}
  materials.py expand "<query>" [<director-folder>]     expand a search with synonyms (spec + that director's cards);
                                                        prints {added, text, grep}

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
    """Next tag for the current monogram; items tagged with a former monogram keep their tags and don't count."""
    n = 0
    for it in items:
        m = re.fullmatch(re.escape(mono) + r"(\d+)", str(it.get("tag", "")))
        if m: n = max(n, int(m.group(1)))
    return f"{mono}{n + 1}"


def entry(folder, mono, items, rel, name=None, as_of="", pinned=False, card_for=None):
    p = os.path.join(folder, "data", rel)
    added = datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"tag": next_tag(mono, items), "file": rel.replace(os.sep, "/"), "name": name or os.path.basename(rel), "chars": chars(p),
            "shared": rel.replace(os.sep, "/").startswith("shared/"), "pinned": bool(pinned), "as_of": as_of, "added_at": added,
            **({"card_for": card_for} if card_for else {})}


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
    line = lambda a: (f"- `[{a['tag']}]` {a.get('name')} — `{os.path.join(base, a['file'])}` ({a.get('chars', 0):,} characters{', shared' if a.get('shared') else ''}"
                      + (f", summary card of [{a['card_for']}]" if a.get("card_for") else "") + ")")
    out = [f"Materials of the {p['title']} (cite by tag, e.g. [{items[0]['tag'] if items else p['mono'] + '1'}]):"]
    pin_full = [a for a in pl["full"] if a.get("pinned")]; other_full = [a for a in pl["full"] if not a.get("pinned")]
    if pin_full: out += ["Read these in full first (pinned):"] + [line(a) for a in pin_full]
    if other_full: out += ["Read these in full too (they fit in the budget):"] + [line(a) for a in other_full]
    if pl["cut"]: out += ["Read only the first part of these (budget limit):"] + [line(a) + f", first {k:,} characters" for a, k in pl["cut"]]
    if pl["indexed"]: out += ["Search these with Grep and Read only the passages you need:"] + [line(a) for a in pl["indexed"]]
    if pl["over_pinned"]: out.append(f"(Pinned items alone exceed {budget:,} characters; the newest pinned items were cut.)")
    groups = spec.load_synonyms() + card_synonyms(folder)
    if items: out += ["Search synonyms (Grep for the whole pattern when your term is in one):"] + [f"- `{spec.grep_pattern(g)}`" for g in groups]
    if not items: out.append("(No materials.)")
    return "\n".join(out)


# ───────── summary cards (mirrors cardSource/validateCard/parseSynonyms in the app's SPEC:CARDS block) ─────────
CARD_HEADING = re.compile(r"^(#{1,6}\s+\S.*|--- page \d+ ---|## Sheet: .*|[A-Z][A-Z0-9 &,'()/-]{3,79})$")


def u16len(t): return len(t.encode("utf-16-le")) // 2  # the app counts UTF-16 units


def card_source(text, R, marker):
    t = str(text or "").replace("\r", ""); mx = R["cards"]["source_chars"]
    if len(t) <= mx: return {"text": t, "truncated": False, "headings": 0}
    seen, hs = set(), []
    for line in t[mx:].split("\n"):
        l = line.strip()
        if l and CARD_HEADING.match(l) and l not in seen:
            seen.add(l); hs.append(l)
            if len(hs) >= R["cards"]["max_headings"]: break
    return {"text": t[:mx] + "\n\n" + marker + "\n" + "\n".join(hs), "truncated": True, "headings": len(hs)}


def card_parts(text, R):
    """Mirror of cardParts(): consecutive parts of at most source_chars, ending at a line break within split_window."""
    t = str(text or "").replace("\r", ""); size, win = R["cards"]["source_chars"], R["cards"]["split_window"]; parts, start = [], 0
    while start < len(t):
        end = min(start + size, len(t))
        if end < len(t):
            nl = t.rfind("\n", 0, end)
            if nl > start and nl >= end - win: end = nl + 1
        parts.append(t[start:end]); start = end
    return parts


def card_calls(text, R, whole):
    n = len(str(text or "").replace("\r", ""))
    return len(card_parts(text, R)) + 1 if whole and n > R["cards"]["source_chars"] else 1


def validate_card(card, R):
    t = str(card or "").strip(); n = u16len(t); c = R["cards"]; issues = []
    if n < c["min_chars"]: issues.append(f"too short: {n} characters, at least {c['min_chars']}")
    if n > c["max_chars"]: issues.append(f"too long: {n} characters, at most {c['max_chars']}")
    for sec in c["sections"]:
        if not re.search(r"^[ \t]*" + re.escape(sec) + r"[ \t]*:", t, re.I | re.M): issues.append(f"missing section: {sec}")
    return {"ok": not issues, "length": n, "issues": issues}


def parse_synonyms(card):
    m = re.search(r"^[ \t]*SYNONYMS[ \t]*:[ \t]*(.*)$", str(card or ""), re.I | re.M)
    if not m: return []
    groups = [[x.strip() for x in g.split(",") if x.strip()] for g in m.group(1).split(";")]
    return [g for g in groups if len(g) >= 2]


def card_synonyms(folder):
    """Synonym groups from every summary card in a director's manifest."""
    out = []
    for it in load_manifest(folder):
        if it.get("card_for"):
            try:
                with open(os.path.join(folder, "data", it["file"]), encoding="utf-8") as f: out += parse_synonyms(f.read())
            except OSError: pass
    return out


# ───────── citations (mirrors classifyCite/nextTag in the app's SPEC:CITE block) ─────────
def classify_cite(tok, tags, monos):
    """'cite' for F<n> or a real tag; 'unknown' for <MONO><n> of a known current or former monogram that has no
    such item; None for anything else ([CO2], [I95], [NJ1])."""
    t = str(tok or "").strip()
    if re.fullmatch(r"F\d+", t) or t in tags: return "cite"
    m = re.fullmatch(r"([A-Z]{1,3})(\d+)", t)
    return "unknown" if m and m.group(1) in monos else None


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
            for mono in [p["mono"], *p.get("formerMonos", [])]:  # legacy [MONO:file] citations, old monograms included
                out[f"{mono}:{os.path.basename(it.get('file', ''))}"] = info
    return out


def main(a):
    if len(a) < 2: print(__doc__); sys.exit(1)
    cmd, folder = a[0], a[1]; opt = lambda k: a[a.index(k) + 1] if k in a else None
    if cmd == "index":
        for it in index(folder): print(f"{it['tag']:<6} {it['file']}{'  (missing)' if it.get('missing') else ''}")
    elif cmd == "add":
        rel = a[2]; items = load_manifest(folder); mono = persona(folder)["mono"]
        if any(it.get("file") == rel for it in items): raise SystemExit(f"{rel} is already listed")
        cf = opt("--card-for")
        if cf and not any(x.get("tag") == cf for x in items): raise SystemExit(f"No item tagged {cf} to summarize")
        it = entry(folder, mono, items, rel, opt("--name"), opt("--as-of") or "", "--pin" in a or bool(cf), cf); items.append(it); save_manifest(folder, items)
        print(json.dumps(it))
    elif cmd == "pin":
        items = load_manifest(folder); hit = [it for it in items if it.get("tag") == a[2]]
        if not hit: raise SystemExit(f"No item tagged {a[2]}")
        hit[0]["pinned"] = "--off" not in a; save_manifest(folder, items); print(json.dumps(hit[0]))
    elif cmd == "plan":
        b = opt("--budget"); print(plan_markdown(folder, "--shared-only" in a, int(b) if b else None, "--no-tools" not in a))
    elif cmd in ("card-source", "card-parts"):
        items = load_manifest(folder); hit = next((it for it in items if it.get("tag") == a[2]), None)
        if not hit: raise SystemExit(f"No item tagged {a[2]}")
        prompts, _ = spec.load_prompts(); R = spec.load_rules()
        with open(os.path.join(folder, "data", hit["file"]), encoding="utf-8", errors="ignore") as f: text = f.read()
        if cmd == "card-parts":
            print(json.dumps({"tag": a[2], "chars": len(text.replace("\r", "")), "parts": len(card_parts(text, R)),
                              "calls_quick": card_calls(text, R, False), "calls_whole": card_calls(text, R, True)}))
        elif opt("--part"):
            parts = card_parts(text, R); i = int(opt("--part"))
            if not 1 <= i <= len(parts): raise SystemExit(f"Part must be 1 to {len(parts)}")
            print(parts[i - 1])
        else:
            src = card_source(text, R, prompts["summary-card.rest_marker"]); print(src["text"])
            if src["truncated"]: print(f"\n(Shortened: first {R['cards']['source_chars']:,} characters plus {src['headings']} headings.)", file=sys.stderr)
    elif cmd == "check-card":
        with open(folder, encoding="utf-8") as f: res = validate_card(f.read(), spec.load_rules())
        print(json.dumps(res)); sys.exit(0 if res["ok"] else 1)
    elif cmd == "expand":
        q = a[1]; folder2 = a[2] if len(a) > 2 else None; R = spec.load_rules()
        groups = spec.load_synonyms() + (card_synonyms(folder2) if folder2 else [])
        ex = spec.expand_query(q, groups, R["search"]["max_added_terms"])
        terms = [t for g in spec.matched_groups(q, groups) for t in g]
        ex["grep"] = spec.grep_pattern(terms) if terms else spec.grep_pattern([q]); print(json.dumps(ex, indent=1))
    elif cmd == "tags":
        print(json.dumps(all_tags(folder), indent=2))
    else: print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
