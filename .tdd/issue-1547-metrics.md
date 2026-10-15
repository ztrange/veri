### 📊 Metrics — issue 1547

Wall time for the issue: 4705 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1573.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 3 | 6 | 1569 | 123958 | 45691 | 0.21 |
| red | 18 | 8 | 0 | 0 | 779 | 472 | 113 | 224 | 47945 | 5828934 | 929934 | 5.00 |
| green | 16 | 8 | 0 | 0 | 3120 | 430 | 119 | 234 | 44508 | 6163512 | 792076 | 4.23 |
| refactor | 16 | 8 | 0 | 0 | 997 | 224 | 72 | 140 | 18094 | 3234740 | 748806 | 3.50 |
| predicate | 2 | 0 | 0 | 0 | 28 | 18 | 7 | 14 | 1384 | 293230 | 85355 | 0.38 |
| pin | 1 | 1 | 0 | 0 | 26 | 18 | 5 | 10 | 1679 | 233743 | 46899 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 26 | 26 | 0 | 0 | 2307 | 504 | 144 | 282 | 45480 | 6818060 | 1214416 | 5.99 |
| developer | claude-sonnet-5-5 | 26 | 0 | 0 | 0 | 2572 | 605 | 163 | 322 | 63705 | 8446395 | 1330308 | 6.80 |
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

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 168 | 167 | 1 | 8 | 31 | 1 | 2 | 5 | 0 | 2 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 8 | 1 | 1 | 41 | 1 | 1 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | 31 | 7 | 1 | 1 | 1 | 1 | 0 | 2 | 1 | 5 | 0 | 0 | 8 | 1 | 10 | 0 | 10 | 178 | 10 | 11 | 19 | 8 | 11 | 12 | 177 | 12 | 14 | 2 | 14 | 180 | 14 | 9 | 166 | 14 | 15 | 15 | 15 | 0 | 32 | 15 | 14 | 16 | 17 | 24 | 17 | 16 |
| fast | 55 | 51 | 53 | 56 | 54 | 55 | 55 | 58 | 56 | 54 | 56 | 55 | 55 | 54 | 55 | 57 | 53 | 51 | 56 | 57 | 54 | 57 | 56 | 55 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 2 | 10 | 0 | 11 | 2 | 2 | 11 | 1 | 11 | 2 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 319 | 628 | 115179 | 15878117 | 2648761 | 13.56 |
