#!/usr/bin/env python3
"""Compute the Virtual Boardroom's weighted verdict from a session's votes.

Usage: score.py <session-folder>

Reads  votes.json        {"votes":[{"director","title","choice","confidence","scores":{opt:n},"pillar_scores":{opt:n},
                                    "ruin_risk":{opt:"none|possible|likely"},"door":{opt:"one-way|two-way"},
                                    "red_line":{opt:"clear|at_risk|breached"}, ...}]}
       calibration.json  {"weights":{"<director id>":{"w":n,"why":"..."}}}   (optional; default weight from the rules)
       ratify.json       {"votes":[{"director","vote":"endorse|amend|dissent","final_score":n}]}  (optional)
Writes votes.json["scoring"] and prints a summary. Standard library only.

Every threshold comes from spec/rules.json (found next to this script, or under $CLAUDE_PLUGIN_ROOT/spec):
  option score = sum(weight x score) / sum(weight), one decimal with halves rounding up; recommended = highest.
  verdict bands, the ruin cap, the red-line caps (any "breached" on the recommendation caps at RESHAPE unless
  ratification lifts it; any "at_risk" caps at GO WITH CONDITIONS), the one-way-door cap, council confidence and
  weak pillars as configured there.
Director ids are normalized through rules["legacy_ids"], so sessions from v1.1 workspaces still score.
This mirrors scoreVotes() in app/strategy-boardroom.html; tests/ check that both give the same result.
"""
import json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec


def load(p, d=None):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d


def num(x):
    if isinstance(x, bool): return math.nan
    if isinstance(x, (int, float)): return float(x)
    if isinstance(x, str) and x.strip():
        try: return float(x)
        except ValueError: return math.nan
    return math.nan


def fin(x): return not math.isnan(x) and not math.isinf(x)


def g(x): return f"{x:g}"


