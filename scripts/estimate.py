#!/usr/bin/env python3
"""Estimate a Virtual Boardroom session's Claude usage (the same formula as the app: spec.estimate_usage).

Usage: estimate.py --boardroom <boardroom-dir> --seats <id,id,...> --depth quick|standard|deep [--ratify] [--evidence <evidence.json>]

Each seated director's materials count up to what fits in its prompt (materials.plan with OWN_BUDGET); shared
materials up to SHARED_BUDGET; the evidence register by its length (or rules usage.default_evidence_chars).
Standard library only.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_io, materials, spec


def in_prompt(items, budget):
    p = materials.plan(items, budget, True)
    return sum(a.get("chars") or 0 for a in p["full"]) + sum(k for _, k in p["cut"])


def main(a):
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    if not opt("--boardroom") or not opt("--seats"): print(__doc__); sys.exit(1)
    R = spec.load_rules(); depth = opt("--depth") or "standard"
    seats = [spec.canon(x.strip(), R) for x in opt("--seats").split(",") if x.strip()]
    if depth == "quick": seats = seats[:R["QUICK_SEATS"]]
    have = board_io.folders(opt("--boardroom")); own, shared = [], []
    for did in seats:
        items = materials.load_manifest(have[did][0]) if did in have else []
        own.append(in_prompt(items, R["OWN_BUDGET"])); shared += [it for it in items if it.get("shared")]
    evidence = None
    if opt("--evidence"):
        with open(opt("--evidence"), encoding="utf-8") as f: evidence = len(json.dumps(json.load(f).get("facts", [])))
    u = spec.estimate_usage({"plan": spec.plan_for(depth, "--ratify" in a, rules=R), "own": own, "shared": in_prompt(shared, R["SHARED_BUDGET"]), "evidence": evidence}, R)
    fmt = lambda n: f"{n / 1e6:.1f}M" if n >= 1e6 else f"{round(n / 1e3)}k" if n >= 1e3 else str(n)
    print(f"Estimate: about {u['calls']} Claude calls (sub-agent turns), ~{fmt(u['input_tokens'])} input and ~{fmt(u['output_tokens'])} output tokens, "
          f"plus research and a few extra searches for directors with large data.")


if __name__ == "__main__":
    main(sys.argv[1:])
