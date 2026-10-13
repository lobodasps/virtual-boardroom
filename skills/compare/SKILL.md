---
name: compare
description: Compare decisions across Virtual Boardroom sessions, side by side, covering the board's choice, the vote split, each director's vote, the resolution, paths forward and top risks, plus a scoreboard of which markets won the most votes. Use when the user wants to review or compare past board sessions.
argument-hint: "[session folders, or blank for all decided sessions]"
---

# Compare board sessions

1. Find the sessions under `boardroom/sessions/` that have a `votes.json`. If the user named particular sessions, use those.
2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_report.py" --compare <session folders…>`. It writes `boardroom/comparison.html` and prints a Markdown summary.
3. Show the Markdown summary in your reply. Then point out where the board was consistent across sessions, where directors changed their votes, and any decision that depended on an evidence gap that has since been filled.
