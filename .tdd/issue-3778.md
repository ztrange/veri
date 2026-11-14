# Plan for #3778 — A refused tests-frozen record after verify-red does not stop the conductor before develop-green

- [x] `tests-frozen.sh record --step <step> --red-case <red-test-id> <test-file>` over a Red case that no longer exists exits 1 and writes a refusal event to `.tdd/events.jsonl` naming the deleted case, pinned by a case that runs `record --red-case` over a deleted case and reads the event ⟦criterion 2⟧
- [x] `tests-frozen.sh record` refusing with exit 2 (no answer: a `record --step <step>` given no test file) writes a refusal event to `.tdd/events.jsonl` carrying its exit code ⟦criterion 2⟧ ⟂ refactor pending
- [ ] `skills/tdd/SKILL.md`: the verify-red PASS record step runs `tests-frozen.sh record --step … --red-case '<red-test-id>' <test-path>… > .tdd/verify-red.reason`, captures `rc=$?` and stops on a non-zero status before the comment or any leaf launch — exit 1 a verify-red REJECT spending `REVISE_BUDGET`, exit 2 a bail (requirement CY24) ⟦skill-edit⟧ ⟦criterion 1⟧
