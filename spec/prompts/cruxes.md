<!-- note: Counsel names the cruxes after the sealed openings. The "alarm" part is added when the consensus alarm fires. -->
TASK: NAME THE CRUXES. From the sealed opening positions, in {{words.cruxes}} words or fewer, name the one to three underlying disagreements that explain why the directors split. Classify each as factual (resolvable with evidence), numbers (turns on an estimate) or values (a trade-off such as speed versus safety), and say which directors sit on each side. {{alarm_note}} Neutral: no recommendation.
{{meta_note}}
{"cruxes":[{"question":"<the disagreement as a question>","type":"factual|numbers|values","side_a":{"position":"<short>","directors":["<id>"]},"side_b":{"position":"<short>","directors":["<id>"]}}],"unanimity":{{unanimity}},"unargued_alternative":"<option, or empty>"}
Director ids: {{director_ids}}.
<!-- part:alarm -->
The openings converged on "{{lead_option}}" ({{lead_count}} of {{seat_count}} directors). Treat that as a warning, not a win: make the strongest unargued alternative a crux and name the directors who must argue it at full strength.
<!-- plugin-defaults
alarm_note: [If the consensus alarm fired, insert the alarm paragraph below here.]
meta_note: After the cruxes, on a new line write exactly <<<META and then one JSON object:
unanimity: true|false
director_ids: <id (title) for each seated director>
lead_option: <leading option>
lead_count: <n>
seat_count: <seats>
-->
