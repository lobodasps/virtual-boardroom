#!/usr/bin/env python3
"""Render Virtual Boardroom session records to self-contained HTML.

Usage:
  render_report.py <session-folder>              -> <session-folder>/report.html
  render_report.py --compare <session-folder>... -> boardroom/comparison.html (+ Markdown summary on stdout)

Standard library only.
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import materials

TURN_RE = re.compile(r"<!--\s*vb-turn\s+(\{.*?\})\s*-->", re.S)
CITE_RE = re.compile(r"\[([^\]]+)\]")
TAGS = {}  # material tags of the session's boardroom, filled by render_session/render_compare
FIG_RE = re.compile(r"(\$\s?\d|\b\d[\d,.]*\s?(%|percent\b|million\b|billion\b|bn\b|[MBK]\b))", re.I)
STAGE_LABEL = {"brief": "Counsel's evidence brief", "opening": "Opening positions (sealed)", "redteam": "Red-team dissent"}

CSS = """
:root{--bg:#EEF0EE;--surface:#fff;--ink:#15191C;--muted:#5A646C;--line:#D3D8D5;--accent:#1F6F64;--soft:#D9ECE8;--flag:#FFF1C2;--flagink:#6B4B00;--bad:#B23A32}
@media (prefers-color-scheme:dark){:root{--bg:#101315;--surface:#181C1F;--ink:#E6EAEC;--muted:#98A2AA;--line:#2B3136;--accent:#55B8A8;--soft:#16312C;--flag:#3A3010;--flagink:#F3D37A;--bad:#E2716A;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Georgia,"Times New Roman",serif}
main{max-width:1000px;margin:0 auto;padding:32px 20px 64px}
h1,h2,h3,.ui{font-family:"Helvetica Neue",Arial,sans-serif}h1{font-size:30px;line-height:1.15;margin:4px 0 8px}h2{font-size:20px;margin:32px 0 10px}
.eyebrow{font:11px/1 ui-monospace,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:16px;margin:10px 0}
.turn{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:14px 16px;margin:10px 0}
.turn .who{font:700 14px "Helvetica Neue",Arial,sans-serif;color:var(--accent)}.turn .tgt{font:12px ui-monospace,monospace;color:var(--muted);margin-left:8px}
.headline{font:600 14.5px "Helvetica Neue",Arial,sans-serif;margin:6px 0}
.tag{display:inline-block;font:11px ui-monospace,monospace;padding:2px 7px;border:1px solid var(--line);border-radius:3px;color:var(--muted);margin:6px 4px 0 0}
.flag{background:var(--flag);color:var(--flagink);border-color:transparent}.uncited{background:linear-gradient(transparent 62%,var(--flag) 62%)}
.cite{font:12px ui-monospace,monospace;background:var(--soft);color:var(--accent);padding:0 3px;border-radius:3px;text-decoration:none}
table{border-collapse:collapse;width:100%;font:13px "Helvetica Neue",Arial,sans-serif}th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}.scroll{overflow-x:auto}
.resolution{font-size:21px;border-left:4px solid var(--accent);padding:4px 0 4px 16px;margin:8px 0 14px}
.bar{display:flex;height:24px;border-radius:5px;overflow:hidden;margin:8px 0}.bar div{display:grid;place-items:center;color:#fff;font:11px ui-monospace,monospace;background:var(--accent);overflow:hidden;white-space:nowrap}
.bar div:nth-child(2){background:#5A8F87}.bar div:nth-child(n+3){background:var(--muted)}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
"""

def esc(s): return html.escape(str(s if s is not None else ""))

def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception: return default

def is_cite(tok):
    """Only F<n> or a real material tag (including legacy MONO:file) counts; [CO2] or [NJ1] does not."""
    tok = html.unescape(tok).strip()
    return bool(re.fullmatch(r"F\d+", tok)) or tok in TAGS

def has_cite(s): return any(is_cite(t) for b in CITE_RE.findall(s) for t in re.split(r"\s*[,;]\s*", b))

def inline(text, facts):
    h = esc(text)
    h = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", h)
    def one(key):
        f = facts.get(key)
        if f: return f'<a class="cite" href="{esc(f.get("url","#"))}" title="{esc(f.get("claim",""))}">{esc(key)}</a>'
        if re.fullmatch(r"F\d+", key): return f'<span class="cite" title="Not in the evidence register">{esc(key)}?</span>'
        t = TAGS.get(html.unescape(key)) or {}
        return f'<span class="cite" title="{esc("Briefing material: " + str(t.get("file", "")))}">{key}</span>'
    def rep(m):
        toks = re.split(r"\s*[,;]\s*", m.group(1))
        if not any(is_cite(t) for t in toks): return m.group(0)
        return " ".join(one(t) if is_cite(t) else t for t in toks)
    return CITE_RE.sub(rep, h)

def prose(text, facts, flag=False):
    out, uncited = [], 0
    for para in re.split(r"\n\s*\n", (text or "").strip()):
        if not para.strip(): continue
        if para.lstrip().startswith("###"):
            out.append(f"<h3>{inline(para.lstrip('# ').strip(), facts)}</h3>"); continue
        sents = re.split(r"(?<=[.!?])\s+", " ".join(para.split()))
        parts = []
        for s in sents:
            h = inline(s, facts)
            if flag and FIG_RE.search(s) and not has_cite(s):
                uncited += 1; h = f'<span class="uncited" title="Figure without a citation">{h}</span>'
            parts.append(h)
        out.append("<p>" + " ".join(parts) + "</p>")
    return "\n".join(out), uncited

def read_turns(folder):
    tdir = os.path.join(folder, "transcript"); turns = []
    if not os.path.isdir(tdir): return turns
    for name in sorted(os.listdir(tdir)):
        if not name.endswith(".md"): continue
        raw = open(os.path.join(tdir, name), encoding="utf-8").read()
        m = TURN_RE.search(raw)
        head = {}
        if m:
            try: head = json.loads(m.group(1))
            except Exception: head = {}
            raw = raw[m.end():]
        head["text"] = raw.strip(); head["file"] = name
        turns.append(head)
    return turns

def stage_label(st):
    if st in STAGE_LABEL: return STAGE_LABEL[st]
    m = re.match(r"(challenge|response)(\d+)", st or "")
    if m: return ("Cross-examination" if m.group(1) == "challenge" else "Rebuttals") + f", round {m.group(2)}"
    return st or ""

def tally_bar(t):
    counts = (t or {}).get("counts") or {}
    if not counts: return ""
    return '<div class="bar ui">' + "".join(f'<div style="flex:{v}" title="{esc(k)}">{esc(k)} · {v}</div>' for k, v in counts.items()) + "</div>"

def red_flags(sc, names):
    rb, ra = sc.get("redBreached") or [], sc.get("redAtRisk") or []
    if not rb and not ra: return ""
    who = [f"{esc(names.get(d, d))} (breached)" for d in rb] + [f"{esc(names.get(d, d))} (at risk)" for d in ra]
    return f'<p class="ui">Red lines on {esc(sc.get("rec"))}: ' + ", ".join(who) + "</p>"

def load_tags(folder):
    TAGS.clear()
    try: TAGS.update(materials.all_tags(os.path.dirname(os.path.dirname(os.path.abspath(folder)))))
    except Exception: pass

def render_session(folder):
    load_tags(folder)
    s = load(os.path.join(folder, "session.json"), {}) or {}
    ev = load(os.path.join(folder, "evidence.json"), {}) or {}
    facts = {f["id"]: f for f in ev.get("facts", []) if "id" in f}
    votes = load(os.path.join(folder, "votes.json"), {}) or {}
    dec = load(os.path.join(folder, "decision.json"), {}) or {}
    turns = read_turns(folder)
    names = {t.get("speaker"): t.get("title") for t in turns if t.get("title")}
    total_uncited = 0
    sc = (votes or {}).get("scoring") or {}
    cit = load(os.path.join(folder, "citations.json"), {}) or {}
    body = [f'<div class="eyebrow">Virtual Boardroom · {esc(s.get("created",""))}</div><h1>{esc(s.get("title") or s.get("question"))}</h1>',
            f'<p>{esc(s.get("question",""))}</p><p class="ui" style="color:var(--muted)">{esc(" · ".join(x for x in [s.get("company"), s.get("sector"), s.get("geography")] if x))}</p>']
    if sc:
        body.append(f'<h2>Weighted verdict</h2><div class="panel"><p class="ui"><span class="tag flag" style="font-size:13px">{esc(sc.get("label"))}</span> <b>{esc(sc.get("rec"))}</b> {esc(sc.get("score"))}/10 · spread {esc(sc.get("spread"))} · council confidence {esc(sc.get("confidence"))}/10'
                    + (f' · support for the resolution {esc(sc.get("support"))}/10' if sc.get("support") is not None else "") + "</p>"
                    + "".join(f'<span class="tag flag">{esc(c)}</span>' for c in sc.get("caps", []))
                    + "<table><tr><th>Option</th><th>Score</th><th>Math</th></tr>" + "".join(f"<tr><td>{esc(k)}</td><td>{esc(sc['options'][k]['score'])}</td><td>{esc(sc['options'][k]['math'])}</td></tr>" for k in sc.get("ranked", []))
                    + "</table>" + red_flags(sc, names) + (f'<p class="ui">Weak pillars on the recommendation: {esc(", ".join(names.get(d, d) for d in sc.get("weak", [])))}</p>' if sc.get("weak") else "") + "</div>")
    if dec:
        body.append('<h2>Record of decision</h2>')
        body.append(f'<div class="resolution">{inline(dec.get("resolution",""), facts)}</div><p>{inline(dec.get("summary",""), facts)}</p>')
        body.append(tally_bar(votes.get("tally")))
        body.append('<div class="cols">')
        body.append('<div class="panel"><h3>Points of agreement</h3><ul>' + "".join(f"<li>{inline(a, facts)}</li>" for a in dec.get("agreements", [])) + "</ul></div>")
        body.append('<div class="panel"><h3>Dissent on the record</h3><ul>' + "".join(f"<li><b>{esc(names.get(d.get('director'), d.get('director')))}:</b> {inline(d.get('point',''), facts)}</li>" for d in dec.get("dissents", [])) + "</ul></div>")
        body.append("</div><h2>Conflicting paths forward</h2><div class='cols'>")
        for p in dec.get("paths", []):
            body.append(f'<div class="panel"><h3>{esc(p.get("name"))}</h3><p>{inline(p.get("thesis",""), facts)}</p><ul>' + "".join(f"<li>{inline(x, facts)}</li>" for x in p.get("first_moves", [])) + f'</ul><p class="ui"><b>Kill criteria:</b> {inline(p.get("kill_criteria",""), facts)}</p></div>')
        body.append("</div><h2>Key assumptions and risks</h2><div class='scroll'><table><tr><th>Assumption</th><th>How to test</th></tr>" + "".join(f"<tr><td>{inline(a.get('assumption',''), facts)}</td><td>{inline(a.get('test',''), facts)}</td></tr>" for a in dec.get("key_assumptions", [])) + "</table></div>")
        body.append("<div class='scroll'><table><tr><th>Risk</th><th>Severity</th><th>Mitigation</th></tr>" + "".join(f"<tr><td>{inline(r.get('risk',''), facts)}</td><td>{esc(r.get('severity'))}</td><td>{inline(r.get('mitigation',''), facts)}</td></tr>" for r in dec.get("risks", [])) + "</table></div>")
        if dec.get("red_lines"): body.append('<div class="panel"><h3>Red lines on the recommendation</h3><ul>' + "".join(f"<li><b>{esc(names.get(x.get('director'), x.get('director')))}</b> <span class=\"tag flag\">{esc(str(x.get('status','')).replace('_',' '))}</span> {inline(x.get('response',''), facts)}</li>" for x in dec["red_lines"]) + "</ul></div>")
        if dec.get("pillar_fixes"): body.append('<div class="panel"><h3>Fixes for weak pillars</h3><ul>' + "".join(f"<li><b>{esc(names.get(x.get('director'), x.get('director')))}:</b> {inline(x.get('fix',''), facts)}</li>" for x in dec["pillar_fixes"]) + "</ul></div>")
        if dec.get("amendments"): body.append('<div class="panel"><h3>Amendments</h3><ul>' + "".join(f"<li><b>{esc(names.get(x.get('director'), x.get('director')))}</b> ({'adopted' if x.get('adopted') else 'not adopted'}): {inline(x.get('amendment',''), facts)}</li>" for x in dec["amendments"]) + "</ul></div>")
        if dec.get("evidence_gaps"): body.append('<div class="panel"><h3>Evidence gaps the decision rests on</h3><ul>' + "".join(f"<li>{inline(x, facts)}</li>" for x in dec["evidence_gaps"]) + "</ul></div>")
    if votes.get("votes"):
        body.append("<h2>Roll call</h2><div class='scroll'><table><tr><th>Director</th><th>Choice</th><th>Support</th><th>Confidence</th><th>Red-line flags</th><th>Rationale</th><th>Flips if</th></tr>")
        for v in votes["votes"]:
            flags = [f"{k}: {str(x).replace('_', ' ')}" for k, x in (v.get("red_line") or {}).items() if re.sub(r"[\s-]+", "_", str(x).strip().lower()) in ("at_risk", "breached")]
            flag_html = "".join('<span class="tag flag">' + esc(x) + "</span> " for x in flags) or "clear"
            body.append(f"<tr><td>{esc(v.get('title') or v.get('director'))}</td><td><b>{esc(v.get('choice'))}</b></td><td>{esc(v.get('support'))}</td><td>{esc(v.get('confidence'))}</td><td>{flag_html}</td><td>{inline(v.get('rationale',''), facts)}</td><td>{inline(v.get('flip_if',''), facts)}</td></tr>")
        body.append("</table></div>")
    body.append("<h2>Transcript</h2>"); last = None
    for t in turns:
        if t.get("stage") in ("vote", "synthesis"): continue
        if t.get("stage") != last:
            last = t.get("stage"); body.append(f'<div class="eyebrow" style="margin-top:22px">{esc(stage_label(last))}</div>')
        meta = t.get("meta") or {}
        is_counsel = t.get("speaker") == "counsel"
        txt, n = prose(t.get("text", ""), facts, flag=not is_counsel); total_uncited += n
        tgt = f'<span class="tgt">→ challenges {esc(names.get(t["target"], t["target"]))}</span>' if t.get("target") else ""
        tags = []
        if meta.get("confidence") is not None: tags.append(f'<span class="tag">confidence {esc(meta["confidence"])}</span>')
        for st in meta.get("stances", []) or []: tags.append(f'<span class="tag">{esc(st.get("option"))}: {esc(st.get("stance"))}</span>')
        if meta.get("position_changed"): tags.append('<span class="tag flag">position changed</span>')
        if n: tags.append(f'<span class="tag flag">{n} uncited figure{"s" if n > 1 else ""}</span>')
        body.append(f'<div class="turn"><span class="who">{esc(t.get("title") or t.get("speaker"))}</span>{tgt}'
                    + (f'<div class="headline">{inline(meta.get("headline",""), facts)}</div>' if meta.get("headline") else "")
                    + (f'<p><i>Claim under challenge:</i> {inline(meta.get("claim",""), facts)}</p>' if meta.get("claim") else "")
                    + txt + (f'<p class="ui"><b>Question:</b> {inline(meta.get("question",""), facts)}</p>' if meta.get("question") else "")
                    + "".join(tags) + "</div>")
    if facts:
        body.append("<h2>Evidence register</h2><div class='scroll'><table><tr><th>ID</th><th>Fact</th><th>Source</th></tr>" + "".join(
            f"<tr id='{esc(f['id'])}'><td>{esc(f['id'])}</td><td>{esc(f.get('claim'))}</td><td><a href='{esc(f.get('url'))}'>{esc(f.get('source'))}</a> {esc(f.get('published',''))}</td></tr>" for f in facts.values()) + "</table></div>")
    cc = cit.get("counts") or {}
    extra = (f' <span class="tag {"flag" if cc.get("MISMATCH") else ""}">{cc.get("MISMATCH",0)} cited figures not found in the source</span> <span class="tag {"flag" if cc.get("UNKNOWN") else ""}">{cc.get("UNKNOWN",0)} unknown citations</span>') if cc else ""
    body.insert(2, f'<p class="ui"><span class="tag {"flag" if total_uncited else ""}">Citation discipline: {total_uncited} uncited figure{"s" if total_uncited != 1 else ""} in directors\' remarks</span>{extra}</p>')
    out = os.path.join(folder, "report.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(s.get("title","Board session"))}</title><style>{CSS}</style></head><body><main>' + "\n".join(body) + "</main></body></html>")
    print(f"Wrote {out}")
    print(f"Uncited figures in directors' remarks: {total_uncited}")

def render_compare(folders):
    rows = []
    for fd in folders:
        s = load(os.path.join(fd, "session.json"), {}) or {}
        v = load(os.path.join(fd, "votes.json"), {}) or {}
        d = load(os.path.join(fd, "decision.json"), {}) or {}
        if not v.get("votes"): continue
        rows.append((fd, s, v, d))
    if not rows:
        print("No decided sessions found (a session needs votes.json)."); return
    directors = {}
    for _, _, v, _ in rows:
        for x in v["votes"]: directors.setdefault(x.get("director"), x.get("title") or x.get("director"))
    md = ["| | " + " | ".join(esc(s.get("title", os.path.basename(fd))) for fd, s, _, _ in rows) + " |", "|---" * (len(rows) + 1) + "|"]
    def row(label, fn): md.append(f"| {label} | " + " | ".join(fn(*r) for r in rows) + " |")
    row("Board choice", lambda fd, s, v, d: f"**{v.get('tally', {}).get('leader', '')}** ({v.get('tally', {}).get('counts', {}).get(v.get('tally', {}).get('leader', ''), '')}/{len(v['votes'])})")
    row("Resolution", lambda fd, s, v, d: (d.get("resolution") or "").replace("|", "/"))
    for did, title in directors.items():
        row(title, lambda fd, s, v, d, did=did: next((f"{x.get('choice')} ({x.get('support')})" for x in v["votes"] if x.get("director") == did), "—"))
    row("Paths forward", lambda fd, s, v, d: "; ".join(p.get("name", "") for p in d.get("paths", [])))
    agg = {}
    for _, _, v, _ in rows:
        for x in v["votes"]: agg[x.get("choice")] = agg.get(x.get("choice"), 0) + 1
    md.append("\n**Market scoreboard (votes across these sessions):** " + ", ".join(f"{k}: {n}" for k, n in sorted(agg.items(), key=lambda kv: -kv[1])))
    text = "\n".join(md)
    root = os.path.dirname(os.path.dirname(os.path.abspath(rows[0][0])))
    out = os.path.join(root, "comparison.html")
    table = "<div class='scroll'><table>" + "".join(
        "<tr>" + "".join(f"<{'th' if i == 0 else 'td'}>{c.strip()}</{'th' if i == 0 else 'td'}>" for c in line.strip("|").split("|")) + "</tr>"
        for i, line in enumerate(md[:1] + md[2:]) if line.startswith("|")) + "</table></div>"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Board comparison</title><style>{CSS}</style></head><body><main><div class="eyebrow">Virtual Boardroom</div><h1>Comparing board decisions</h1>{table}<p class="ui">{esc(md[-1].strip("*"))}</p></main></body></html>')
    print(text); print(f"\nWrote {out}")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args: print(__doc__); sys.exit(1)
    if args[0] == "--compare": render_compare(args[1:])
    else: render_session(args[0])
