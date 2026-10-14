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

Ask whether to pin it: pinned items are always read in full, up to `OWN_BUDGET` characters (`SHARED_BUDGET` for shared items) from `spec/rules.json`; unpinned items fill the remaining budget and are otherwise searched. Then report each item's tag, name, size in characters, private or shared, and pinned or not, and show `materials.py plan boardroom/directors/<folder>` so the user sees what will be read in full. Warn if pinned items alone exceed the budget.

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
