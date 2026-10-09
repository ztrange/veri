# Plan for #1292 — add-ledger-step.sh --criterion refuses a criterion no step carries yet, forcing a mis-tag on a criterion added mid-run

- [x] add-ledger-step.sh --criterion <k>, given a whole number k ≥ 1 that no ledger step carries yet, inserts every new step tagged with criterion k and exits 0 — replacing #1224's case that expected exit 2 for an uncarried criterion ⟦criterion 1⟧
- [x] add-ledger-step.sh --criterion <k> refuses a k that is not a whole number ≥ 1 (0, a word, a negative, an empty value) with exit 2 and one stderr line naming that value, leaving the ledger byte-identical ⟦criterion 1⟧
- [x] SKILL.md beside the uncovered-spec add-ledger-step.sh call no longer tells the conductor to bail when no ledger step carries criterion k, since the script now accepts it ⟦criterion 2⟧
- [x] SKILL.md's add-ledger-step.sh entry under The scripts says --criterion <k> tags the added steps with criterion k for any whole number k ≥ 1, carried or not, and lists the real exit-2 cases including a k that is not a whole number ≥ 1 ⟦criterion 2⟧ ⟂ refactor pending
- [ ] SKILL.md's Refactor-loop sub-step 4 (an uncovered-spec flag) sends each behaviour into the add-ledger-step.sh call for the criterion it serves, one call per criterion, instead of into one shared call ⟦criterion 2⟧
- [ ] SKILL.md beside the uncovered-spec add-ledger-step.sh calls says each per-criterion call emits its own step-added event, anchored on the step and carrying added=<that call's count> ⟦criterion 2⟧
