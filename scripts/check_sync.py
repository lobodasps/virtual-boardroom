#!/usr/bin/env python3
"""Fail if any generated block is stale versus spec/.

Usage: check_sync.py

Checks the app's SPEC:* blocks (build_app.py) and the plugin's generated personas and injected prompts
(build_plugin.py) without writing anything. Exit 0 when everything matches, 1 otherwise. Standard library only.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_app, build_plugin

stale = build_app.build(check=True) + build_plugin.build(check=True)
if stale:
    print("Out of sync with spec/:")
    for p in stale: print("  " + p)
    print("Run: python3 scripts/build_app.py && python3 scripts/build_plugin.py")
    sys.exit(1)
print("In sync: app and plugin match spec/.")
