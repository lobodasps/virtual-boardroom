---
name: ask
description: Consult one Virtual Boardroom director for a quick answer, using its persona and its own data, optionally grounded in a past session's dilemma and evidence. One sub-agent run, no voting. Use when the user says "ask the Risk Hawk…", "what would the Profit Warden say…", or wants a single director's read.
argument-hint: "<director> <question> [--session <session-folder>]"
---

# Consult one director

1. Match the director the user named to a folder in `boardroom/directors/`, by id, title or monogram. If it's ambiguous, list the closest matches and ask which one.
2. Find the session if one was named, or offer the most recent one. A session supplies `dilemma.md`, `calibration.md` and `evidence.md`.
3. Launch one `virtual-boardroom:board-director` task. If that type isn't available, use `general-purpose` and paste `${CLAUDE_PLUGIN_ROOT}/agents/board-director.md` at the top of the prompt. Give it:
   - its persona file and data folder
   - the session files, if any
   - the question
   - this task, verbatim:

> SINGLE-DIRECTOR CONSULT. Answer in your own voice, first person, under 400 words. Give your call, your reasoning from your mandate (search your data first, and cite evidence and materials by ID or tag), what you would do this week, and the one question you would ask back. Do not narrate yourself in the third person. Reply with the answer only.

4. Show the answer. Save it to `boardroom/directors/<id>/consults/<YYYY-MM-DD>-<slug>.md`, with the question at the top.
