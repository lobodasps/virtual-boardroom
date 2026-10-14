# Virtual Boardroom: how it works

**Version 1.3.0.** This document describes the system's behavior: who takes part, what happens at each stage of a session, and the exact rules for evidence, voting and data. Field-level formats are in [`spec/schema.md`](../spec/schema.md). The numbers quoted here come from [`spec/rules.json`](../spec/rules.json); if they ever disagree, `rules.json` wins.

## 1. What it is

The Virtual Boardroom puts a growth decision to a simulated board of directors. A typical decision is "which market should we enter first, and how?"

- **Evidence comes first.** The board debates only after sourced web research, and directors must cite every fact.
- **Each director has a fixed point of view.** Directors argue from that point of view and from their own private data, and they vote in secret.
- **Arithmetic decides the verdict.** The scores, not the model, produce the verdict, and fixed rules cap it when a director flags ruin, a broken red line or an irreversible bet.
- **The result is a written record of decision:** a resolution, the dissent, risks, assumptions to test, and the conflicting paths forward.

The directors are composite archetypes, not real people. The system supports judgment; it does not replace it.

## 2. Two front ends, one specification

| | Browser app | Claude Code plugin |
| --- | --- | --- |
| Where it runs | `app/strategy-boardroom.html`, published as a Claude artifact | `/virtual-boardroom:*` commands in Claude Code |
| Who runs the agents | The page, through the artifact's Claude access | Claude Code sub-agents (`agents/*.md`) |
| Where data lives | The artifact's database | The `boardroom/` folder in your project |
| Research | Copied into a Claude chat with web search | `market-researcher` sub-agents |

Both are built from [`spec/`](../spec), which holds the directors, the rules, every prompt, the synonym list and the formats.

- **Building:** `scripts/build_app.py` writes generated blocks into the app, and `scripts/build_plugin.py` writes the persona templates, the researcher agent and the prompt text in the skills.
- **Checking:** `scripts/check_all.sh` rebuilds both, confirms they match the spec, and runs parity tests. Those tests show that both front ends compute the same verdicts, data budgets, cards, search expansions, usage estimates and citation results.

So a change is made once, in `spec/`, and applies to both.

## 3. Who takes part

**The chair (you)** describes the company and the decision, approves the research plan, decides who sits on the board, supplies directors' private data, and reads the outcome.

**The Strategy Counsel** is non-voting and neutral. It:
- scopes the analysis
- calibrates the board to the company's sector and geography
- writes the evidence brief and challenges weak evidence
- names the underlying disagreements, called cruxes
- drafts the resolution, when ratification is used
- writes the record of decision

It never votes and never recommends before the vote.

**Researchers** gather sourced facts for each market, plus one researcher for cross-cutting constraints (Section 6).

**Directors** are the voting members. There are seven defaults, and you can add, edit or remove directors.

| Id | Title | Tag prefix | Lens |
| --- | --- | --- | --- |
| `titan` | Market Expansion Strategist | ME | Growth goes where demand is forming. Get there before the field crowds in. |
| `developer` | Customer & Deal Champion | CD | Follow the customer's money. Build what they will pay a premium for. |
| `hawk` | Risk & Regulatory Hawk | RH | One bad contract or one compliance failure can erase years of profit. |
| `technologist` | First-Principles Technologist | FT | If revenue only grows when headcount grows, we are renting out people, not building a company. |
| `allocator` | Capital & M&A Allocator | CA | Organic growth is slow. What can we buy, and what is it worth once it is ours? |
| `maverick` | Sustainability & Long-Horizon Pathfinder | SP (formerly SM) | Positioning for the demand curve—well before the deadline. |
| `warden` | Lean Operator / Profit Warden | PW | Who exactly is going to deliver this, and what does it do to our overhead and cash? |

### What defines a director

| Field | Meaning |
| --- | --- |
| Lens | Its one-line motto |
| Mandate | What it pushes the company toward |
| Always presses on | The questions it always asks |
| Red line | What it will never accept |
| Thresholds | The numbers that move it from yes to no |
| Blind spots | Where its lens tends to misjudge. It is told to say so and adjust rather than veto. |
| Voice | How it talks |
| PESTLE focus | The external factors it watches most |
| Natural opponents | The directors it pushes back on hardest |
| Monogram | Its tag prefix, used for avatars and citation tags |

