---
name: director
description: Manage Virtual Boardroom directors. List the board, add a new director (optionally drafted from a one-line description), edit a persona, choose who is seated by default, remove a director, or attach supporting data files to a director. Use when the user wants to customize board members or give a director data.
argument-hint: "[list | add <description> | edit <director> | attach <director> <files> | pin <director> <tag> | seat | remove <director> | export [file] | import <file>]"
---

# Manage the board's directors

Directors live in `boardroom/directors/<id>/`:
- `persona.md` has YAML frontmatter (`id`, `title`, `mono`, `color`, `seated_by_default`, `pestle`, `opponents`) and these sections: `## Lens`, `## Mandate`, `## Always presses on` (bulleted, one or more), `## Red line`, `## Thresholds`, `## Blind spots` and `## Voice`. The full format is in `${CLAUDE_PLUGIN_ROOT}/spec/schema.md`. Every field after `## Voice` in that list is optional.
- The folder name is for people; the frontmatter `id` is what sessions, votes and weights use. Never change an existing director's `id`.
- `data/` holds material private to that director.
- `data/shared/` holds material the whole board sees.
- `data/index.json` is the manifest: one entry per item with its citation tag (`[MONO#]`, e.g. `[PW2]`), file, name, size, `shared`, `pinned` and `as_of`. Manage it with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/materials.py"`; never renumber tags by hand. If a director has files but no `index.json` (a v1.1 workspace), run `materials.py index <director-folder>` once to create it.

If `boardroom/directors/` is missing, run the setup skill first (`${CLAUDE_PLUGIN_ROOT}/skills/setup/SKILL.md`).

## list
Show a table of every director: title, monogram, seated by default, number of private items, number of shared items, number pinned, and lens. Read the counts from each `data/index.json`.

## add
1. If the user gave a description, for example "a former hospital CFO who obsesses over reimbursement risk", draft a persona from it with this prompt (generated from `spec/prompts/draft-director.md`):

<!-- SPEC:draft-director quote -->
> You design voting directors for a company's AI advisory board. Each director is a composite archetype, never a real or named person.
> The chair wants a new director described as: <the user's description>
> Existing directors, by id (the new one must hold a distinct view that will clash with at least one of them):
> <each existing director as "- <id>: <title>: <lens>", one per line>
> Reply with only JSON: {"title":"<role title, 2-5 words>","lens":"<one-sentence motto in the first person plural>","mandate":"<2 sentences: what this director pushes the company toward>","presses":"<the question they always ask>","redLine":"<what they will never accept>","thresholds":"<1-2 concrete numbers or tests that move them from yes to no>","blindSpots":"<where this lens tends to misjudge, one sentence>","tone":"<voice, a few adjectives>","pestle":["<1-2 of: Political, Economic, Social, Technological, Legal, Environmental>"],"opponents":["<ids of the 1-2 existing directors they will clash with most>"]}
<!-- /SPEC:draft-director -->

   The director must be a composite archetype, never a real or named person, and must clash with at least one existing director.
2. Choose a monogram of 1 to 3 capital letters that no other director uses (SC is reserved for the Strategy Counsel). Choose a short lowercase `id` that no other director uses, and a kebab-case folder name.
3. Turn the JSON into `persona.md`: `presses` becomes the bulleted `## Always presses on`, `thresholds` goes under `## Thresholds`, `blindSpots` under `## Blind spots`, and `opponents` (ids of existing directors only) into the frontmatter. Pick an unused color from `spec/rules.json` → `custom_palette`.
4. Show the draft and ask the user to confirm or edit it. Then write `persona.md`, and create `data/`, `data/shared/` and an empty `data/index.json` (`[]`).

## edit
Show the current persona, apply the user's changes, and keep the frontmatter valid. Never change `id`. Offer to fill in `## Thresholds` (the numbers that move this director from yes to no), `## Blind spots` (where the lens misjudges) and `opponents` (ids of the directors it should clash with) if they are empty or still hold the placeholder comment. If the monogram changes, existing items keep their tags (so past citations still resolve) and new items use the new monogram.

## seat
Show the roster with `seated_by_default`, and update the flags the user changes. At least 3 directors should be seated by default.

## remove
Confirm first. Move the director's folder to `boardroom/removed/<id>/` rather than deleting it, so the data isn't lost.

## attach
Copy each file into the director's folder:
- `data/` by default, or `data/shared/` if the user says the whole board should see it
- keep the original in `boardroom/originals/<id>/`

Directors can only search text, so convert anything else:
- `.pdf`: extract text to `<name>.txt` with `pdftotext -layout` if installed, otherwise with Python `pypdf`. Keep page breaks as `--- page N ---` lines.
- `.docx`: convert with `pandoc -t gfm` to `<name>.md`, or with Python `python-docx`.
- `.xlsx`/`.xls`: write each sheet to `<name>__<sheet>.csv` with Python `openpyxl` or `pandas`.
- `.txt`, `.md`, `.csv`, `.json`: copy as-is.
- Scanned PDFs with no extractable text: tell the user they need OCR first. Don't guess at the content.

Install a missing converter with `pip install --user` only after the user agrees.

