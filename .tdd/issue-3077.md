# Plan for #3077 — PRD 017.3: rerecord-refactored re-records an extraction into a new helper when the case also calls an unchanged asserting helper

- [x] When a verified refactor moves a frozen Go case's assertion lines verbatim into a new helper while the case also calls a helper that existed at green and holds a t.Fatalf, rerecord-refactored re-records the case (exit 0, no skipped: line) and check-earlier then exits 0, the existing helper's assertions counting on both green's and HEAD's side; pinned by a process case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py ⟦criterion 1⟧
- [ ] Go-red control: restoring the comparison in rerecord_refactored to count the called helpers' assertions on HEAD's side only turns the first criterion's case red ⟦human-owed⟧ ⟦criterion 2⟧