The id never changes, because saved data is keyed by it.

## 4. A session, step by step

### 4.1 Intake

You provide:
- the company, sector and geography
- the growth area and the decision question
- markets you already have in mind (optional)
- a company profile, constraints, and the assumptions you want tested
- the debate depth, and whether to ratify a resolution
- the seated directors: 3 to 12

Before you convene, both front ends show an estimate of the session's Claude usage (Section 11).

### 4.2 Analysis plan and calibration (you approve)

The Counsel proposes 3 to 5 specific markets. For each one it lists the decisive questions, the public data to pull with its likely primary sources, and the most relevant PESTLE dimensions.

It also calibrates the board:
- **Structural realities:** 4 to 6 facts about the sector and geography, such as regulators and licensing, buyers and how they buy, the labor model, payment cycles and competition.
- **Lenses:** one sentence per director on what its lens means for this company.
- **Weights:** a relevance weight from 1 to 3 per director, with a reason. The weights feed the verdict.

The plan is framing only, with no facts or figures. You can drop, rename or add markets, give instructions to the researchers, or ask for a new plan. Nothing is researched until you approve.

### 4.3 Sourced research

Each approved market gets a researcher, and one more covers cross-cutting constraints: labor, licensing, financing, and policy changes. The rules and limits are in Section 6. The researchers' facts are merged into the **evidence pack**:

- **The evidence register:** facts numbered F1…Fn, each with its market, PESTLE dimension, source, link and date. Facts dropped over the cap are listed separately.
- **A summary** citing the register.
- **A PESTLE synthesis** for each market.
- **A screening scorecard** for each market, scored 1 to 5 on demand, access, right to win, margin, capital-light, low risk, speed and synergy, each with a cited basis.
- **Evidence gaps:** what couldn't be found, and where the researchers looked.

In the app, the research runs in a Claude chat. The **Waiting for sourced research** panel holds the complete request, which you copy into the chat, and lists the limits. The pack appears in the app when the chat writes it back. In the plugin, the convene skill runs the research itself.

### 4.4 The debate

The stage list depends on the depth you chose.

| Depth | Seats | Stages |
| --- | --- | --- |
| Quick | the 4 most relevant by calibration weight | brief, opening, cruxes, 1 cross-examination round, red team if alarmed, vote, synthesis |
| Standard | as chosen | the same as Quick |
| Deep | as chosen | the same, with 2 cross-examination rounds and a red team every time |

Ratification, if chosen, adds a draft resolution and a sealed ratification before the synthesis. **Add a debate round** inserts another cross-examination round and re-runs the vote and synthesis.

| Stage | Who | Sees | Produces | Limit |
| --- | --- | --- | --- | --- |
| Brief | Counsel | the dilemma, evidence, calibration, shared data | the real question, market map, PESTLE highlights, evidence challenge, synergies, expected fault lines | ~650 words |
| Opening (sealed) | every director, in parallel | the brief only | pursue, test or avoid for each option; the key assumption; confidence | 220 words |
| Cruxes | Counsel | the brief and all openings | 1 to 3 underlying disagreements, each typed factual, numbers or values, with the directors on each side | 150 words |
| Cross-examination | each director challenges one assigned director | the transcript so far and the cruxes | quotes one claim, shows why it fails, asks one question | 150 words |
| Rebuttal | each challenged director | the transcript so far | answers each question, concedes only what the evidence forces, answers each crux | 220 words |
| Red team | the director least behind the leading option | the transcript | the strongest case against the leading option | 230 words |
| Vote (sealed) | every director, in parallel | everything except other votes | the vote JSON (Section 7) | — |
| Draft resolution | Counsel | the transcript, votes, scoring, evidence | recommendation, checkable conditions, next steps, cheapest test, kill criteria, a mitigation for every ruin and red-line flag | 200 words |
| Ratification (sealed) | every director | the draft and its own vote | endorse, amend or dissent; support 0–10 | — |
| Synthesis | Counsel | everything | the record of decision (Section 4.5) | — |

