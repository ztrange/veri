# Plan for #2111 — A plan whose guard-subject is also its Red test file cannot pass tests-frozen

Option A of the issue: verify-plan rejects the overlap; `tests_frozen.py` is not changed.

- [x] verify-plan.md carries a REJECT paragraph, in the style of its `⟦replaces-case⟧` and adds-a-script rejections: a plan holding a step that carries `⟦guard-subject: P⟧` where the step text or the spec names `P` as that step's Red test file (the file its failing case is written in) is rejected, the reason naming the step and `P`, because tests-frozen records the Red's test file whole and so a Green editing `P` can never pass `tests-frozen check --step`; the text and every checksum or verbatim pin of verify-plan.md it moves land in one commit ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] a small unit case renders the verify-plan prompt with build_verify_prompt and asserts it carries the guard-subject overlap rejection (a step's `⟦guard-subject: P⟧` that is also its Red test file is a REJECT naming the step and `P`), so reverting the paragraph turns that case red; no production change ⟦criterion 1⟧
- [ ] Option A is the fix: the branch leaves `skills/tdd/scripts/veri/tests_frozen.py` unchanged, so a recorded test case edited or deleted in a recorded file still makes `tests-frozen check --step` exit 1 naming it, as today ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] Option A is the fix: the branch leaves `skills/tdd/scripts/veri/tests_frozen.py` unchanged, so a step whose guard-subject is not its Red file behaves as today ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] Go-red check: with the verify-plan.md paragraph reverted, the new rendered-prompt case fails, watched red and restored ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] skills/tdd/SKILL.md states the overlap rule in its `⟦guard-subject: <path>⟧` paragraph (requirement PL47 of the issue's `## Requirements`) ⟦skill-edit⟧ ⟦criterion 5⟧
