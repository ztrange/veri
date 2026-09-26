### With VERI_PARALLEL unset (default 1) parallel-conductors.sh runs two solvable issues' conductors one after another — the second starts only after the first has ended ⟦criterion 1⟧
- parallel-conductors.test.sh: both cases invoke the launcher behind the same `env -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES … VERI_GH_JSON=… CLAUDE_BIN=…` prefix; a small hermetic-launch helper would dedupe it. Only two call sites so far, so the helper will pay off once later steps add cases.
### An issue solvable-issues.sh still prints after its conductor finished is not launched a second time in the same invocation ⟦criterion 2⟧
- the stub conductors in timeline_stub, case 4 and case 5 repeat the same prelude (`#!/bin/sh` plus the `n=` sed line) and epilogue (the result JSON line plus `exit 0`); a shared head/tail helper could remove it, but it is 2 lines each and I judged the extra indirection not worth a transform
### A finished conductor whose PR is ready is reported `#<n> — done <pr-url>`, and one whose PR is a draft and whose event log ends in a bail is reported `#<n> — bailed <pr-url>` ⟦criterion 3⟧
- parallel-conductors.sh `report` starts one python3 per launched issue to match its PR; one call could classify every number in `order` at once
- parallel-conductors.sh `report`'s `VERI_GH_JSON`-or-`gh pr list` read repeats the `gh_read` fixture switch in solvable-issues.sh:119-123; sharing it means extracting that switch into `scripts/lib/`
- case 8's stub conductor in parallel-conductors.test.sh writes the same launch/bail event JSON literal on several `printf` lines; one event-line helper would remove that
### A conductor its supervisor killed (supervise exit 2) is reported `#<n> — killed after <VERI_RUN_TIMEOUT>s` ⟦criterion 3⟧
- test case 9 builds its `jump_clock` awake-clock stub inline with printf. It is the one such stub in this file, so no duplicate exists yet to justify extracting it
