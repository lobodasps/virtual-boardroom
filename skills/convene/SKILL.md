---
name: convene
description: Put a growth decision to the Virtual Boardroom. The Strategy Counsel scopes the analysis, researcher sub-agents gather cited web evidence and a PESTLE scan, then seated director sub-agents debate, cross-examine and cast sealed votes, and the Counsel writes the record of decision. Use when the user wants the board to weigh which market or growth move to pursue, or says "convene the board".
argument-hint: "[growth area or decision question]"
---

# Convene the Virtual Boardroom

You are the board's clerk and orchestrator. You run the stages, launch the sub-agents, pass each one only the files it may see, and write the records. You never argue a position yourself and never vote. The value of the board comes from independent agents and sourced evidence, so follow the isolation rules exactly.

Workspace: `boardroom/` in the current project. Plugin files: `${CLAUDE_PLUGIN_ROOT}`. The board's numbers (seat limits, stage lists, the consensus alarm, pairing weights, verdict bands and caps) are in `${CLAUDE_PLUGIN_ROOT}/spec/rules.json`. The stage tasks below are generated from `spec/prompts/` and must be passed **verbatim**, with the `<placeholders>` filled in.

Sub-agents (launch with the Agent tool):
- `virtual-boardroom:strategy-counsel`: plan, calibration, evidence synthesis, brief, cruxes, draft resolution, record of decision
- `virtual-boardroom:market-researcher`: one per market, plus one for cross-cutting constraints
- `virtual-boardroom:board-director`: one per seated director per turn

If a namespaced `subagent_type` is rejected, use `general-purpose`, and paste the matching agent file's instructions from `${CLAUDE_PLUGIN_ROOT}/agents/` at the top of the prompt.

Keep a task list with one item per stage so the user can follow progress. Tell the user up front what it costs: a standard session runs about 30 sub-agent turns with 7 directors (about 4 per director plus research and Counsel), and deep runs about 45.

**Director ids.** A director's id is the `id` in its `persona.md` frontmatter (for the defaults: `titan`, `developer`, `hawk`, `technologist`, `allocator`, `maverick`, `warden`), not its folder name. Use that id in `session.json` seats, transcript headers, `votes.json`, `ratify.json` and calibration weights. Workspaces created before v1.2 may still say `id: risk-hawk` and so on; `rules.json` → `legacy_ids` maps those, and the scripts accept either.

## 0. Workspace

If `boardroom/directors/` does not exist, set it up first by following `${CLAUDE_PLUGIN_ROOT}/skills/setup/SKILL.md`.

If the user names an existing session folder or says "continue", resume it. Read `session.json` and skip every stage whose output files already exist.

## 1. Intake

Collect the following. Use AskUserQuestion for the choices and plain questions for text, and offer to reuse `boardroom/company.md` if it exists:
- company name, sector or industry, geography served
- growth area to explore, and the decision question
- markets already in mind (optional)
- company profile: size, offering, customers, locations, licenses, finances
- constraints, and the assumptions the board should test
- which way the chair is leaning, and why
- depth (the stage lists are `stages.quick|standard|deep` in `rules.json`):
  - `quick`: the `QUICK_SEATS` most relevant directors (by calibration weight), 1 round
  - `standard`: 1 cross-examination round; red team only on a consensus alarm
  - `deep`: 2 rounds plus a red team every time
- whether to **ratify a draft resolution** after the vote. This is optional and costs about one more turn per director. It turns the vote into a plan the board signed off.
- seats: list the directors from `boardroom/directors/*/persona.md` (title, monogram, how many data files), pre-select those with `seated_by_default: true`, and let the user change the selection. `MIN_SEATS` to `MAX_SEATS` directors.

Create `boardroom/sessions/<YYYY-MM-DD>-<slug>/` and write:
- `session.json`: `{title, company, sector, geography, growth_area, question, lean, markets, constraints, assumptions, depth, ratify, seats:[ids], created, status:"intake"}`
  - `lean` records which way the chair is leaning and why. The board tests the lean instead of echoing it, so ask for it.
