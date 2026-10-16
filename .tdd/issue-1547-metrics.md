### 📊 Metrics — issue 1547

Wall time for the issue: 2525 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 13 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1573.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 3 | 6 | 1569 | 123958 | 45691 | 0.21 |
| red | 23 | 9 | 0 | 0 | 1118 | 625 | 149 | 296 | 64532 | 7862084 | 1214924 | 6.51 |
| green | 18 | 9 | 0 | 0 | 3954 | 517 | 142 | 280 | 54486 | 7572310 | 904958 | 4.92 |
| refactor | 18 | 9 | 0 | 0 | 1120 | 255 | 83 | 160 | 20464 | 3708610 | 844162 | 3.95 |
| predicate | 2 | 0 | 0 | 0 | 28 | 18 | 7 | 14 | 1384 | 293230 | 85355 | 0.38 |
| pin | 4 | 4 | 0 | 0 | 206 | 96 | 23 | 46 | 9771 | 1128350 | 193469 | 0.98 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 32 | 32 | 0 | 0 | 2753 | 635 | 179 | 350 | 58375 | 8489186 | 1502142 | 7.44 |
| developer | claude-sonnet-5-5 | 32 | 0 | 0 | 0 | 3602 | 823 | 216 | 428 | 87837 | 11585694 | 1682380 | 8.77 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 92 | 69 | 12 | 24 | 5994 | 613662 | 104037 | 0.76 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On a resumed worktree whose tracked ledger under .tdd/ carries an uncommitted append and whose default branch has moved, preflight step 3's discard followed by rebase-onto-default.sh exits 0 and the append is present afterwards (uncommitted or committed); running the same discard and rebase a second time on that tree also exits 0 — pinned by a case that runs rebase-onto-default.sh after the resume's discard on a real git repo with such an append and a moved default branch ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 171 | 45 | 88 | 18181 | 2373672 | 308414 | 1.65 | 1021 | unknown | 0/5 | nothing-structural |  |  | full |
| A ledger tick written by a Green before its step's green commit, with the run killed before that commit, does not survive the resume: after preflight step 3's discard and rebase, the step reads unticked in the ledger and carries no ⟂ refactor pending mark, while other uncommitted .tdd/ appends are still kept — pinned by a case that writes the tick with tick-ledger.sh --refactor-pending, leaves the green code uncommitted (the kill), and runs the resume's discard ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 30 | 60 | 12169 | 1450976 | 288232 | 1.42 | 622 | unknown | 0/5 | nothing-structural |  |  | full |
| When the saved .tdd/ appends cannot be re-applied after the resume rebase, the resume stops with exit 2 and a stderr message naming the file whose appends failed and the path where they were kept; the saved appends exist at that path and the resume never continues with them dropped — pinned by a case that makes the re-apply fail ⟦criterion 3⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 139 | 43 | 84 | 13648 | 2103899 | 332016 | 1.68 | 525 | unknown | 0/5 | nothing-structural |  |  | full |
| An uncommitted line appended directly after a step line that is itself ticked in the same uncommitted change (the shape add-ledger-step.sh after produces when its anchor is the step being ticked), on a tracked .tdd/ ledger whose default branch has moved, survives preflight step 3's discard run as SKILL.md writes it and then rebase-onto-default.sh, while the tick whose green commit never landed is dropped — the discard judges per changed line, not per hunk — pinned by a case that runs the SKILL.md discard block and then rebase-onto-default.sh on a real git repo ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 35 | 70 | 13389 | 1759159 | 296077 | 1.49 | 688 | unknown | 0/5 | nothing-structural |  |  | full |
| An uncommitted line appended to a tracked .tdd/ file whose last committed line had no trailing newline survives preflight step 3's discard run as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch — pinned by a case that runs the SKILL.md discard block and then rebase-onto-default.sh on a real git repo ⟦added⟧ ⟦criterion 4⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 172 | 41 | 80 | 14917 | 2028411 | 347697 | 1.96 | 730 | 1/2 | 0/5 | nothing-structural |  |  | full |
| The line an uncommitted add-ledger-step.sh instead-of replacement adds to a tracked .tdd/ ledger survives preflight step 3's discard run as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch — pinned by a case that runs the SKILL.md discard block and then rebase-onto-default.sh on a real git repo ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 39 | 76 | 13071 | 1955136 | 292689 | 1.50 | 874 | unknown | 0/5 | nothing-structural |  |  | full |
| When the git apply in preflight step 3's discard (as SKILL.md writes it) cannot re-apply the saved .tdd/ appends, the discard stops with exit 2 and a stderr message naming the file whose appends failed and the path where they are kept, and the appends exist at that path — pinned by a case that runs the SKILL.md discard block and forces that apply to fail ⟦added⟧ ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 33 | 64 | 11407 | 1593175 | 299914 | 1.47 | 540 | unknown | 0/5 | nothing-structural |  |  | full |
| When rebase-onto-default.sh's rebase conflicts and is aborted (its exit 1 path) and the saved .tdd/ appends then cannot be re-applied, it exits 2 with a stderr message naming the file whose appends failed and the path where they are kept, and the appends exist at that path — pinned by a case that forces the re-apply to fail on the conflict-abort path ⟦added⟧ ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 124 | 35 | 70 | 12028 | 1754611 | 295489 | 1.48 | 533 | unknown | 0/5 | nothing-structural |  |  | full |
| When rebase-onto-default.sh's rebase fails without a conflict to abort (its early exit 2 inside the rebase: no rebase directory left, or one already present before it ran) and the saved .tdd/ appends then cannot be re-applied, it exits 2 with a stderr message naming the file whose appends failed and the path where they are kept, and the appends exist at that path — pinned by a case that forces the re-apply to fail on that path ⟦added⟧ ⟦criterion 5⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 51 | 15 | 30 | 4800 | 735120 | 142542 | 0.69 | unknown | unknown | unknown | unknown |  |  | pin |
| After the resume's reset the tracked ledger .tdd/issue-<n>.md is judged by step identity, not by a diff of it: every - [x] step line whose step is not ticked in the committed ledger (its green commit is not on the branch) is unticked and loses its ⟂ refactor pending mark, and every other working-copy line is kept exactly as written — pinned by a case where an uncommitted instead-of replacement sits next to a stale tick, run through preflight step 3's discard as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch: the replacement line is kept and the stale tick is removed ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 162 | 47 | 92 | 17947 | 2604462 | 321710 | 1.73 | 1153 | unknown | 0/5 | nothing-left |  |  | full |
| An uncommitted line inserted right before a ticked step of the tracked ledger is kept, and that ticked step appears exactly once afterwards (not duplicated), after preflight step 3's discard as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch — pinned by a case of that shape ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 12 | 24 | 6097 | 629782 | 106739 | 0.55 | unknown | unknown | unknown | unknown |  |  | pin |
| An uncommitted instead-of replacement whose new step text starts with the replaced step's text is kept as written after preflight step 3's discard as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch — pinned by a case of that shape ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 16 | 32 | 6957 | 870900 | 103976 | 0.57 | unknown | unknown | unknown | unknown |  |  | pin |
| Every tracked .tdd/ file other than the ledger keeps its working-copy content unchanged across preflight step 3's discard as SKILL.md writes it and rebase-onto-default.sh on a moved default branch, a rewritten (not appended) row in .tdd/issue-<n>-metrics.md included — pinned by a case of that shape ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 13 | 26 | 6026 | 705281 | 107373 | 0.56 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| On a resumed worktree whose tracked ledger under .tdd/ carries an uncommitted append and whose default branch has moved, preflight step 3's discard followed by rebase-onto-default.sh exits 0 and the append is present afterwards (uncommitted or committed); running the same discard and rebase a second time on that tree also exits 0 — pinned by a case that runs rebase-onto-default.sh after the resume's discard on a real git repo with such an append and a moved default branch ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 274 | 0.48 |
| A ledger tick written by a Green before its step's green commit, with the run killed before that commit, does not survive the resume: after preflight step 3's discard and rebase, the step reads unticked in the ledger and carries no ⟂ refactor pending mark, while other uncommitted .tdd/ appends are still kept — pinned by a case that writes the tick with tick-ledger.sh --refactor-pending, leaves the green code uncommitted (the kill), and runs the resume's discard ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 93 | 0.41 |
| When the saved .tdd/ appends cannot be re-applied after the resume rebase, the resume stops with exit 2 and a stderr message naming the file whose appends failed and the path where they were kept; the saved appends exist at that path and the resume never continues with them dropped — pinned by a case that makes the re-apply fail ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 109 | 0.44 |
| An uncommitted line appended directly after a step line that is itself ticked in the same uncommitted change (the shape add-ledger-step.sh after produces when its anchor is the step being ticked), on a tracked .tdd/ ledger whose default branch has moved, survives preflight step 3's discard run as SKILL.md writes it and then rebase-onto-default.sh, while the tick whose green commit never landed is dropped — the discard judges per changed line, not per hunk — pinned by a case that runs the SKILL.md discard block and then rebase-onto-default.sh on a real git repo ⟦added⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 113 | 0.45 |
| An uncommitted line appended to a tracked .tdd/ file whose last committed line had no trailing newline survives preflight step 3's discard run as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch — pinned by a case that runs the SKILL.md discard block and then rebase-onto-default.sh on a real git repo ⟦added⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 104 | 0.43 |
| The line an uncommitted add-ledger-step.sh instead-of replacement adds to a tracked .tdd/ ledger survives preflight step 3's discard run as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch — pinned by a case that runs the SKILL.md discard block and then rebase-onto-default.sh on a real git repo ⟦added⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 99 | 0.42 |
| When the git apply in preflight step 3's discard (as SKILL.md writes it) cannot re-apply the saved .tdd/ appends, the discard stops with exit 2 and a stderr message naming the file whose appends failed and the path where they are kept, and the appends exist at that path — pinned by a case that runs the SKILL.md discard block and forces that apply to fail ⟦added⟧ ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 106 | 0.44 |
| When rebase-onto-default.sh's rebase conflicts and is aborted (its exit 1 path) and the saved .tdd/ appends then cannot be re-applied, it exits 2 with a stderr message naming the file whose appends failed and the path where they are kept, and the appends exist at that path — pinned by a case that forces the re-apply to fail on the conflict-abort path ⟦added⟧ ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 99 | 0.43 |
| After the resume's reset the tracked ledger .tdd/issue-<n>.md is judged by step identity, not by a diff of it: every - [x] step line whose step is not ticked in the committed ledger (its green commit is not on the branch) is unticked and loses its ⟂ refactor pending mark, and every other working-copy line is kept exactly as written — pinned by a case where an uncommitted instead-of replacement sits next to a stale tick, run through preflight step 3's discard as SKILL.md writes it and then rebase-onto-default.sh on a moved default branch: the replacement line is kept and the stale tick is removed ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 123 | 0.45 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 168 | 167 | 1 | 8 | 31 | 1 | 2 | 5 | 0 | 2 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 8 | 1 | 1 | 41 | 1 | 1 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | 31 | 7 | 1 | 1 | 1 | 1 | 0 | 2 | 1 | 5 | 0 | 0 | 8 | 1 | 10 | 0 | 10 | 178 | 10 | 11 | 19 | 8 | 11 | 12 | 177 | 12 | 14 | 2 | 14 | 180 | 14 | 9 | 166 | 14 | 15 | 15 | 15 | 0 | 32 | 15 | 14 | 16 | 17 | 24 | 17 | 16 | 20 | 21 | 0 | 0 | 0 | 20 | 21 | 24 | 23 |
| fast | 55 | 51 | 53 | 56 | 54 | 55 | 55 | 58 | 56 | 54 | 56 | 55 | 55 | 54 | 55 | 57 | 53 | 51 | 56 | 57 | 54 | 57 | 56 | 55 | 63 | 62 | 60 | 58 | 62 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 2 | 10 | 0 | 11 | 2 | 2 | 11 | 1 | 11 | 2 | 1 | 2 | 15 | 16 | 15 | 2 | 2 | 2 | 2 | 26 | 2 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 407 | 802 | 152206 | 20688542 | 3288559 | 16.97 |
