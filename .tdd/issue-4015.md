# Plan for #4015 — PRD 024.10: the grader's effort is set in grader.conf

- [x] `grade_prose.grader_model` returns the `model=` value whether an `effort=` line sits above or below it ⟦criterion 7⟧
- [x] with an `effort=<level>` line the grader leaf's argv carries `--effort <level>`; with none, no `--effort` ⟦criterion 1⟧
- [x] an `effort=` value outside low, medium, high, xhigh, max makes `grade-prose.sh` exit 2 naming `grader.conf`, nothing launched ⟦criterion 2⟧
- [x] the `grading` event carries `effort=<level>`, or `effort=default` with no line ⟦criterion 3⟧
- [x] with an `effort=` line `grade_prose.signature` stamps unit text, rows, model and level; with none, today's value ⟦criterion 5⟧
- [x] adding, changing or removing the `effort=` line makes `prose-owed.sh <repo-root>` print every listed unit and exit 1 ⟦criterion 6⟧
- [x] `metrics.sh <n>` prints a `Gradings:` line: count, PASS, REJECT, summed `cost_usd`, efforts seen; none without a `grading` event ⟦criterion 4⟧
- [ ] `skills/tdd/grader.conf` holds a comment naming the `effort=` line, its five levels and the re-grade it owes, and no `effort=` line ⟦criterion 9⟧ ⟦criterion 8⟧