- `dilemma.md`: all of the above as readable Markdown.

Offer to save the company profile to `boardroom/company.md` for next time.

## 2. Analysis plan and calibration (checkpoint)

Launch one `strategy-counsel` task. Give it `dilemma.md` and the seated persona files, and this task:

<!-- SPEC:plan quote -->
> TASK: Recommend the market analysis the board needs before it can decide, and calibrate the board to this company's sector and geography.
> 1. Define 3 to 5 distinct, specific markets or segments within or adjacent to the growth area that this company could realistically enter in its geography. Include the chair's markets if named; you may sharpen or add. For each one, list the questions that decide it and the specific public data to pull, naming the likely primary sources for this sector and geography (government statistics, regulators and their rules, public budgets and procurement portals, industry associations, public company filings, labor market data). Assign the PESTLE dimensions most relevant to each.
> 2. Calibrate: list 4 to 6 structural realities of this sector and geography (regulators and licensing, buyer types and buying process, labor model, funding and payment cycles, competitive structure). For each seated director, write one sentence on what their lens means here, and give a relevance weight from 1 to 3 for how much that director's mandate matters to this decision, with a one-line reason.
> Framing only: do not state any facts or figures. This is a research plan, not findings.
>
> Reply with only JSON:
> {"framing":"<2 sentences: what the board is really deciding>",
>  "markets":[{"name":"<short market name>","definition":"<one sentence: customer type, offering, geography>","why":"<why it is worth analyzing for this company>","questions":["<decisive question>"],"data":[{"item":"<data point to find>","sources":"<likely primary sources>"}],"pestle":["political","economic","social","technological","legal","environmental"]}],
>  "calibration":{"themes":["<structural reality>"],"lenses":{"<director id>":"<one sentence>"},"weights":{"<director id>":{"w":1,"why":"<one line>"}}},
>  "criteria":"<one sentence on how markets will be screened>"}
<!-- /SPEC:plan -->

Write `plan.json`, `plan.md`, `calibration.md` and `calibration.json` (the calibration object, including `weights`). For a quick session, seat only the `QUICK_SEATS` highest-weighted directors and tell the user which ones. Show the user the markets, with their questions and the calibration, and **stop for approval**. They may drop, rename or add markets, add instructions for the researcher, or ask for a new plan. Record the approved markets in `session.json` as `approved_markets`.

## 3. Sourced research

In one message, launch one `market-researcher` per approved market plus one for cross-cutting constraints, so they run in parallel. Cross-cutting means the labor market, licensing, financing and payment norms, and policy changes affecting the company's eligibility or assumed advantages. Give each one the market definition, decisive questions, data items, geography, a one-line company description, and the chair's assumptions to test.

Then assemble the evidence:
1. Merge the facts, drop duplicates, and number them `F1…Fn` in market order. Tag each with its exact market name, or `all` for cross-cutting facts.
2. Re-verify the 3 to 5 facts most likely to swing votes yourself with WebFetch. Fix or drop anything the source doesn't support.
3. Launch a `strategy-counsel` task with the merged facts. Ask for only this JSON: a `summary` (3 to 5 sentences citing `[F#]`); a `pestle` object per market (political, economic, social, technological, legal and environmental, each a list of `{point, facts:[ids]}`); and a `scorecard` per market (`demand, access, right_to_win, margin, capital_light, risk_low, speed, synergy`, each scored 1 to 5 where higher is better, plus a `basis` citing `[F#]`).
4. Write `evidence.json` in this shape: `{researched_at, summary, markets:[{name,definition}], facts:[{id,market,pestle,claim,source,url,published}], pestle:[...], scorecard:[...], gaps:[{market,question,note}]}`. Also write `evidence.md`, a readable version with the register as a table.

