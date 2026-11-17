# Plan for #4230 — PRD 035.5b1: push, readying and the CI wait are counted as stages

- [x] under VERI_EVENT_STRICT=1 `stage-start`/`stage-end` accept `stage` push, draft-pr, full-suite, ready and ci-wait; JOURNAL.md states them ⟦criterion 1⟧
- [x] `push-branch.sh` runs as stage `push`, its `stage-end` status its exit code, on a landed push and a failed one ⟦criterion 2⟧
- [x] `pr-ready.sh` runs as stage `ready`, its `stage-end` status its exit code, on a ready PR and on no answer ⟦criterion 2⟧
- [x] `wait-ci.sh` runs as stage `ci-wait`, its `stage-end` status its exit code, on a green and a red CI ⟦criterion 2⟧
- [ ] `SCRIPTS.md`'s entries for the three scripts state the stage (SC428, SC429, SC430) ⟦criterion 3⟧
