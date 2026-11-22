# Plan for #4583 — verify-refactor runs near-duplicates.sh itself and REJECTs a Duplicated Code pair the step added and the refactor left

- [x] `build-verify-prompt.sh refactor` renders, in check 2, the command `<scripts dir>/near-duplicates.sh <step-green sha>`, the scripts directory as reached and the sha the one `--step-green` carried ⟦criterion 1⟧
- [ ] `verify-refactor.md` check 2 tells the verifier to run that command, read both sites of each printed pair, and REJECT a pair meeting the Duplicated Code row even on an empty range, never filing such a pair as out of scope; rows VF24-VF26 grade it PASS ⟦criterion 3⟧
- [ ] `build-verify-prompt.sh refactor` called without `--step-green` refuses with exit 2 and the usage line byte-identical to the one before this issue ⟦criterion 2⟧
