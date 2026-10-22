# Plan for #2062 — grade-prose.sh gives up on the first reply without a BEGIN GRADES block, with no protocol retry

- [x] With VERI_NO_VERDICT_RETRIES unset, a stub grader whose first reply has no BEGIN GRADES block and whose second reply carries a valid all-PASS block makes grade-prose.sh launch the grader a second time and exit 0 on that second reply (a small case, faking only the grader launch) ⟦criterion 1⟧
- [x] With VERI_NO_VERDICT_RETRIES=2 and a stub grader that never writes a BEGIN GRADES block, grade-prose.sh launches the grader exactly three times and then exits 2 with stderr "grade-prose.sh: no verdict obtained: the reply has no BEGIN GRADES block", the same message as today (a small case, faking only the grader launch) ⟦criterion 2⟧
- [x] The grader prompt grade-prose.sh renders states that an empty unit is graded FAIL on every requirement row without using any reading tool, pinned by a small case asserting that text in the rendered prompt ⟦criterion 3⟧ ⟂ refactor pending
