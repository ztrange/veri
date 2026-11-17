# Plan for #4232 — PRD 035.5c1: rebase, merge and release are counted as stages

- [x] under VERI_EVENT_STRICT=1 `stage-start`/`stage-end` accept `stage` plan, refactor-loop, structural, rebase, merge and release; JOURNAL.md states them ⟦criterion 1⟧
- [x] `rebase-onto-default.sh` runs as stage `rebase`, each line carrying the issue, its `stage-end` status its exit code, on a rebase and a refusal ⟦criterion 2⟧
- [x] `queued-merge.sh` runs as stage `merge`, each line carrying the branch's issue and written to the main clone, its `stage-end` status its exit code, on a merge and a refusal ⟦criterion 2⟧
- [x] `release-issue.sh` runs as stage `release`, each line carrying the issue, its `stage-end` status its exit code, on a release and on no answer ⟦criterion 2⟧
- [x] `SCRIPTS.md`'s entries for the three scripts state the stage (SC431, SC432, SC433) ⟦criterion 3⟧
