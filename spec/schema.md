# Virtual Boardroom spec: formats

`spec/` is the single source of truth for both front ends:

- the Claude Code plugin (`agents/`, `skills/`, `scripts/`, `templates/`)
- the browser app, `app/strategy-boardroom.html`

Edit `spec/`, run `python3 scripts/build_app.py && python3 scripts/build_plugin.py`, and commit both the spec and the generated output. `scripts/check_sync.py` fails when they disagree.

Every field added after v1.1 is optional and has a safe default in both front ends.

## Director ids

The canonical ids are the app's: `titan`, `developer`, `hawk`, `technologist`, `allocator`, `maverick`, `warden`, `counsel`. The app's saved data is keyed by them. Plugin folders keep readable names (`risk-hawk/`), but the persona's `id` is canonical, and weights, votes, scoring and citations all key off that `id`.

Plugin workspaces created before v1.2 used the folder name as the id (`risk-hawk`). `rules.json` → `legacy_ids` maps those to canonical ids, and the scripts normalize through it, so old sessions still score.

## Persona (`spec/directors/<slug>.md`, `boardroom/directors/<slug>/persona.md`)

YAML frontmatter, then Markdown sections.

| Frontmatter | Type | Default | App field |
| --- | --- | --- | --- |
| `id` | string, canonical id | folder name | `id` |
| `order` | number, seating order of the defaults | 99 | position in `BOARD` |
| `title` | string | required | `title` |
| `mono` | 1-3 capital letters, unique; `SC` is reserved | initials of the title | `mono` |
| `former_monos` | list of earlier monograms | `[]` | `formerMonos`. Items tagged with them keep their tags and keep resolving as citations; new items use `mono` |
| `color` | `{light: "#hex", dark: "#hex"}` | next free palette color | `color` (`--c-<id>` CSS variable) |
| `seated_by_default` | bool | `true` | `active` (`false` means not seated by default) |
| `pestle` | list of Political, Economic, Social, Technological, Legal, Environmental | `[]` | `pestle`, a comma-separated string |
| `opponents` | list of director ids | `[]` | `opponents` (array) |
| `non_voting` | bool, only the Counsel | `false` | `nonVoting` |

| Section | App field | Notes |
| --- | --- | --- |
| `## Lens` | `lens` | one-line motto |
| `## Mandate` | `mandate` | |
| `## Always presses on` | `presses` | bulleted; several allowed. The app stores them one per line. |
| `## Red line` | `redLine` | |
| `## Thresholds` | `thresholds` | the numbers that move this director from yes to no. Optional. |
| `## Blind spots` | `blindSpots` | where the lens misjudges. Optional. |
| `## Voice` | `tone` | |

HTML comments inside a section are ignored, so `<!-- placeholder: … -->` leaves the field empty. An empty field is left out of prompts.

## Rules (`spec/rules.json`)

The constants, verdict bands, caps, stage lists, pairing weights and word limits used by both front ends. `scripts/score.py` reads it at run time. The app gets a generated copy between `/* SPEC:RULES:BEGIN */` and `/* SPEC:RULES:END */`.

Scores round to one decimal, with halves rounding up: `floor(x * 10 + 0.5) / 10`. Both front ends use this rounding.

## Prompts (`spec/prompts/<name>.md`)

- The main text is the prompt. `<!-- note: … -->` lines are documentation and are stripped.
- `<!-- part:<key> -->` starts a named fragment, addressed as `<name>.<key>` (e.g. `cruxes.alarm`). It runs until the next part or the defaults block.
- `{{path}}` placeholders:
  - If `path` exists in `rules.json` (e.g. `{{words.opening}}`, `{{weights.max}}`, `{{CHUNK}}`), it is filled at build time in both front ends.
  - Otherwise it is filled at run time by the app (e.g. `{{target_title}}`).
- `<!-- plugin-defaults … -->` holds `name: value` lines. When a prompt is injected into the plugin's Markdown, run-time placeholders are replaced by these defaults. A placeholder with no default is shown as `<name with spaces>`.

## Attachment manifest (`boardroom/directors/<slug>/data/index.json`)

A JSON list with one entry per material, private or shared:

```json
[{"tag": "DP1", "file": "utilization-2025.csv", "name": "2025 utilization by service line",
  "chars": 18234, "shared": false, "pinned": true, "as_of": "2025-12", "added_at": "2026-10-14T15:51:00Z"}]
```

