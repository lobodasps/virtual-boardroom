# Changelog

Changes to the Virtual Boardroom: the Claude Code plugin and the Strategy Boardroom browser app.

## 1.3.0

### Printing and reports
- **Print or save as PDF.** A session page can now be printed, or saved as a PDF from your browser's print dialog. Printing shows the whole record: every market's evidence and every collapsed section, in light colors.
- **Download report.** The app can save a session as a standalone page with the roster, verdict, roll call, record of decision, transcript and full evidence pack, ready to print. The plugin's `report.html` also prints cleanly.

### Research
- **The same research rules in both front ends.**
  - Each researcher reports 10 to 18 facts, opens at most 15 pages and takes at most 20 turns.
  - Sources must be from the last 24 months, except for laws, rules and standards still in force.
  - The 3 to 5 facts most likely to swing the vote are re-checked against two independent sources.
  - The evidence register keeps at most 80 facts, and the rest are listed as dropped.
- **A complete research request in the app.** The copy box now holds the full instructions for a Claude chat: the approved markets, their questions and data to pull, and the limits above. The waiting panel lists the limits.

### Directors' data
- **Summary cards.** When you attach a long file or note, a card of 1,500 to 3,000 characters is drafted for you to edit. It holds the key figures with their dates, named clients and people, conclusions, and a line of synonyms. The card is pinned, so the director reads it every session, and the original stays searchable.
  - For files over 100,000 characters, you can choose a quick card (one call) or a card from the whole file (one call per part, plus a merge). The number of calls is shown before anything runs.
  - A card that breaks the length or section rules can still be kept with **Save anyway**. It is marked as saved with warnings.
- **Smarter search.** Searches now also look for synonyms: "margin" also finds "gross margin", "GP%" and "gross profit". The synonyms come from a shared list plus each card's synonyms line. Singular and plural forms match too, so "rebates" finds "rebate".
- **More room per director.** Each director can now read up to 60,000 characters of its own data per call, up from 30,000.

### Planning a session
- **Usage estimate.** Before you convene, the app shows about how many Claude calls and tokens the session will use, and it updates as you change seats, depth or ratification. The plugin quotes the same estimate before it starts.
- **Easier seat changes.** The list of seated directors is now an open panel on the session page. From Board members, you can go back to the session you came from.

### The board
- **The Pathfinder.** The Sustainability & Long-Horizon Maverick is now the **Sustainability & Long-Horizon Pathfinder**: "Positioning for the demand curve—well before the deadline." Its monogram is now **SP**. Data tagged with the old SM monogram keeps its tags and keeps working as citations.

## 1.2.0

### One board, two front ends
- **Built from one spec.** The plugin and the browser app are now built from a single source in `spec/`: the directors, the rules and every prompt. A change to the board is made once and applies to both. Checks fail if the two drift apart.
- **Fixed scoring mismatches.** The plugin and the app now reach identical verdicts from the same votes. They used to round some halves differently.

### Verdicts
- **Red lines count.** In the sealed vote, each director says whether each option is clear of, at risk of, or breaching their red line.
  - A breach on the recommended option caps the verdict at RESHAPE, unless every director who flagged it endorses the ratified resolution.
  - A red line at risk caps the verdict at GO WITH CONDITIONS.
  - Flags appear in the roll call, the verdict and the record of decision, and the draft resolution must answer each one.

### Directors
- **Richer personas.** Directors can now have thresholds (the numbers that move them from yes to no), blind spots, and natural opponents. Opponents are paired more often in cross-examination.
- **Move your board between the app and the plugin.** Export a board, with its directors and their data, to a `.board.json` file and import it on the other side. Import asks before overwriting and never deletes anything.

### Directors' data
- **Citation tags.** Every item has a tag such as `[PW2]`. Old plugin citations such as `[PW:file.csv]` still resolve. Codes that only look like tags, such as CO2 or I95, are no longer mistaken for citations.
- **Pinned items.** Pinned items are always read in full. Other items fill whatever room is left, and anything that doesn't fit can still be searched.

### Reliability
- **Saving warning.** The app shows a clear warning when it can't save, so you know your work will be lost on reload.
