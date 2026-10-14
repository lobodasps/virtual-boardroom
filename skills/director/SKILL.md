---
name: director
description: Manage Virtual Boardroom directors. List the board, add a new director (optionally drafted from a one-line description), edit a persona, choose who is seated by default, remove a director, or attach supporting data files to a director. Use when the user wants to customize board members or give a director data.
argument-hint: "[list | add <description> | edit <director> | attach <director> <files> | seat | remove <director>]"
---

# Manage the board's directors

Directors live in `boardroom/directors/<id>/`:
- `persona.md` has YAML frontmatter (`id`, `title`, `mono`, `color`, `seated_by_default`, `pestle`, `opponents`) and these sections: `## Lens`, `## Mandate`, `## Always presses on` (bulleted, one or more), `## Red line`, `## Thresholds`, `## Blind spots` and `## Voice`. The full format is in `${CLAUDE_PLUGIN_ROOT}/spec/schema.md`. Every field after `## Voice` in that list is optional.
- The folder name is for people; the frontmatter `id` is what sessions, votes and weights use. Never change an existing director's `id`.
- `data/` holds material private to that director.
- `data/shared/` holds material the whole board sees.

If `boardroom/directors/` is missing, run the setup skill first (`${CLAUDE_PLUGIN_ROOT}/skills/setup/SKILL.md`).

## list
Show a table of every director: title, monogram, seated by default, number of private files, number of shared files, and lens.

## add
1. If the user gave a description, for example "a former hospital CFO who obsesses over reimbursement risk", draft a persona from it with this prompt (generated from `spec/prompts/draft-director.md`):

<!-- SPEC:draft-director quote -->
> You design voting directors for a company's AI advisory board. Each director is a composite archetype, never a real or named person.
> The chair wants a new director described as: <the user's description>
> Existing directors (the new one must hold a distinct view that will clash with at least one of them):
> <each existing director's title and lens, one per line>
> Reply with only JSON: {"title":"<role title, 2-5 words>","lens":"<one-sentence motto in the first person plural>","mandate":"<2 sentences: what this director pushes the company toward>","presses":"<the question they always ask>","redLine":"<what they will never accept>","tone":"<voice, a few adjectives>","pestle":["<1-2 of: Political, Economic, Social, Technological, Legal, Environmental>"]}
<!-- /SPEC:draft-director -->

   The director must be a composite archetype, never a real or named person, and must clash with at least one existing director.
2. Choose a monogram of 1 to 3 capital letters that no other director uses (SC is reserved for the Strategy Counsel). Choose a short lowercase `id` that no other director uses, and a kebab-case folder name.
3. Show the draft and ask the user to confirm or edit it. Then write `persona.md`, and create `data/` and `data/shared/`.

## edit
Show the current persona, apply the user's changes, and keep the frontmatter valid. Warn the user that changing the monogram changes the citation tags in future sessions; past sessions keep theirs.

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

Install a missing converter with `pip install --user` only after the user agrees. Then report each file's name, size in characters, and whether it is private or shared. Remind the user that the director cites these files as `[MONO:filename]`.