Tell the user how many facts you found and which of their assumptions the evidence challenges, then list the biggest gaps. Continue unless they want changes.

## 4. The debate

Build the stage list from `rules.json`: take `stages.<depth>`, and if ratifying insert `ratify.stages` (`draft`, `ratify`) before `synthesis`. Save the list to `session.json`, and update `status` after each stage.

Write each turn to `transcript/NN-<stage>-<director-id>.md`. NN is a running two-digit number. Start each file with this header line, followed by the remarks:

```
<!-- vb-turn {"stage":"opening","speaker":"<id>","title":"<title>","target":null,"targets":[],"meta":{...}} -->
```

When a director's reply contains `<<<META`, the remarks are everything before it and `meta` is the JSON object after it.

### Director task template

Each `board-director` task gets:
- the persona file, `boardroom/directors/<folder>/persona.md`
- the data folder, `boardroom/directors/<folder>/data/`
- the shared folder of every other seated director, `boardroom/directors/<other>/data/shared/`
- `dilemma.md`, `calibration.md` and `evidence.md`
- only the transcript files the stage allows (listed below)
- the seated directors' titles
- the stage task, verbatim, with its `<placeholders>` filled

Never give a director the transcript files of a sealed stage while that stage is running.

### Stages

**brief.** `strategy-counsel` reads `dilemma.md`, `evidence.md` and `calibration.md`, plus every seated director's `data/shared/` folder. Task:

<!-- SPEC:brief quote -->
> TASK: EVIDENCE BRIEF opening the session. Write these sections, each under a "### " heading:
> ### The real question: one or two sentences, including what is not being decided.
> ### Market map: for each option, the buyers and procurement path, competitive intensity, right to win for this company, margin and cash profile, people required, and time to first revenue. Cite [F#] for every fact.
> ### PESTLE highlights: the two or three forces per market most likely to decide it, cited.
> ### Evidence challenge: where the register is thin, single-sourced, stale or silent; which of the chair's assumptions the evidence does not support; what the board must not treat as settled.
> ### Synergies: how each option reuses or strains existing service lines, certifications, licenses and staff.
> ### Expected fault lines: which directors will clash and over what.
> About 650 words. Neutral: no recommendation.
> Follow the evidence discipline in your agent instructions.
> After the brief, on a new line write exactly <<<META and then one JSON object:
> {"fault_lines":[{"a":"<director id>","b":"<director id>","issue":"<12 words max>"}],"evidence_flags":[{"fact":"<F# or 'gap'>","issue":"<why it is weak>"}]}
> Director ids: <id (title) for each seated director>.
<!-- /SPEC:brief -->

**opening (sealed).** Launch every seated director in **one message**. Allowed transcript: the brief only.

<!-- SPEC:opening quote -->
> TASK: OPENING POSITION. This is sealed: you have not heard the other directors. In 220 words or fewer, say which options the company should pursue, test or avoid, and why, from your mandate. Check your briefing materials first and use at least one PESTLE finding. Name the single assumption your position depends on most.
> After your remarks, on a new line write exactly <<<META and then one JSON object, nothing after it:
> {"headline":"<your position in one sentence>","stances":[{"option":"<exact market name>","stance":"pursue|test|avoid"} for every option],"key_assumption":"<one sentence>","confidence":<0-100>}
<!-- /SPEC:opening -->

**cruxes.** `strategy-counsel` reads the brief and all the openings. The **consensus alarm** fires when at least `max(consensus_alarm.min, seats − consensus_alarm.seats_minus)` openings gave `pursue` to the same option (the leading option). Task:

