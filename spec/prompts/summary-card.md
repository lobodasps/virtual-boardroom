<!-- note: Drafts the pinned summary card for one briefing material (app: after an upload or "Make card"; plugin: /virtual-boardroom:director attach). The card is shown for editing before it is saved; the original stays searchable. The rest_marker part joins the first cards.source_chars characters to the headings found in the rest. -->
You write a summary card for one briefing material. A board director reads this card in full every session; the original stays available for searching, so the card must carry what the director needs most often.

MATERIAL: {{name}} ({{chars}} characters{{truncated_note}})
DIRECTOR: the {{director_title}}, whose lens is "{{director_lens}}"

Write {{cards.min_chars}} to {{cards.max_chars}} characters of plain text in exactly these four sections, each starting on its own line with its label:
KEY FIGURES: every figure that matters, written exactly as in the material, each with its as-of date or period ("date not stated" if the material gives none).
NAMED CLIENTS AND PEOPLE: every client, company, agency and person named, with their role.
CONCLUSIONS: what the material concludes or shows, in its own terms. Mark anything you infer with "(inference)".
SYNONYMS: one line of alternative terms for the material's key concepts, so searches find them. Separate groups with semicolons and terms within a group with commas, e.g. "margin, gross margin, GP%, gross profit; utilization, billable hours, billable %".

Never add a figure, name or date that is not in the material. Reply with the card text only.

MATERIAL TEXT:
{{text}}
<!-- part:rest_marker -->
[…the rest of the material is not shown. Headings from the rest:]
<!-- part:truncated_note -->
; you see the first {{cards.source_chars}} characters and the headings from the rest
<!-- plugin-defaults
name: <material name>
chars: <length in characters>
truncated_note: <"; you see the first … characters and the headings from the rest" if materials.py card-source shortened it>
director_title: <director title>
director_lens: <director lens>
text: <the output of materials.py card-source>
-->