Register every converted file in the manifest, which assigns the next tag:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/materials.py" add boardroom/directors/<folder> <path relative to data/> [--name "<display name>"] [--as-of YYYY-MM] [--pin]
```

**Summary card.** For every item longer than `cards.max_chars` characters (`spec/rules.json`), draft a summary card:

1. Get the text to summarize: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/materials.py" card-source boardroom/directors/<folder> <TAG>`. For a long file this is the first `cards.source_chars` characters plus the headings from the rest.
   - **Card from the whole file (optional, for items over `cards.source_chars`).** Run `materials.py card-parts boardroom/directors/<folder> <TAG>` and tell the user the cost before you start: a quick card is 1 summarizing step; the whole file is `calls_whole` steps (each part, then a merge). If they choose the whole file, write a card for each part with the prompt below, using `card-source … --part N` as the text and "<name> (part N of M)" as the name, then merge the part cards with this prompt (generated from `spec/prompts/summary-card-merge.md`):

<!-- SPEC:summary-card-merge quote -->
> You merge partial summary cards into one summary card for a briefing material. Each partial card covers one consecutive part of the same material, in order. A board director reads the merged card in full every session; the original stays available for searching.
>
> MATERIAL: <material name> (<length in characters> characters, summarized in <number of parts> parts)
> DIRECTOR: the <director title>, whose lens is "<director lens>"
>
> Write 1500 to 3000 characters of plain text in exactly these four sections, each starting on its own line with its label:
> KEY FIGURES: every figure that matters, written exactly as in the material, each with its as-of date or period ("date not stated" if the material gives none).
> NAMED CLIENTS AND PEOPLE: every client, company, agency and person named, with their role.
> CONCLUSIONS: what the material concludes or shows, in its own terms. Mark anything you infer with "(inference)".
> SYNONYMS: one line of alternative terms for the material's key concepts, so searches find them. Separate groups with semicolons and terms within a group with commas, e.g. "margin, gross margin, GP%, gross profit; utilization, billable hours, billable %".
>
> Keep every figure exactly as written, with its as-of date. When parts disagree or update each other, keep the latest and say which part it came from. Merge the SYNONYMS lines into one. Never add a figure, name or date that is not in the partial cards. Reply with the card text only.
>
> PARTIAL CARDS:
> <each part's card, headed "PART n OF N">
<!-- /SPEC:summary-card-merge -->

2. Write the card yourself with this prompt (generated from `spec/prompts/summary-card.md`):

<!-- SPEC:summary-card quote -->
> You write a summary card for one briefing material. A board director reads this card in full every session; the original stays available for searching, so the card must carry what the director needs most often.
>
> MATERIAL: <material name> (<length in characters> characters<"; you see the first … characters and the headings from the rest" if materials.py card-source shortened it>)
> DIRECTOR: the <director title>, whose lens is "<director lens>"
>
> Write 1500 to 3000 characters of plain text in exactly these four sections, each starting on its own line with its label:
> KEY FIGURES: every figure that matters, written exactly as in the material, each with its as-of date or period ("date not stated" if the material gives none).
> NAMED CLIENTS AND PEOPLE: every client, company, agency and person named, with their role.
> CONCLUSIONS: what the material concludes or shows, in its own terms. Mark anything you infer with "(inference)".
> SYNONYMS: one line of alternative terms for the material's key concepts, so searches find them. Separate groups with semicolons and terms within a group with commas, e.g. "margin, gross margin, GP%, gross profit; utilization, billable hours, billable %".
>
> Never add a figure, name or date that is not in the material. Reply with the card text only.
>
> MATERIAL TEXT:
> <the output of materials.py card-source>
<!-- /SPEC:summary-card -->

3. Show the card to the user and let them edit it. Save it next to the original as `<name>.card.md` (in `shared/` if the original is shared), check it with `materials.py check-card <file>` and fix anything it reports. If the user wants to keep it as it is anyway, warn them which rules it breaks and save it on their say-so. Then register it: `materials.py add boardroom/directors/<folder> <path relative to data/> --card-for <TAG> --name "Summary card: <original name>"`. Cards are always pinned; the original stays searchable. The user may skip the card.

Ask whether to pin the original: pinned items are always read in full, up to `OWN_BUDGET` characters (`SHARED_BUDGET` for shared items) from `spec/rules.json`; unpinned items fill the remaining budget and are otherwise searched. Then report each item's tag, name, size in characters, private or shared, and pinned or not, and show `materials.py plan boardroom/directors/<folder>` so the user sees what will be read in full. Warn if pinned items alone exceed the budget.

## pin
Pin or unpin an item by tag: `materials.py pin boardroom/directors/<folder> <TAG>` (add `--off` to unpin). Show the new plan afterwards.

## export
Write every director (including removed ones), its persona and its text materials to a `<name>.board.json` file that the browser app can import (Board members → Import board):

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/board_io.py" export boardroom [exports/<name>.board.json]
```

The file contains the directors' private data and `company.md`. Tell the user where it is, and that `exports/` and `*.board.json` should stay out of git.

## import
Bring in a `<name>.board.json` exported from the app (Board members → Export board) or from another workspace. Run it without a flag first:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/board_io.py" import boardroom <file>
```

It matches directors by `id`, keeps every material's tag, and never deletes anything that isn't in the file. If it exits with status 2, some directors or tags already exist: show the user the list it printed and ask whether to overwrite them or add only the new items, then rerun with `--overwrite` or `--new-only`. Directors whose monogram is already taken are skipped; say so.
