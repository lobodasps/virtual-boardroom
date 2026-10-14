<!-- note: Counsel drafts the resolution for ratification (optional stage). -->
TASK: DRAFT RESOLUTION for the board to ratify. Recommend the option with the highest weighted score ({{rec}}) and state the verdict label ({{label}}). In {{words.draft}} words or fewer: the recommendation; the conditions directors asked for (merge duplicates, make each checkable with a number, a date or a test result; where directors differ, pick one and say whose); next steps with dates; the cheapest test; kill criteria; and a mitigation for every ruin flag. Weigh arguments, not headcount: one director with a decisive fact beats three with opinions.
{{fact_rules}}
{{meta_note}}
{"recommendation":"<option>","label":"<verdict label>","conditions":["..."],"next_steps":["..."],"cheapest_test":"...","kill_criteria":"...","mitigations":[{"for":"<director id>","mitigation":"..."}]}
<!-- plugin-defaults
rec: the "rec" in votes.json scoring
label: the "label" in votes.json scoring
fact_rules: Follow the evidence discipline in your agent instructions.
meta_note: After the draft, on a new line write exactly <<<META and then one JSON object:
-->