def score_votes(votes, weights, rat, R, all_ids=None):
    """votes: [{"id","title","v"}]; weights: {id:{"w"}}; rat: {id:{"vote","final_score"}}. Same result as the app's scoreVotes()."""
    Wr = R["weights"]
    def W(i):
        x = num((weights.get(i) or {}).get("w"))
        x = x if fin(x) and x else Wr["default"]
        return min(Wr["max"], max(Wr["min"], spec.round0(x)))
    V = [x for x in votes if isinstance((x.get("v") or {}).get("scores"), dict)]
    if not V: return None
    rat = rat or {}
    title = lambda i: next((x.get("title") for x in V if x["id"] == i and x.get("title")), i)
    keys = []
    for x in V:
        for k in x["v"]["scores"]:
            if k not in keys: keys.append(k)
    options = {}
    for k in keys:
        n = d = 0; parts = []; per = []
        for x in V:
            sc = num(x["v"]["scores"].get(k))
            if not fin(sc): continue
            w = W(x["id"]); n += w * sc; d += w; parts.append(f"{w}×{g(sc)}"); per.append(sc)
        options[k] = {"score": spec.round1(n / d) if d else 0, "math": f"({' + '.join(parts)}) / {d}", "spread": (max(per) - min(per)) if per else 0}
    ranked = sorted(options, key=lambda k: -options[k]["score"])
    rec = ranked[0]; score = options[rec]["score"]; spread = options[rec]["spread"]; hold = rec.lower() == "hold"
    O, C = R["verdict"]["order"], R["caps"]
    label = R["verdict"]["hold_label"] if hold else next((b["label"] for b in R["verdict"]["bands"] if score >= b["min"]), R["verdict"]["floor_label"])
    caps, codes = [], []
    def cap_to(to, code, why):
        nonlocal label
        if not hold and O.index(label) > O.index(to): label = to
        caps.append(why); codes.append(code)
    def note(code, why): caps.append(why); codes.append(code)
    def flagged(field, val): return [x["id"] for x in V if str((x["v"].get(field) or {}).get(rec, "") or "").lower() == val]
    def ratified(ids): return bool(rat) and all(i in rat and str(rat[i].get("vote", "")).lower() in C["ratify_lifting_votes"] for i in ids)
    names = lambda ids: ", ".join(title(i) for i in ids)
    norm = lambda x: re.sub(r"[\s-]+", "_", str(x if x is not None else "").strip().lower())
    def red_on(val): return [x["id"] for x in V if norm((x["v"].get("red_line") or {}).get(rec)) == val]
    ruin = flagged("ruin_risk", C["ruin"]["flag"])
    if ruin and not hold:
        if C["ruin"]["lift_by_ratification"] and ratified(ruin): note("ruin_lifted", f"Ruin cap lifted: {names(ruin)} endorsed the resolution's mitigation")
        else: cap_to(C["ruin"]["cap"], "ruin", f'Ruin cap: {names(ruin)} flagged likely ruin on "{rec}"')
    red_breached, red_at_risk = red_on(C["red_line_breached"]["flag"]), red_on(C["red_line_at_risk"]["flag"])
    if red_breached and not hold:
        if C["red_line_breached"]["lift_by_ratification"] and ratified(red_breached): note("red_breached_lifted", f"Red-line cap lifted: {names(red_breached)} endorsed the resolution's mitigation")
        else: cap_to(C["red_line_breached"]["cap"], "red_breached", f'Red line breached: {names(red_breached)} say "{rec}" crosses their red line')
    if red_at_risk and not hold:
        if C["red_line_at_risk"]["lift_by_ratification"] and ratified(red_at_risk): note("red_at_risk_lifted", f"Red-line cap lifted: {names(red_at_risk)} endorsed the resolution's mitigation")
        else: cap_to(C["red_line_at_risk"]["cap"], "red_at_risk", f'Red line at risk: {names(red_at_risk)} say "{rec}" puts their red line at risk')
    oneway = len(flagged("door", C["one_way_door"]["flag"]))
    if not hold and oneway > 0 and (not C["one_way_door"]["needs_majority"] or oneway > len(V) / 2) and spread >= C["one_way_door"]["min_spread"]:
        cap_to(C["one_way_door"]["cap"], "one_way_door", f'One-way door: {oneway} of {len(V)} directors call "{rec}" hard to reverse and scores spread {g(spread)} points')
    K = R["confidence"]
    avg = sum((num(x["v"].get("confidence")) if fin(num(x["v"].get("confidence"))) else 0) for x in V) / len(V)
    confidence = max(K["min"], min(K["max"], spec.round0(avg / 10) - (K["penalty"] if spread >= K["spread_penalty_at"] else 0)))
    pillars = {}
    for x in V:
        p = num((x["v"].get("pillar_scores") or {}).get(rec))
        if fin(p): pillars[x["id"]] = p
    support = None
    if rat:
        n = d = 0
        for i, r in rat.items():
            f = num((r or {}).get("final_score"))
            if fin(f): n += W(i) * f; d += W(i)
        support = spec.round1(n / d) if d else None
    return {"options": options, "ranked": ranked, "rec": rec, "score": score, "label": label, "caps": caps, "cap_codes": codes,
            "spread": spread, "confidence": confidence, "ruin": ruin, "redBreached": red_breached, "redAtRisk": red_at_risk, "pillars": pillars,
            "weak": [i for i, p in pillars.items() if p <= R["weak_pillar_max"]],
            "weights": {i: W(i) for i in (all_ids or [x["id"] for x in V])}, "support": support}


def score(folder):
    R = spec.load_rules(); canon = lambda i: spec.canon(i, R)
    vp = os.path.join(folder, "votes.json"); votes = load(vp, {}) or {}
    weights = {canon(k): v for k, v in ((load(os.path.join(folder, "calibration.json"), {}) or {}).get("weights") or {}).items()}
    rat = {canon(r.get("director")): r for r in (load(os.path.join(folder, "ratify.json"), {}) or {}).get("votes", [])}
    V = [{"id": canon(v.get("director")), "title": v.get("title"), "v": v} for v in votes.get("votes", [])]
    out = score_votes(V, weights, rat, R)
    if not out: print("No scored votes found."); return None
    votes["scoring"] = out
    with open(vp, "w", encoding="utf-8") as f: json.dump(votes, f, indent=2)
    print(f"VERDICT: {out['label']} — {out['rec']} at {g(out['score'])}/10 (spread {g(out['spread'])}, council confidence {out['confidence']}/10)"
          + (f", support for the resolution {g(out['support'])}/10" if out["support"] is not None else ""))
    for k in out["ranked"]: print(f"  {k}: {out['options'][k]['math']} = {g(out['options'][k]['score'])}")
    for c in out["caps"]: print(f"  * {c}")
    if out["redBreached"] or out["redAtRisk"]:
        print(f"  Red lines on '{out['rec']}': breached by {', '.join(out['redBreached']) or 'none'}; at risk for {', '.join(out['redAtRisk']) or 'none'}")
    if out["weak"]: print(f"  Weak pillars on the recommendation (<={R['weak_pillar_max']}): {', '.join(out['weak'])}")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2: print(__doc__); sys.exit(1)
    score(sys.argv[1])
