<!-- note: Red-team dissent, run on a consensus alarm or in every deep session. -->
TASK: RED-TEAM DISSENT. {{alarm_prefix}}The board is leaning toward "{{lead_option}}". Counsel gives you the floor to make the strongest possible case against it and for the best alternative, even beyond your usual lens. Name the specific evidence, or missing evidence, that would prove the majority wrong. {{words.redteam}} words max.
{{meta_note}}
{"headline":"<the dissent in one sentence>","confidence":<0-100>}
<!-- part:alarm -->
Counsel has sounded a consensus alarm.
<!-- plugin-defaults
alarm_prefix: 
meta_note: After your remarks, on a new line write exactly <<<META and then one JSON object, nothing after it:
-->