| Field | Default | Meaning |
| --- | --- | --- |
| `tag` | required | `<MONO><n>`, numbered in order of attachment, never reused |
| `file` | required | path relative to `data/`. Shared items live in `shared/`, e.g. `shared/rates.csv` |
| `name` | the file name | display name |
| `chars` | file length | characters of searchable text |
| `shared` | `false` | visible to every seated director |
| `pinned` | `false` | always given in full, up to `OWN_BUDGET` (`SHARED_BUDGET` for shared items) |
| `as_of` | `""` | the date the material describes |
| `added_at` | `""` | ISO time attached |
| `card_for` | absent | this item is the summary card of the item with that tag. Cards are pinned; the original stays searchable |
| `card_warnings` | absent | app only (`cardWarnings`): the rules a card broke when it was saved anyway |

The app stores the same fields on each material document (`tag, name, kind, chars, shared, pinned, asOf, addedAt, cardFor`; `kind` is `file`, `text` or `card`).

**Summary cards** (`rules.json` → `cards`, `spec/prompts/summary-card.md`). A card is offered for every material longer than `cards.max_chars`, or on request. It is drafted from the first `cards.source_chars` characters plus the headings found in the rest, then shown for editing. A card normally passes the check: `min_chars`–`max_chars` long, with every section in `cards.sections`. **Save anyway** keeps a failing card, and the app records the issues as `cardWarnings`. **Card from the whole file** is an option for materials over `source_chars`: `cardParts` splits the text into parts of at most `source_chars`, ending at a line break within `split_window` when possible. Each part is summarized, then `summary-card-merge.md` merges them. The cost is `cardCalls` = parts + 1 calls, shown before it runs. Its SYNONYMS line (groups split by `;`, terms by `,`) feeds query expansion. `cardSource`/`validateCard`/`parseSynonyms` in the app's `SPEC:CARDS` block and `card_source`/`validate_card`/`parse_synonyms` in `scripts/materials.py` must agree (`tests/test_cards.*`).

