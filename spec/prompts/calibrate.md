<!-- note: Counsel. The app calls this on its own when the board is seated without a plan's calibration; the plugin calibrates inside the plan. The parts build the calibration JSON schema for each seated director. -->
TASK: Calibrate the board to this company's sector and geography before the debate. Framing only, no figures.
Reply with only JSON: {{{calibration_schema}}}
<!-- part:schema -->
"calibration":{"themes":["<4-6 structural realities of this sector and geography a board must reason about: regulators and licensing, buyer types and buying process, labor model, funding and payment cycles, competitive structure; framing only, no figures>"],"lenses":{{{lenses}}},"weights":{{{weights}}}}
<!-- part:lens -->
"{{id}}":"<one sentence: what the {{title}}'s lens means for this company's sector and geography>"
<!-- part:weight -->
"{{id}}":{"w":<{{weights.min}}-{{weights.max}}>,"why":"<one line: how much this director's mandate matters to this decision>"}
