#!/usr/bin/env python3
"""Run scripts/score.py against every tests/fixtures/*.json and compare with "expected". Standard library only.

Each fixture: {"votes":[...], "weights":{id:{w}} (optional), "ratify":{"votes":[...]} (optional), "expected":{...}}.
The same fixtures run through the app's scoreVotes() in tests/test_app_score.mjs, so both must agree.
"""
import glob, json, os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import score

KEYS = ["rec", "label", "score", "options", "spread", "confidence", "cap_codes", "ruin", "redBreached", "redAtRisk", "weak", "support", "weights"]


def comparable(out, key):
    v = out.get(key)
    if key == "options": return {k: o["score"] for k, o in v.items()}
    return v


def main():
    fails = 0; files = sorted(glob.glob(os.path.join(ROOT, "tests", "fixtures", "*.json")))
    for path in files:
        fx = json.load(open(path, encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            json.dump({"votes": fx["votes"]}, open(os.path.join(d, "votes.json"), "w"))
            json.dump({"weights": fx.get("weights", {})}, open(os.path.join(d, "calibration.json"), "w"))
            if fx.get("ratify"): json.dump(fx["ratify"], open(os.path.join(d, "ratify.json"), "w"))
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()): out = score.score(d)
        bad = [f"{k}: expected {fx['expected'][k]!r}, got {comparable(out, k)!r}" for k in KEYS if k in fx["expected"] and comparable(out, k) != fx["expected"][k]]
        print(("FAIL " if bad else "ok   ") + os.path.basename(path)); fails += bool(bad)
        for b in bad: print("     " + b)
    print(f"score.py: {len(files) - fails}/{len(files)} fixtures pass")
    sys.exit(1 if fails or not files else 0)


if __name__ == "__main__":
    main()