<!-- SPEC:cruxes quote -->
> TASK: NAME THE CRUXES. From the sealed opening positions, in 150 words or fewer, name the one to three underlying disagreements that explain why the directors split. Classify each as factual (resolvable with evidence), numbers (turns on an estimate) or values (a trade-off such as speed versus safety), and say which directors sit on each side. [If the consensus alarm fired, insert the alarm paragraph below here.] Neutral: no recommendation.
> After the cruxes, on a new line write exactly <<<META and then one JSON object:
> {"cruxes":[{"question":"<the disagreement as a question>","type":"factual|numbers|values","side_a":{"position":"<short>","directors":["<id>"]},"side_b":{"position":"<short>","directors":["<id>"]}}],"unanimity":true|false,"unargued_alternative":"<option, or empty>"}
> Director ids: <id (title) for each seated director>.
<!-- /SPEC:cruxes -->

If the alarm fired, put this paragraph where the task says, and set `unanimity` to `true`:

<!-- SPEC:cruxes.alarm quote -->
> The openings converged on "<leading option>" (<n> of <seats> directors). Treat that as a warning, not a win: make the strongest unargued alternative a crux and name the directors who must argue it at full strength.
<!-- /SPEC:cruxes.alarm -->

From here on, every director prompt includes the cruxes.

**challengeN.** You assign the pairings; don't let directors choose. Score every director pair with the weights in `rules.json` → `pairing`:
- stance divergence: `pursue`=2, `test`=1, `avoid`=0 (missing = 1), summed as absolute differences across options
- `counsel_fault_line` (+2) if the Counsel listed the pair as a fault line
- `default_fault_line` (+1) if either director lists the other under `opponents` in the default personas at `${CLAUDE_PLUGIN_ROOT}/templates/directors/*/persona.md`
- `opposite_crux_sides` (+2) if the pair sit on opposite sides of a crux
- `repeat_pair` (−4) if the pair was already used in an earlier round

Give each director the opponent with the highest score, and let nobody be challenged more than `max_times_challenged` (2) times. Allowed transcript: everything before this stage. Launch the challenges in parallel.

<!-- SPEC:challenge quote -->
> TASK: CROSS-EXAMINATION, round N. You are directed to challenge the <target title>. Make the challenge bear on a crux where the two of you sit on opposite sides, if there is one. Quote or closely paraphrase one specific claim they made. Explain concretely why it fails in this sector and geography or for a company this size, citing the register or your materials, or showing that their claim is uncited. End with one pointed question they must answer. 150 words max. Challenge no one else.
> After your remarks, on a new line write exactly <<<META and then one JSON object, nothing after it:
> {"claim":"<the claim you attack, 25 words max>","question":"<your question>","confidence":<0-100>}
<!-- /SPEC:challenge -->

**responseN.** Every director who was challenged answers all the challenges against them in one turn. Allowed transcript: everything so far.

<!-- SPEC:response quote -->
> TASK: REBUTTAL, round N. You were challenged:
> <each challenger's title and question>
> Answer each question directly. Concede only what the evidence forces you to concede, and say exactly which fact or material changed your mind. Hold everything else and say why. Then answer each crux the Counsel named in one line. 220 words max.
> After your remarks, on a new line write exactly <<<META and then one JSON object, nothing after it:
> {"headline":"<your position now, one sentence>","conceded":"<what you concede, or 'nothing'>","position_changed":true|false,"confidence":<0-100>}
<!-- /SPEC:response -->

**redteam.** The leading option is the one with the most `pursue` stances in the openings. Run this stage if `rules.json` → `redteam.<depth>` is `always`, or if the consensus alarm fired. Otherwise record it as skipped. The director who scored the leading option lowest takes the floor (lowest confidence breaks ties). Start the task with the alarm sentence below if the alarm fired.

<!-- SPEC:redteam quote -->
> TASK: RED-TEAM DISSENT. The board is leaning toward "<lead option>". Counsel gives you the floor to make the strongest possible case against it and for the best alternative, even beyond your usual lens. Name the specific evidence, or missing evidence, that would prove the majority wrong. 230 words max.
> After your remarks, on a new line write exactly <<<META and then one JSON object, nothing after it:
> {"headline":"<the dissent in one sentence>","confidence":<0-100>}
<!-- /SPEC:redteam -->

