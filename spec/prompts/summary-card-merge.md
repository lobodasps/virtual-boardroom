<!-- note: Whole-file mode for materials over cards.source_chars: each part (cardParts / materials.py card-source --part) is summarized with summary-card.md, then this prompt merges the partial cards into the one card that is shown for editing. -->
You merge partial summary cards into one summary card for a briefing material. Each partial card covers one consecutive part of the same material, in order. A board director reads the merged card in full every session; the original stays available for searching.

MATERIAL: {{name}} ({{chars}} characters, summarized in {{parts}} parts)
DIRECTOR: the {{director_title}}, whose lens is "{{director_lens}}"

{{@summary-card.sections}}

Keep every figure exactly as written, with its as-of date. When parts disagree or update each other, keep the latest and say which part it came from. Merge the SYNONYMS lines into one. Never add a figure, name or date that is not in the partial cards. Reply with the card text only.

PARTIAL CARDS:
{{cards}}
<!-- plugin-defaults
name: <material name>
chars: <length in characters>
parts: <number of parts>
director_title: <director title>
director_lens: <director lens>
cards: <each part's card, headed "PART n OF N">
-->
