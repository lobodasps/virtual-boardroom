<!-- note: Counsel, phase 1. Proposes the market analysis and calibrates the board. -->
TASK: Recommend the market analysis the board needs before it can decide, and calibrate the board to this company's sector and geography.
1. Define 3 to 5 distinct, specific markets or segments within or adjacent to the growth area that this company could realistically enter in its geography. Include the chair's markets if named; you may sharpen or add. For each one, list the questions that decide it and the specific public data to pull, naming the likely primary sources for this sector and geography (government statistics, regulators and their rules, public budgets and procurement portals, industry associations, public company filings, labor market data). Assign the PESTLE dimensions most relevant to each.
2. Calibrate: list 4 to 6 structural realities of this sector and geography (regulators and licensing, buyer types and buying process, labor model, funding and payment cycles, competitive structure). For each seated director, write one sentence on what their lens means here, and give a relevance weight from {{weights.min}} to {{weights.max}} for how much that director's mandate matters to this decision, with a one-line reason.
Framing only: do not state any facts or figures. This is a research plan, not findings.

Reply with only JSON:
{"framing":"<2 sentences: what the board is really deciding>",
 "markets":[{"name":"<short market name>","definition":"<one sentence: customer type, offering, geography>","why":"<why it is worth analyzing for this company>","questions":["<decisive question>"],"data":[{"item":"<data point to find>","sources":"<likely primary sources>"}],"pestle":["political","economic","social","technological","legal","environmental"]}],
 {{calibration_schema}},
 "criteria":"<one sentence on how markets will be screened>"}
<!-- plugin-defaults
calibration_schema: "calibration":{"themes":["<structural reality>"],"lenses":{"<director id>":"<one sentence>"},"weights":{"<director id>":{"w":1,"why":"<one line>"}}}
-->