<!-- SPEC:redteam.alarm quote -->
> Counsel has sounded a consensus alarm.
<!-- /SPEC:redteam.alarm -->

**vote (sealed).** Launch every seated director in **one message**. Allowed transcript: everything except other votes. List every approved option by its exact name.

<!-- SPEC:vote quote -->
> TASK: SEALED ROLL-CALL VOTE. You cannot see anyone else's vote. Choose exactly one option for the company to pursue as its priority, or "Hold" (pursue none now). Options: every approved market by its exact name, "Hold".
> Also score EVERY option, including Hold:
> - scores: 0-10, how strongly you back it.
> - pillar_scores: 0-10, the option judged only on your own mandate.
> - ruin_risk: "none", "possible" or "likely". This means an irreversible downside that could sink the company if it pursued that option.
> - door: "one-way" (hard to reverse) or "two-way" (easy to reverse).
> Reply with only JSON:
> {"choice":"<exact option name or Hold>","scores":{"<option>":<0-10>, for every option and Hold},"pillar_scores":{"<option>":<0-10>, for every option and Hold},"ruin_risk":{"<option>":"none|possible|likely", for every option and Hold},"door":{"<option>":"one-way|two-way", for every option and Hold},"support":"strong|conditional","ranking":["<options best to worst>"],"conditions":["<what your vote depends on, max 3>"],"flip_if":"<the one finding that would flip your vote>","confidence":<0-100>,"rationale":"<2-3 sentences in your voice, citing [F#] or material tags for facts>","changed_from_opening":true|false,"change_reason":"<why, or empty>"}
<!-- /SPEC:vote -->

Write `votes.json` as `{votes:[{director, title, ...vote}], tally:{counts:{option:n}, leader, tie, cast, strong, avg_confidence}}`.

Then run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/score.py" <session>`. Never do the arithmetic yourself. The script applies `rules.json` and computes:
- **Weighted option scores:** weight × score, divided by the total weight.
- **The recommended option and verdict band:** GO, GO WITH CONDITIONS, RESHAPE or DON'T DO IT by `verdict.bands`. Hold on top gives HOLD.
- **The ruin cap:** any director at "likely" ruin on the recommendation caps the verdict at RESHAPE until those directors endorse a mitigation.
- **The one-way-door cap:** if a majority call the recommendation one-way and the scores spread `min_spread` or more points, the verdict is capped at GO WITH CONDITIONS.
- **Spread, council confidence and weak pillars:** a weak pillar is a director scoring the recommendation `weak_pillar_max` or below on their own mandate.

The script stores all of this in `votes.json` under `scoring`. The first choices are kept too; if they disagree with the weighted result, say so.

**draft (if ratifying).** `strategy-counsel` reads the transcript, `votes.json` (including `scoring`) and `evidence.md`. Task:

<!-- SPEC:draft quote -->
> TASK: DRAFT RESOLUTION for the board to ratify. Recommend the option with the highest weighted score (the "rec" in votes.json scoring) and state the verdict label (the "label" in votes.json scoring). In 200 words or fewer: the recommendation; the conditions directors asked for (merge duplicates, make each checkable with a number, a date or a test result; where directors differ, pick one and say whose); next steps with dates; the cheapest test; kill criteria; and a mitigation for every ruin flag. Weigh arguments, not headcount: one director with a decisive fact beats three with opinions.
> Follow the evidence discipline in your agent instructions.
> After the draft, on a new line write exactly <<<META and then one JSON object:
> {"recommendation":"<option>","label":"<verdict label>","conditions":["..."],"next_steps":["..."],"cheapest_test":"...","kill_criteria":"...","mitigations":[{"for":"<director id>","mitigation":"..."}]}
<!-- /SPEC:draft -->