**Sealed means independent.** No director sees another's opening, vote or ratification while that stage is running.

**Consensus alarm.** The alarm fires if at least max(3, seats − 1) directors open with "pursue" on the same option. The Counsel must then make the strongest unargued alternative a crux. The red team runs on an alarm, or always in Deep sessions.

**Who challenges whom.** The system pairs directors, not the directors themselves. Every possible pair is scored:

| Condition | Points |
| --- | --- |
| Difference in stances across options (pursue 2, test 1, avoid 0) | the sum of the differences |
| The Counsel named the pair as a fault line | +2 |
| A default fault line from the personas | +1 |
| Either lists the other as a natural opponent | +2 |
| Opposite sides of a crux | +2 |
| Already paired in an earlier round | −4 |

Each director challenges its highest-scoring partner, and no director is challenged more than twice in a round.

### 4.5 The record of decision

The Counsel's synthesis contains:

- **The resolution:** one sentence that states the computed verdict, the recommended option and any caps, and reflects the vote as cast.
- **Summary, agreements and dissents:** every dissent is recorded fairly.
- **Red lines:** each red-line flag on the recommendation, and how the resolution answers it, or that it doesn't.
- **Key assumptions,** each with who holds it and how to test it, by when.
- **Risks,** each with a severity and a mitigation.
- **Evidence gaps** the decision rests on.
- **2 or 3 genuinely conflicting paths forward,** each with its backers, first 90-day moves and kill criteria.
- **A fix for every weak pillar** (Section 7).
- **The fate of each amendment,** if ratification ran.
- **Open questions.**

### 4.6 After the decision

You can:
- **Regenerate from a stage:** re-run that stage and everything after it.
- **Add a debate round.**
- **Compare sessions** side by side.
- **Ask one director** a question, optionally grounded in a session.
- **Print or save a PDF.**
- **Download a standalone report.** In the plugin, `report.html` prints cleanly.

## 5. Evidence and citations

**What directors may cite:**
- **Evidence register:** `[F7]`
- **Their own materials:** by tag, such as `[PW2]`

**Discipline:**
- Every factual statement about markets, buyers, budgets, rules, deadlines, competitors, prices or wages must carry a citation.
- No director may introduce a figure that isn't in the register, the materials or the company profile. An unknown fact must be called unknown.
- A director may reason freely, but must say when something is its own judgment.

**What counts as a citation:** a token is a citation only if it is `F` followed by a number, or a tag that actually exists. `[CO2]`, `[I95]` and `[NJ1]` are plain text.
- A token that uses a director's monogram but matches no item is flagged as an **unknown citation**. This includes former monograms, so `[SM9]` is flagged when no SM9 exists.
- Old plugin citations such as `[PW:utilization.csv]` still resolve.

**The citation check flags three things** in directors' remarks and vote rationales:

| Flag | Meaning |
| --- | --- |
| Uncited | A sentence with a figure but no valid citation |
| Unknown | A citation that doesn't exist |
| Mismatch | A cited figure that isn't found in the cited source. Treat this as "check it", not as proof of an error. |

The app highlights these inline. The plugin's `check_citations.py` writes them to `citations.json`, and the report shows the counts.

## 6. Research rules

Both front ends follow the same instructions, from `spec/prompts/research.md`, with these limits:

