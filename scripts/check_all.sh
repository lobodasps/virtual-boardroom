#!/bin/sh
# Build both front ends from spec/, confirm they are in sync, and run every test.
# Usage: scripts/check_all.sh   (needs python3 and node; no packages)
set -e
cd "$(dirname "$0")/.."
echo "== build";            python3 scripts/build_app.py && python3 scripts/build_plugin.py
echo "== sync";             python3 scripts/check_sync.py
echo "== score.py";         python3 tests/test_score.py
echo "== app scoreVotes";   node tests/test_app_score.mjs
echo "== app planMaterials"; node tests/test_data.mjs
echo "== materials.py";     python3 tests/test_materials.py
echo "== research prompt"; python3 tests/test_research_sync.py
echo "== summary cards";   python3 tests/test_cards.py && node tests/test_cards.mjs
echo "== query expansion"; python3 tests/test_expand.py && node tests/test_expand.mjs
echo "== usage estimate";  python3 tests/test_usage.py && node tests/test_usage.mjs
echo "All checks passed."