**Citations** are `[MONO#]`, e.g. `[DP2]`, plus `[F#]` for the evidence register. `classifyCite` (app, `SPEC:CITE`) and `materials.classify_cite` decide: a real tag or `F#` is a citation; `<MONO><n>` of a current or former monogram with no such item is an unknown citation; anything else is plain text (`tests/test_monogram.*`). A token counts as a citation only if it is `F<digits>` or a tag in the manifest (the app's `attIndex`). `[CO2]`, `[I95]` and `[NJ1]` are not citations. Legacy plugin citations `[MONO:filename]` resolve through the manifest's `file` field.

**Budgets:**

1. Pinned items go in full, oldest first, until they use up the budget.
2. Unpinned items fill whatever budget is left, smallest first.
3. Items that don't fit are searchable only when search tools are available. In the app that means `search_materials`/`read_material`; in the plugin, Grep/Read. They appear in the index with their name and first `PREVIEW_CHARS` characters.
4. Without tools, unpinned items share the remaining space instead: smallest first, each cut to a fair share. A pinned item that doesn't fit is cut too, and only pinned items get the over-budget warning.

## Usage estimate (`rules.json` → `usage`)

`estimateUsage` (app, `SPEC:USAGE`) and `spec.estimate_usage` (plugin, `scripts/estimate.py`) take the stage list, each seated director's characters in the prompt, the shared characters and the evidence characters.

- **Calls:** one plan call, then per stage one call for Counsel stages and the red team, and one per seated director for every other stage.
- **Input:** frame + context + evidence + shared, plus each director's own materials on director stages, plus the transcript so far (word limits × `chars_per_word`). Openings see only the brief, and ratification only the draft.
- **Output:** word limits × `output_tokens_per_word`, or `json_output_tokens` for JSON stages.

Searches by directors with large data come on top. `buildPlan` (app, `SPEC:PLAN`) and `spec.plan_for` must give the same stage lists (`tests/test_usage.*`).

## Query expansion (`spec/synonyms.json`, `rules.json` → `search`)

A search query gains the other terms of every synonym group it mentions. Matching is whole words and case-insensitive, and also accepts the simple singular or plural of a term's last word (`rebates`~`rebate`, `policies`~`policy`, `taxes`~`tax`, `fee`~`fees`; words ending in -ss, -us and -is keep their form). `marginal` still does not match `margin`, groups are taken in order, and at most `search.max_added_terms` terms are added. The groups are `spec/synonyms.json` plus the SYNONYMS line of every summary card the director can see.

- **App:** `search_materials` searches with the expanded query and reports `expanded_with`.
- **Plugin:** each reading plan from `materials.py plan` lists the groups as Grep patterns, and the director agent is told to Grep for the whole pattern. `materials.py expand "<query>" [<director-folder>]` shows an expansion.

`expandQuery` (app, `SPEC:SEARCH`) and `spec.expand_query` must agree (`tests/test_expand.*`).

## Research (`rules.json` → `research`, `spec/prompts/research.md`)

Both front ends research the same way:

- **Plugin:** each `market-researcher` agent is generated from the prompt's main text and output part, with `maxTurns` set from `max_turns`. The convene skill gives each researcher the `brief` (or `cross`) part, then assembles the register with the `merge` part.
- **App:** the copy box in "Waiting for sourced research" holds the `chat` part, which wraps the same instructions, briefs and merge rules plus the evidence-pack format, for a Claude chat to run.

`tests/test_research_sync.py` fails if the two differ.

| Limit | Meaning |
| --- | --- |
| `facts_per_researcher` `{min, max}` | facts each researcher reports for its market |
| `max_turns` | turns per researcher (the agent's `maxTurns`) |
| `max_pages_opened` | pages a researcher may open with WebFetch |
| `recency_months`, `recency_exception` | source age limit, and what may be older |
| `swing_facts` `{min, max}`, `swing_facts_need_two_sources` | facts re-verified by the assembler, and whether each needs a second, independent source (rendered as yes/no in the prompt) |
| `max_register_facts` | cap on the merged register; the rest are logged under `dropped` |

### Evidence pack (app: `sessions/<id>/evidence/pack`; plugin: `evidence.json`)

The app's shape is the `pack` part of `research.md`: `researchedAt, researchedBy, summary, markets, facts, pestle, scorecard, gaps, dropped`. The plugin's `evidence.json` holds the same content with `researched_at` and the same `dropped` list. `dropped` is optional; packs written before v1.2 have none.

## Vote (one entry in `votes.json` → `votes[]`, or the app's `vote__<id>` turn `meta`)

```json
{"director": "hawk", "title": "Chief Risk Counsel",
 "choice": "<exact option or Hold>",
 "scores": {"<option>": 0-10, "Hold": 0-10},
 "pillar_scores": {"<option>": 0-10},
 "ruin_risk": {"<option>": "none|possible|likely"},
 "door": {"<option>": "one-way|two-way"},
 "red_line": {"<option>": "clear|at_risk|breached"},
 "support": "strong|conditional", "ranking": ["..."], "conditions": ["max 3"],
 "flip_if": "...", "confidence": 0-100, "rationale": "...",
 "changed_from_opening": false, "change_reason": ""}
```

A missing `red_line`, `ruin_risk` or `door` entry counts as `clear`, `none` or `two-way`. `director` is normalized through `legacy_ids`.

### Scoring output (`votes.json` → `scoring`, app `session.outcome.scoring`)

```json
{"options": {"<option>": {"score": 6.4, "math": "(2x7 + 3x6) / 5", "spread": 3}},
 "ranked": ["..."], "rec": "<option>", "score": 6.4, "label": "GO WITH CONDITIONS",
 "caps": ["<human-readable reason>"], "cap_codes": ["ruin|ruin_lifted|one_way_door|red_breached|red_breached_lifted|red_at_risk"],
 "spread": 3, "confidence": 6, "ruin": ["<id>"], "redBreached": ["<id>"], "redAtRisk": ["<id>"],
 "pillars": "app: [{id, score}]; plugin: {id: score}", "weak": ["<id>"], "weights": {"<id>": 2}, "support": 7.2}
```

Scoring outputs saved before v1.2 have no `cap_codes`, `redBreached` or `redAtRisk`. Readers treat them as empty.

## Board export (`<name>.board.json`)

Moves directors and their data between the app and the plugin. Import matches directors by `id`, asks before overwriting, keeps tags, and never deletes anything that isn't in the file.

```json
{"version": 1, "exported_at": "2026-10-14T16:00:00Z", "company_profile": "<text, or empty>",
 "directors": [{"id": "hawk", "title": "...", "mono": "RH", "color": {"light": "#A23B3B", "dark": "#E07A7A"},
   "lens": "...", "mandate": "...", "presses": ["..."], "redLine": "...", "thresholds": "...", "blindSpots": "...",
   "tone": "...", "pestle": ["Legal"], "opponents": ["technologist"],
   "custom": false, "archived": false, "active": true}],
 "materials": [{"director_id": "hawk", "tag": "RH1", "name": "...", "kind": "file|text", "shared": false,
   "pinned": false, "as_of": "", "added_at": "...", "text": "..."}]}
```

The persona fields use the app's names, and `presses` is a list. `active` is `seated_by_default`. A built-in director exported from the app carries its effective persona (the original plus any edits).
