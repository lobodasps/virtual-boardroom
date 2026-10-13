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
| `/virtual-boardroom:director` | Lists, adds, edits, seats and removes directors, and attaches data to a director |
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
| Risk & Regulatory Hawk | One bad contract can erase years of profit. |
| First-Principles Technologist | Revenue that only grows with headcount isn't scale. |
| Capital & M&A Allocator | What can we buy, and what is it worth once it's ours? |
| Sustainability & Long-Horizon Maverick | Mandates create buyers who must buy. |
| Lean Operator / Profit Warden | Who delivers this, and what does it do to overhead and cash? |

## Evidence rules

- Directors must cite every fact. They cite the evidence register as `[F7]` and their own material as `[PW:utilization-2025.csv]`.
- `scripts/check_citations.py` flags three things: uncited figures, citations that don't exist, and cited figures it couldn't find in the cited source.
- `scripts/score.py` does all the verdict arithmetic, so the model never computes the scores itself.
- Research sub-agents report only facts from pages they opened, and they log what they could not find as gaps instead of estimating.

## Cost

A standard session with seven directors runs about 30 sub-agent turns, counting research and the Counsel. A deep session runs about 45. Each extra director adds about four turns. All of it counts against your Claude plan's usage.

## Privacy

Director data and session records often contain confidential figures. `/virtual-boardroom:setup` offers to add them to `.gitignore`.
