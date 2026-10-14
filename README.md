# Virtual Boardroom

A multi-agent board of directors for growth decisions, packaged as a Claude Code plugin. It works for any company, sector and geography.

You bring a decision, such as "which market should we enter first?". The plugin runs it in four phases:

1. **Scoping.** A non-voting **Strategy Counsel** scopes the analysis and calibrates the board to your sector and region. You approve the plan before any research starts.
2. **Research.** **Researcher sub-agents** gather cited facts from the web. The Counsel turns them into a PESTLE scan, a market scorecard and a list of gaps.
3. **Debate.** **Director sub-agents** debate in stages: sealed opening positions, assigned cross-examination, rebuttals, and a red-team dissent when the board agrees too quickly. Every director has its own persona and its own data folder to search.
4. **Decision.** Directors cast sealed votes and score every option. The scores give a weighted verdict: GO, GO WITH CONDITIONS, RESHAPE, DON'T DO IT or HOLD. Ruin-risk and one-way-door flags can cap that verdict. Optionally, directors ratify a draft resolution. The Counsel then writes a record of decision with the resolution, dissent, fixes for weak pillars, assumptions to test, risks, evidence gaps and the conflicting paths forward.

Between the openings and the cross-examination, the Counsel names the **cruxes**: the underlying factual, numerical or value disagreements. The cross-examination is aimed at those. Quick mode seats the 4 most relevant directors for smaller, reversible calls.

## Install

In Claude Code:

```
/plugin marketplace add lobodasps/virtual-boardroom
/plugin install virtual-boardroom@virtual-boardroom
```

Python 3 is needed for the HTML report. Optional converters, used when you attach Word, Excel or PDF data: `pandoc`, `pdftotext`, or the Python packages `python-docx`, `openpyxl` and `pypdf`.

## Use

| Command | What it does |
|---|---|
| `/virtual-boardroom:setup` | Creates `boardroom/` in your project with the seven default directors |
| `/virtual-boardroom:director` | Lists, adds, edits, seats and removes directors, attaches and pins data, and exports or imports a `.board.json` to move the board to or from the browser app |
| `/virtual-boardroom:convene` | Puts a decision to the board: intake, plan approval, research, debate, vote, report |
| `/virtual-boardroom:ask` | Consults one director: a single answer from its persona and data, optionally grounded in a session |
| `/virtual-boardroom:compare` | Compares decisions across sessions |

## The workspace

```
boardroom/
  company.md                       your company profile, reused across sessions
  directors/<id>/persona.md        title, monogram, lens, mandate, presses-on, red line, voice, PESTLE focus
  directors/<id>/data/             private briefing material (search-ready text)
  directors/<id>/data/shared/      material the whole board can see
  originals/<id>/                  the original files you attached
  sessions/<date>-<slug>/          session.json, plan, calibration, evidence, transcript/, votes.json, decision.md, report.html
```

### Default directors

All seven are composite archetypes, not real people. Edit them or add your own.

| Director | Lens |
|---|---|
| Market Expansion Strategist | Growth goes where demand is forming. |
| Customer & Deal Champion | Follow the customer's money. |
| Chief Risk Counsel | One bad contract can erase years of profit. |
| First-Principles Technologist | Revenue that only grows with headcount isn't scale. |
| Capital & M&A Allocator | What can we buy, and what is it worth once it's ours? |
| Sustainability & Long-Horizon Pathfinder | Positioning for the demand curve—well before the deadline. |
| Delivery & Profit Lead | Who delivers this, and what does it do to overhead and cash? |

## Evidence rules

- Directors must cite every fact. They cite the evidence register as `[F7]` and their own material by tag, such as `[DP2]` (tags live in each director's `data/index.json`; pinned items are always read in full).
- `scripts/check_citations.py` flags three things: uncited figures, citations that don't exist, and cited figures it couldn't find in the cited source. Only real tags count, so `[CO2]` or `[I95]` is never mistaken for a citation.
- `scripts/score.py` does all the verdict arithmetic, so the model never computes the scores itself.
- Research sub-agents report only facts from pages they opened, and they log what they could not find as gaps instead of estimating. Their limits (facts per market, pages opened, turns, source age, two-source swing facts, register size) are in `spec/rules.json` → `research`, and the browser app's research request uses the same instructions.

New to the browser app? Start with [doc/quick-start.md](doc/quick-start.md), a 6-step guide for people you share the app with.

For how a session works end to end (roles, stages, evidence rules, the verdict arithmetic, data budgets, cards and search), see [doc/specifications.md](doc/specifications.md).

## Two front ends, one spec

This repo ships the same board in two forms: the Claude Code plugin (`agents/`, `skills/`, `scripts/`, `templates/`) and a single-file browser app, `app/strategy-boardroom.html`, which runs as a Claude artifact. Both are built from `spec/`:

| In `spec/` | What it controls |
| --- | --- |
| `directors/<slug>.md` | The default directors: persona text, monogram, colors, PESTLE focus, opponents |
| `rules.json` | Seat limits, data budgets, verdict bands, caps, stage lists, pairing weights, word limits |
| `prompts/<stage>.md` | Every prompt the Counsel and directors receive |
| `schema.md` | The formats: personas, attachment manifest, votes, scoring, board export |

### How to change the board

1. Edit the file in `spec/`. Don't edit the generated parts: the app's `SPEC:*` blocks, `templates/directors/*/persona.md`, or the text between `<!-- SPEC:… -->` markers in `skills/` and `agents/`.
2. Regenerate both front ends:

   ```sh
   python3 scripts/build_app.py
   python3 scripts/build_plugin.py
   ```

3. Check that everything agrees: `python3 scripts/check_sync.py`, or `scripts/check_all.sh` to also run the tests.
4. Commit the spec change together with the regenerated files.

To have git refuse stale commits, install the hook: `cp scripts/hooks/pre-commit.sample .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`.

## Cost

A standard session with seven directors runs about 30 sub-agent turns, counting research and the Counsel. A deep session runs about 45. Each extra director adds about four turns. All of it counts against your Claude plan's usage. Both front ends show an estimate of calls and tokens before you convene (`scripts/estimate.py` in the plugin; under the seat picker in the app), from the same formula in `spec/rules.json` → `usage`. Each director reads up to `OWN_BUDGET` (60,000) characters of its own data per call.

## Privacy

Director data and session records often contain confidential figures. `/virtual-boardroom:setup` offers to add them to `.gitignore`.
