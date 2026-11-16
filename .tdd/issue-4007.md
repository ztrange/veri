# Plan for #4007 — PRD 024.3: the metrics report shows each role's launch cost

- [x] `harvest-usage.sh <leaf>` adds the three `first_turn_*` fields to the usage event from the first `assistant` record's `usage`, not a later one ⟦criterion 1⟧
- [x] a log with no `assistant` record carrying `usage` gets none of the three fields, the event otherwise unchanged, the exit code today's ⟦criterion 2⟧
- [x] `metrics.sh <n>` prints `#### Launch cost, by role`: per (actor, model) of usage events carrying the fields, conductor excluded, the leaves and the three sums in tokens, no dollar figure ⟦criterion 3⟧
- [x] under the table, a line names how many leaf usage events lacked the fields; none lacking, no line ⟦criterion 4⟧
- [x] with no usage event carrying the fields, the report has no `#### Launch cost, by role` section ⟦criterion 5⟧
