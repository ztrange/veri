# Plan for #149 — Refactor leaves apply only structural transforms, and the loop ends when none are left

- [x] `develop-refactor.md` defines structural and cosmetic candidates by what the transform changes
- [x] `develop-refactor.md` tells the leaf to apply only a structural transform and to report nothing left to tidy when only cosmetic candidates remain
- [x] `develop-refactor.md` requires every `CANDIDATES:` line to carry its class
- [x] `refactor-triage.sh` exits 0 and prints the structural candidates when the report lists at least one
- [x] `refactor-triage.sh` exits 3 when the report lists only cosmetic candidates or `none`
- [x] `refactor-triage.sh` exits 2 with a diagnostic on stderr and nothing on stdout when a candidate's class is missing or unknown or the report has no `CANDIDATES:` line
- [x] `SKILL.md`'s refactor loop calls `refactor-triage.sh` after each committed transform, stops on its exit 3 and stops and narrates on its exit 2
- [x] The `### 🛠️ Refactor` comment names the stop condition among the three and lists structural and cosmetic leftovers separately
- [ ] `CLAUDE.md`'s script and suite counts move with the new script and its suite
