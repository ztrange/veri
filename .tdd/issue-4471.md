# Plan for #4471 — A repo without CI can declare it in CLAUDE.md, not only through VERI_CI_ON_PR in the environment

- [x] With a `veri: ci on pr: 0` line in the working tree's CLAUDE.md and VERI_CI_ON_PR unset, `branch-suite.sh` prints `local` in a tree whose `.github/workflows/` holds a workflow triggering on `pull_request` (the line is parsed by `detect_test_command.answer_from_file` and read only in `ci_on_pr.declared()`) ⟦criterion 4⟧
- [x] With `VERI_CI_ON_PR=1` set and a `veri: ci on pr: 0` line in the working tree's CLAUDE.md, `ci_on_pr.declared()` returns `1`: the variable wins over the line ⟦criterion 5⟧
- [x] With a `veri: ci on pr: 0` line in the working tree's CLAUDE.md and VERI_CI_ON_PR unset, `rebased-tip-suite.sh` prints `local` in a tree whose `.github/workflows/` holds a workflow triggering on `pull_request` ⟦criterion 4⟧
- [x] With a `veri: ci on pr: 1` line in the working tree's CLAUDE.md and VERI_CI_ON_PR unset, `branch-suite.sh` prints `ci` in a tree with no `.github/workflows/` directory ⟦criterion 4⟧
- [x] With `VERI_CI_ON_PR=0` set and a `veri: ci on pr: 1` line in the working tree's CLAUDE.md, `ci_on_pr.declared()` returns `0`: the variable wins over the line ⟦criterion 5⟧
- [x] With a `veri: ci on pr: 1` line in the working tree's CLAUDE.md and VERI_CI_ON_PR unset, `rebased-tip-suite.sh` prints `ci` in a tree with no `.github/workflows/` directory ⟦criterion 4⟧
- [x] With a CLAUDE.md that holds other `veri:` lines but no `veri: ci on pr:` line, and VERI_CI_ON_PR unset, `ci_on_pr.declared()` returns the empty string, so the workflow detection decides as on current main ⟦criterion 7⟧
- [x] With a `veri: ci on pr: 0` line in the target's CLAUDE.md and VERI_CI_ON_PR unset, `ready-check.sh`'s `pull_request` row passes in a tree with no workflow triggering on `pull_request`, `ready_check.py` reading the answer through `ci_on_pr` ⟦criterion 1⟧
- [x] With a `veri: ci on pr: 0` line in the working tree's CLAUDE.md and VERI_CI_ON_PR unset, `wait-ci.sh` exits 0 for a PR whose head has no check runs and no commit statuses, in a tree whose workflow triggers on `pull_request`, as under `VERI_CI_ON_PR=0` ⟦criterion 2⟧
- [x] With a `veri: ci on pr: 0` line in the merge worktree's CLAUDE.md and VERI_CI_ON_PR unset, `queued_merge.py` re-runs the local full suite on the rebased tree before merging, as under `VERI_CI_ON_PR=0`, `queued_merge.py` reading the answer through `ci_on_pr` ⟦criterion 3⟧
- [x] A `veri: ci on pr:` line whose value is neither `0` nor `1`, VERI_CI_ON_PR unset, makes `branch-suite.sh` exit 2 with one stderr line naming the line ⟦criterion 6⟧ ⟂ refactor pending
- [ ] A `veri: ci on pr:` line whose value is neither `0` nor `1`, VERI_CI_ON_PR unset, makes `rebased-tip-suite.sh` exit 2 with one stderr line naming the line ⟦criterion 6⟧
- [ ] A `veri: ci on pr:` line whose value is neither `0` nor `1`, VERI_CI_ON_PR unset, makes `wait-ci.sh` exit 2 with one stderr line naming the line ⟦criterion 6⟧
- [ ] A `veri: ci on pr:` line whose value is neither `0` nor `1`, VERI_CI_ON_PR unset, makes `ready-check.sh` exit 2 with one stderr line naming the line ⟦criterion 6⟧
- [ ] A `veri: ci on pr:` line whose value is neither `0` nor `1`, VERI_CI_ON_PR unset, makes `queued-merge.sh` exit 2 with one stderr line naming the line ⟦criterion 6⟧
- [ ] No module under `skills/tdd/scripts/veri/` other than `ci_on_pr.py` reads `VERI_CI_ON_PR`: a source-scan case (a `tree_audit` case) enforces it, and goes red when a direct `tunables.read("VERI_CI_ON_PR")` is planted in another module ⟦criterion 8⟧
- [ ] `skills/tdd/SCRIPTS.md` names the `veri: ci on pr:` line wherever it names `VERI_CI_ON_PR` as the CI answer, and says the variable wins (rows SC38, SC63, SC130, SC136) ⟦skill-edit⟧ ⟦criterion 9⟧
- [ ] `skills/tdd/DRAFT-PR.md` names the `veri: ci on pr:` line wherever it names `VERI_CI_ON_PR` as the CI answer, and says the variable wins (rows DP88, DP99) ⟦skill-edit⟧ ⟦criterion 9⟧