| Rule | Value |
| --- | --- |
| Facts per researcher | 10 to 18 |
| Pages opened per researcher | at most 15 |
| Turns per researcher | at most 20 (the plugin agent's `maxTurns`) |
| Source age | the last 24 months, except laws, rules and standards still in force |
| Swing facts re-checked | 3 to 5, each against **two independent sources**. A fact that can't be confirmed is marked "(single source)" and logged as a gap. |
| Register size | at most 80 facts. Extras are kept under "dropped", with a reason. |

**How researchers report:**
- **Opened pages only:** a fact comes from a page the researcher opened, or a search snippet that states it plainly, and it says so.
- **Primary sources first:** prefer them, and label secondary sources as such.
- **One claim per fact,** with numbers exactly as published.
- **No estimates:** anything not found goes into gaps, never into an estimate.
- **Priority on change:** researchers look actively for recent policy changes, lawsuits and incentive cuts that could undercut your assumptions.

## 7. Voting and the verdict

### The vote

Each director chooses one option, or **Hold** (pursue nothing now). It also scores **every** option, including Hold:

| Field | Values | Meaning |
| --- | --- | --- |
| `scores` | 0–10 | How strongly it backs the option |
| `pillar_scores` | 0–10 | The option judged only on its own mandate |
| `ruin_risk` | none, possible, likely | An irreversible downside that could sink the company |
| `door` | one-way, two-way | Whether the move is hard or easy to reverse |
| `red_line` | clear, at_risk, breached | Judged strictly against its own red line and thresholds |

The vote also gives support (strong or conditional), a ranking, up to 3 conditions, the one finding that would flip the vote, confidence (0–100) and a cited rationale.

### The verdict

Both front ends compute it with the same code paths, `scoreVotes` in the app and `score.py` in the plugin. Parity tests prove they agree.

1. **Option score** = Σ(weight × score) ÷ Σ(weight). The weights are the calibration weights from 1 to 3, with 2 by default. Scores round to one decimal, with halves rounding up.
2. **Recommendation:** the highest-scoring option. If Hold scores highest, the verdict is **HOLD**, and no caps apply.
3. **Band:** 7.5 or higher is **GO**; 6.0 or higher is **GO WITH CONDITIONS**; 4.5 or higher is **RESHAPE**; anything lower is **DON'T DO IT**.
4. **Caps** can only lower the verdict:

| Cap | Trigger on the recommended option | Capped at | Lifted by ratification? |
| --- | --- | --- | --- |
| Ruin | any director says ruin risk is "likely" | RESHAPE | yes, if every such director endorses or amends |
| Red line breached | any director says "breached" | RESHAPE | yes, if every such director endorses or amends |
| Red line at risk | any director says "at risk" | GO WITH CONDITIONS | no |
| One-way door | a majority call it one-way **and** the scores spread 4 or more | GO WITH CONDITIONS | no |

5. **Council confidence** (1–10) = the average confidence ÷ 10, rounded, minus 1 if the scores on the recommendation spread 5 or more.
6. **Weak pillar:** a director that scores the recommendation 4 or below on its own mandate. The record of decision must name a fix for each one.
7. **Support for the resolution:** the weighted average of the ratification scores, when ratification ran.

First-choice votes are tallied too. When they disagree with the weighted result, the record says so.

## 8. Directors' data

### Materials

Each director can hold private **materials**, such as files and notes. A material can be **shared** with the whole board.

- **Tags:** each material gets a tag, `<monogram><number>` such as `PW2`, in the order it was added. Tags are never reused.
- **Formats:** the app extracts text from PDF, Word, Excel, CSV and text files in the browser, and stores only the text. The plugin converts files to text when they're attached.
- **Monogram changes:** when a director's monogram changes, existing items keep their tags and keep resolving, and new items use the new monogram.

### What a director reads

| Rule | Value |
| --- | --- |
| Own materials, per call | up to 60,000 characters |
| Shared materials, per call | up to 40,000 characters |
| Pinned items | read in full first, oldest first |
| Unpinned items | fill the remaining room, smallest first |
| Items that don't fit | **searchable** only. The director sees the name and first 180 characters until it searches. With no search available, they are cut to fit. |

The app's data panel shows the pinned and searchable amounts, and warns when pinned items alone exceed the budget. In the plugin, each director's task includes a reading plan that lists "read these in full first" and "search these".

### Search

In the app, directors search with `search_materials` and read 1,500-character parts with `read_material`. In the plugin, they use Grep and Read.

Every search is **expanded with synonyms**:
- **Where synonyms come from:** a shared list (`spec/synonyms.json`), for example margin ↔ gross margin ↔ GP% ↔ gross profit, plus the synonyms line of any summary card the director can see.
- **Matching:** whole words only and case-insensitive. Simple singular and plural forms count, so "rebates" finds "rebate".
- **Cap:** up to 12 terms are added.

### Summary cards

For a material over 3,000 characters, the system drafts a **summary card** of 1,500 to 3,000 characters with four sections: key figures with their as-of dates, named clients and people, conclusions, and a synonyms line.

- **You edit it before saving.** A card that breaks the length or section rules can still be kept with **Save anyway**, and it is marked as saved with warnings.
- **The card is pinned** and the original stays searchable.
- **For files over 100,000 characters,** you choose before anything runs:
  - a **quick card** (1 call), drafted from the first 100,000 characters plus the headings in the rest
  - a **card from the whole file**, which summarizes each part and then merges them; one call per part plus one, shown in advance

## 9. Managing the board

- **Add, edit, seat or remove directors.** Removed directors keep their data and can be restored. Built-in directors can be reset to their original persona.
- **Draft a new director** from a one-line description. The Counsel drafts a persona that will clash with the current board, and you edit it before saving.
- **Ask one director:** a single answer in that director's voice, from its persona and data.
- **Move a board between front ends.** Export the directors, personas and materials, including cards, to a `<name>.board.json` file and import it on the other side.
  - **Matching:** import matches directors by id and keeps material tags.
  - **Overwrites:** it lists what would be overwritten and asks before doing it.
  - **Deletions:** it never deletes anything that isn't in the file.
  - **Monogram clashes:** directors whose monogram is already taken are skipped.

## 10. Where data is stored

**App, in the artifact's database:**

| Collection | Contents |
| --- | --- |
| `sessions` | session records |
| `sessions/<id>/turns` | each turn of the debate |
| `sessions/<id>/evidence/pack` | the evidence pack |
| `directors` | director overrides and custom directors |
| `directors/<id>/data` | materials, with large ones split into parts |
| `directors/<id>/consults` | answers from "Ask this director" |

If the page can't save, a banner says so, and nothing survives a reload.

**Plugin, in the `boardroom/` folder:**

| Path | Contents |
| --- | --- |
| `company.md` | the company profile |
| `directors/<folder>/persona.md` | each director's persona |
| `directors/<folder>/data/` | materials, plus `index.json` (the manifest of tags, pinned and shared flags, card links) |
| `originals/` | the original files you attached |
| `removed/` | removed directors |
| `sessions/<date>-<slug>/` | one folder per session |

Each session folder holds:
- `session.json`, `dilemma.md`, `plan.json`, `calibration.json`
- `evidence.json` and `evidence.md`
- `transcript/` with one file per turn
- `votes.json`, with the scoring
- `ratify.json` and `draft-resolution.md`, if ratification ran
- `decision.json` and `decision.md`
- `citations.json` and `report.html`

`boardroom/`, `exports/` and `*.board.json` are git-ignored, so company data never reaches the repository.

## 11. Usage estimate

Before convening, both front ends estimate the Claude calls and tokens a session will use, with the same formula (`rules.json` → `usage`).

**Calls:**
- one for the plan
- one for each Counsel stage and for the red team
- one per seated director for every other stage

**Input per call:** the prompt frame, company context, evidence and shared materials, plus the director's own materials on director stages, plus the transcript so far.

**Output per call:** each stage's word limit, or a fixed allowance for JSON stages.

Searches by directors with large data add a few calls on top. As a guide, a Standard session with 4 directors and ratification is about 26 calls, and a Deep session with 7 directors is about 47.

## 12. Changing the system

1. Edit the file in `spec/`: a director, `rules.json`, a prompt, or `synonyms.json`.
2. Run `python3 scripts/build_app.py && python3 scripts/build_plugin.py`.
3. Run `scripts/check_all.sh`. It fails if anything is out of sync, or if the two front ends disagree on any tested behavior.
4. Commit the spec change together with the regenerated files. A pre-commit hook sample is in `scripts/hooks/`.

The browser app is a single HTML file. After a change, it has to be republished to its artifact link.

## 13. Known limits

- **Model output, checked by fixed rules:** directors, the Counsel and researchers are AI models. Citation checks and scoring rules constrain them, but cannot guarantee that every fact is right. Read the record and the evidence gaps.
- **The research is only as good as what's reachable:** blocked or paywalled pages become gaps, and some facts rest on secondary sources or search snippets. Those are labelled in the claim.
- **Searching is keyword search with synonyms, not meaning-based search.** It handles simple plurals, but not other word forms.
- **The usage estimate is approximate,** and excludes searches and research.
