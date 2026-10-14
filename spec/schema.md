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
[{"tag": "PW1", "file": "utilization-2025.csv", "name": "2025 utilization by service line",
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

The app stores the same fields on each material document (`tag, name, kind, chars, shared, pinned, asOf, addedAt`).

**Citations** are `[MONO#]`, e.g. `[PW2]`, plus `[F#]` for the evidence register. A token counts as a citation only if it is `F<digits>` or a tag in the manifest (the app's `attIndex`). `[CO2]`, `[I95]` and `[NJ1]` are not citations. Legacy plugin citations `[MONO:filename]` resolve through the manifest's `file` field.

**Budgets:**

1. Pinned items go in full, oldest first, until they use up the budget.
2. Unpinned items fill whatever budget is left, smallest first.
3. Items that don't fit are searchable only when search tools are available. In the app that means `search_materials`/`read_material`; in the plugin, Grep/Read. They appear in the index with their name and first `PREVIEW_CHARS` characters.
4. Without tools, unpinned items share the remaining space instead: smallest first, each cut to a fair share. A pinned item that doesn't fit is cut too, and only pinned items get the over-budget warning.

## Vote (one entry in `votes.json` → `votes[]`, or the app's `vote__<id>` turn `meta`)

```json
{"director": "hawk", "title": "Risk & Regulatory Hawk",
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
