#!/usr/bin/env python3
"""Check citation discipline in a Virtual Boardroom session.

Usage: check_citations.py <session-folder> [--boardroom <boardroom-dir>]

For every director turn in transcript/ (and vote rationales), each sentence that contains a figure is checked:
  UNCITED   - a figure with no [F#] or [MONO:file] citation
  UNKNOWN   - a citation that doesn't exist (no such fact ID, or no such file in that director's data)
  MISMATCH  - the cited source text doesn't contain the figure (commas ignored). Treat as "check this", not proof of error.
Writes citations.json in the session folder and prints a summary. Standard library only.
"""
import json, os, re, sys

TURN_RE = re.compile(r"<!--\s*vb-turn\s+(\{.*?\})\s*-->", re.S)
CITE_RE = re.compile(r"\[(F\d+|[A-Z]{1,3}:[^\]]+)\]")
FIG_RE = re.compile(r"(\$\s?\d|\b\d[\d,.]*\s?(%|percent\b|million\b|billion\b|bn\b|[MBK]\b))", re.I)
NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
TEXT_EXT = (".txt", ".md", ".csv", ".tsv", ".json", ".html", ".htm")

def nums(s):
    out = []
    for x in NUM_RE.findall(s):
        x = x.replace(",", "")
        if re.fullmatch(r"\d{4}", x) and 1900 <= int(x) <= 2100: continue
        if len(re.sub(r"\D", "", x)) >= 2 or "." in x: out.append(x)
    return out

def monos(boardroom):
    m = {}
    ddir = os.path.join(boardroom, "directors")
    for d in (os.listdir(ddir) if os.path.isdir(ddir) else []):
        p = os.path.join(ddir, d, "persona.md")
        if os.path.isfile(p):
            mm = re.search(r"^mono:\s*([A-Z]{1,3})\s*$", open(p, encoding="utf-8").read(), re.M)
            if mm: m[mm.group(1)] = os.path.join(ddir, d, "data")
    return m

def find_file(data_dir, name):
    for root, _, files in os.walk(data_dir):
        for f in files:
            if f == name or os.path.splitext(f)[0] == os.path.splitext(name)[0]: return os.path.join(root, f)
    return None

def check(folder, boardroom=None):
    boardroom = boardroom or os.path.dirname(os.path.dirname(os.path.abspath(folder)))
    ev = {}
    try: ev = {f["id"]: f for f in json.load(open(os.path.join(folder, "evidence.json"), encoding="utf-8")).get("facts", [])}
    except Exception: pass
    mono = monos(boardroom); cache = {}
    def source_text(cite):
        if cite.startswith("F"):
            f = ev.get(cite); return (f.get("claim", "") + " " + f.get("quote", "")) if f else None
        m, _, fname = cite.partition(":"); fname = fname.strip()
        dd = mono.get(m)
        if not dd: return None
        p = find_file(dd, fname)
        if not p: return None
        if not p.lower().endswith(TEXT_EXT): return ""  # exists but not checkable (e.g. PDF)
        if p not in cache:
            try: cache[p] = open(p, encoding="utf-8", errors="ignore").read()
            except Exception: cache[p] = ""
        return cache[p]
    items = []
    tdir = os.path.join(folder, "transcript")
    for name in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        raw = open(os.path.join(tdir, name), encoding="utf-8").read(); m = TURN_RE.search(raw); head = {}
        if m:
            try: head = json.loads(m.group(1))
            except Exception: pass
            raw = raw[m.end():]
        if head.get("speaker") == "counsel": continue
        items.append((name, head.get("speaker"), raw))
    try:
        for v in json.load(open(os.path.join(folder, "votes.json"), encoding="utf-8")).get("votes", []):
            items.append(("votes.json", v.get("director"), v.get("rationale", "")))
    except Exception: pass
    findings = []; counts = {"UNCITED": 0, "UNKNOWN": 0, "MISMATCH": 0}
    for where, who, text in items:
        for sent in re.split(r"(?<=[.!?])\s+", " ".join((text or "").split())):
            cites = CITE_RE.findall(sent)
            for c in cites:
                if source_text(c) is None:
                    counts["UNKNOWN"] += 1; findings.append({"type": "UNKNOWN", "where": where, "director": who, "citation": c, "sentence": sent})
            if not FIG_RE.search(sent): continue
            if not cites:
                counts["UNCITED"] += 1; findings.append({"type": "UNCITED", "where": where, "director": who, "sentence": sent}); continue
            src = " ".join(t for t in (source_text(c) for c in cites) if t)
            if not src: continue
            src = src.replace(",", "")
            missing = [n for n in nums(CITE_RE.sub("", sent)) if n not in src]
            if missing:
                counts["MISMATCH"] += 1; findings.append({"type": "MISMATCH", "where": where, "director": who, "missing": missing, "citations": cites, "sentence": sent})
    out = {"counts": counts, "findings": findings}
    json.dump(out, open(os.path.join(folder, "citations.json"), "w", encoding="utf-8"), indent=2)
    print(f"Citation check: {counts['UNCITED']} uncited figures, {counts['UNKNOWN']} unknown citations, {counts['MISMATCH']} figures not found in the cited source")
    for f in findings[:20]:
        print(f"  {f['type']:<8} {f['where']} ({f['director']}): {f['sentence'][:140]}")
    return out

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(1)
    br = a[a.index("--boardroom") + 1] if "--boardroom" in a else None
    check(a[0], br)
