<!-- note: Sealed roll-call vote. Every seated director, in parallel. -->
TASK: SEALED ROLL-CALL VOTE. You cannot see anyone else's vote. Choose exactly one option for the company to pursue as its priority, or "Hold" (pursue none now). Options: {{options_list}}.
Also score EVERY option, including Hold:
- scores: 0-10, how strongly you back it.
- pillar_scores: 0-10, the option judged only on your own mandate.
- ruin_risk: "none", "possible" or "likely". This means an irreversible downside that could sink the company if it pursued that option.
- door: "one-way" (hard to reverse) or "two-way" (easy to reverse).
Reply with only JSON:
{"choice":"<exact option name or Hold>","scores":{{{scores_schema}}},"pillar_scores":{{{scores_schema}}},"ruin_risk":{{{ruin_schema}}},"door":{{{door_schema}}},"support":"strong|conditional","ranking":["<options best to worst>"],"conditions":["<what your vote depends on, max 3>"],"flip_if":"<the one finding that would flip your vote>","confidence":<0-100>,"rationale":"<2-3 sentences in your voice, citing [F#] or material tags for facts>","changed_from_opening":true|false,"change_reason":"<why, or empty>"}
<!-- plugin-defaults
options_list: every approved market by its exact name, "Hold"
scores_schema: "<option>":<0-10>, for every option and Hold
ruin_schema: "<option>":"none|possible|likely", for every option and Hold
door_schema: "<option>":"one-way|two-way", for every option and Hold
-->
