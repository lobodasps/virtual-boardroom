#!/usr/bin/env python3
"""Compute the Virtual Boardroom's weighted verdict from a session's votes.

Usage: score.py <session-folder>

Reads  votes.json        {"votes":[{"director","choice","confidence","scores":{opt:n},"pillar_scores":{opt:n},
                                    "ruin_risk":{opt:"none|possible|likely"},"door":{opt:"one-way|two-way"}, ...}]}
       calibration.json  {"weights":{"<director id>":{"w":1-3,"why":"..."}}}   (optional; default weight 2)
       ratify.json       {"votes":[{"director","vote":"endorse|amend|dissent","final_score":n}]}  (optional)
Writes votes.json["scoring"] and prints a summary. Standard library only.

Rules
  option score = sum(weight x score) / sum(weight), one decimal; recommended = highest.
  bands: >=7.5 GO, >=6.0 GO WITH CONDITIONS, >=4.5 RESHAPE, else DON'T DO IT; "Hold" on top -> HOLD.
  ruin cap: any director at ruin_risk "likely" on the recommendation caps at RESHAPE,
            unless ratification ran and every such director endorsed or amended.
  one-way door cap: majority call it one-way AND spread >= 4 -> cap at GO WITH CONDITIONS.
  council confidence (1-10) = round(avg confidence / 10), minus 1 if spread >= 5.
  weak pillars: pillar score <= 4 on the recommendation.
"""
import json, os, sys

ORDER = ["DON'T DO IT", "RESHAPE", "GO WITH CONDITIONS", "GO"]

def load(p, d=None):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d

def band(x): return "GO" if x >= 7.5 else "GO WITH CONDITIONS" if x >= 6 else "RESHAPE" if x >= 4.5 else "DON'T DO IT"

def score(folder):
    vp = os.path.join(folder, "votes.json"); votes = load(vp, {}) or {}
    weights = (load(os.path.join(folder, "calibration.json"), {}) or {}).get("weights", {})
    rat = {r.get("director"): r for r in (load(os.path.join(folder, "ratify.json"), {}) or {}).get("votes", [])}
    V = [v for v in votes.get("votes", []) if isinstance(v.get("scores"), dict)]
    if not V: print("No scored votes found."); return None
    def W(d):
        try: return min(3, max(1, round(float((weights.get(d) or {}).get("w", 2)))))
        except Exception: return 2
    keys = []
    for v in V:
        for k in v["scores"]:
            if k not in keys: keys.append(k)
    options = {}
    for k in keys:
        num = den = 0; parts = []; per = []
        for v in V:
            try: sc = float(v["scores"].get(k))
            except Exception: continue
            w = W(v.get("director")); num += w * sc; den += w; parts.append(f"{w}x{sc:g}"); per.append(sc)
        options[k] = {"score": round(num / den, 1) if den else 0.0, "math": f"({' + '.join(parts)}) / {den}", "spread": (max(per) - min(per)) if per else 0}
    ranked = sorted(options, key=lambda k: -options[k]["score"])
    rec = ranked[0]; sc = options[rec]["score"]; spread = options[rec]["spread"]
    label = "HOLD" if rec.lower() == "hold" else band(sc); caps = []
    def cap(to, why):
        nonlocal label
        if label != "HOLD" and ORDER.index(label) > ORDER.index(to): label = to
        caps.append(why)
    ruin = [v.get("director") for v in V if str((v.get("ruin_risk") or {}).get(rec, "")).lower() == "likely"]
    if ruin and label != "HOLD":
        if rat and all(rat.get(d, {}).get("vote") in ("endorse", "amend") for d in ruin):
            caps.append(f"Ruin cap lifted: {', '.join(ruin)} endorsed the resolution's mitigation")
        else: cap("RESHAPE", f"Ruin cap: {', '.join(ruin)} flagged likely ruin on '{rec}'")
    oneway = sum(1 for v in V if str((v.get("door") or {}).get(rec, "")).lower() == "one-way")
    if label != "HOLD" and oneway > len(V) / 2 and spread >= 4:
        cap("GO WITH CONDITIONS", f"One-way door: {oneway} of {len(V)} directors call '{rec}' hard to reverse and scores spread {spread:g} points")
    avg = sum(float(v.get("confidence") or 0) for v in V) / len(V)
    conf = max(1, min(10, round(avg / 10) - (1 if spread >= 5 else 0)))
    pillars = {v.get("director"): (v.get("pillar_scores") or {}).get(rec) for v in V}
    weak = [d for d, p in pillars.items() if isinstance(p, (int, float)) and p <= 4]
    support = None
    if rat:
        n = d = 0
        for did, r in rat.items():
            try: f = float(r.get("final_score"))
            except Exception: continue
            n += W(did) * f; d += W(did)
        support = round(n / d, 1) if d else None
    out = {"options": options, "ranked": ranked, "rec": rec, "score": sc, "label": label, "caps": caps, "spread": spread,
           "confidence": conf, "ruin": ruin, "pillars": pillars, "weak": weak, "weights": {v.get("director"): W(v.get("director")) for v in V}, "support": support}
    votes["scoring"] = out
    with open(vp, "w", encoding="utf-8") as f: json.dump(votes, f, indent=2)
    print(f"VERDICT: {label} — {rec} at {sc}/10 (spread {spread:g}, council confidence {conf}/10)" + (f", support for the resolution {support}/10" if support is not None else ""))
    for k in ranked: print(f"  {k}: {options[k]['math']} = {options[k]['score']}")
    for c in caps: print(f"  * {c}")
    if weak: print(f"  Weak pillars on the recommendation (<=4): {', '.join(weak)}")
    return out

if __name__ == "__main__":
    if len(sys.argv) != 2: print(__doc__); sys.exit(1)
    score(sys.argv[1])