Write the remarks and META to `draft-resolution.md`.

**ratify (sealed, if ratifying).** Launch every seated director in **one message**. Each one reads `draft-resolution.md` and its own vote.

<!-- SPEC:ratify quote -->
> TASK: RATIFY THE DRAFT RESOLUTION. Sealed: you cannot see other directors' ratification votes. Endorse it, endorse with one amendment, or dissent. If you flagged ruin risk, endorse only if the mitigation answers it.
> Reply with only JSON: {"vote":"endorse|amend|dissent","final_score":<0-10, your support for the resolution as written>,"amendment":"<what to change, or why you dissent; empty if you endorse>","one_line":"<the one thing from your mandate the chair must not forget>"}
<!-- /SPEC:ratify -->

Write `ratify.json` as `{votes:[{director, ...}]}`, then rerun `score.py`. Ratification can lift a ruin cap, and the script adds support for the resolution.

**synthesis.** `strategy-counsel` reads the transcript, `votes.json` (including `scoring`), `evidence.md`, and `draft-resolution.md` and `ratify.json` if they exist. Task:

<!-- SPEC:synthesis quote -->
> TASK: FACILITATED SYNTHESIS. You do not vote. Produce the record of decision from the transcript, roll call and weighted scores. The resolution must state the computed verdict label, the recommended option and any caps applied, and must reflect the vote as cast, including its strength, spread, any tie and any split between first choices and weighted scores. Record every dissent fairly. Name a fix for every weak pillar. If ratification ran, record each amendment as adopted or not, with the reason: adopt an amendment when no director objected or the argument for it went unanswered. Challenge the evidence base: say which decisive claims rest on thin or missing evidence.
> Follow the evidence discipline in your agent instructions.
> Reply with only JSON:
> {"resolution":"<one-sentence board resolution reflecting the actual vote>","summary":"<3-4 sentences: what was decided and why>","agreements":["<points nearly all directors accepted>"],"dissents":[{"director":"<id>","point":"<their dissent, one sentence>"}],"key_assumptions":[{"assumption":"...","held_by":["<ids>"],"test":"<how to verify, and by when>"}],"risks":[{"risk":"...","severity":"high|medium|low","mitigation":"..."}],"evidence_gaps":["<decisive questions the evidence did not answer>"],"paths":[{"name":"<short name>","backers":["<ids>"],"thesis":"<one sentence>","first_moves":["<first 90-day moves, max 3>"],"kill_criteria":"<what would make the company stop>"}],"pillar_fixes":[{"director":"<id>","fix":"<named fix for a pillar scored 4 or below>"}],"amendments":[{"director":"<id>","amendment":"...","adopted":true,"reason":"..."}],"open_questions":["..."]}
> Give 2-3 paths that represent the genuinely conflicting directions, not variations of one.
<!-- /SPEC:synthesis -->

Write `decision.json` and a readable `decision.md`.

## 5. Report

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_citations.py" boardroom/sessions/<session>`. It flags three things:
   - uncited figures
   - citations that don't exist
   - cited figures it couldn't find in the cited source

   If it finds a mismatch in a sentence the record of decision relies on, say so in `decision.md` rather than repeating the figure.
2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_report.py" boardroom/sessions/<session>`. It writes `report.html`, including the verdict and the citation check.
3. Give the user a short verdict, under 200 words:
- the verdict label and recommended option, with the option scores on one line, the spread and any caps
- the first-choice vote split
- the strongest dissent
- the riskiest assumption
- where the report is

## Controls the user can ask for

- **Stop:** halt after the current turn. Every completed turn is already saved.
- **Continue:** resume from the next missing stage.
- **Regenerate from a stage:** delete that stage's transcript files and every later one, then resume.
- **Add a round:** add `challengeN` and `responseN` before `redteam`, delete the existing redteam, vote and synthesis outputs, then resume.
- **Change seats:** allowed only before `opening` starts.
