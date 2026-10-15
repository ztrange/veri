### 📊 Metrics — issue 1547

Wall time for the issue: 2961 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1573.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 3 | 6 | 1569 | 123958 | 45691 | 0.21 |
| red | 6 | 3 | 0 | 0 | 258 | 170 | 42 | 84 | 18575 | 2233889 | 308393 | 1.64 |
| green | 6 | 3 | 0 | 0 | 1163 | 160 | 42 | 84 | 16783 | 2199459 | 296011 | 1.57 |
| refactor | 6 | 3 | 0 | 0 | 476 | 88 | 30 | 56 | 7821 | 1323736 | 281210 | 1.34 |
| predicate | 1 | 0 | 0 | 0 | 13 | 9 | 4 | 8 | 819 | 171463 | 43048 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 1011 | 191 | 57 | 110 | 18170 | 2674940 | 469861 | 2.33 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 920 | 252 | 64 | 128 | 27397 | 3377565 | 504492 | 2.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On a resumed worktree whose tracked ledger under .tdd/ carries an uncommitted append and whose default branch has moved, preflight step 3's discard followed by rebase-onto-default.sh exits 0 and the append is present afterwards (uncommitted or committed); running the same discard and rebase a second time on that tree also exits 0 — pinned by a case that runs rebase-onto-default.sh after the resume's discard on a real git repo with such an append and a moved default branch ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 171 | 45 | 88 | 18181 | 2373672 | 308414 | 1.65 | 1021 | unknown | 0/5 | nothing-structural |  |  | full |
| A ledger tick written by a Green before its step's green commit, with the run killed before that commit, does not survive the resume: after preflight step 3's discard and rebase, the step reads unticked in the ledger and carries no ⟂ refactor pending mark, while other uncommitted .tdd/ appends are still kept — pinned by a case that writes the tick with tick-ledger.sh --refactor-pending, leaves the green code uncommitted (the kill), and runs the resume's discard ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 30 | 60 | 12169 | 1450976 | 288232 | 1.42 | 622 | unknown | 0/5 | nothing-structural |  |  | full |
| When the saved .tdd/ appends cannot be re-applied after the resume rebase, the resume stops with exit 2 and a stderr message naming the file whose appends failed and the path where they were kept; the saved appends exist at that path and the resume never continues with them dropped — pinned by a case that makes the re-apply fail ⟦criterion 3⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 139 | 43 | 84 | 13648 | 2103899 | 332016 | 1.68 | 525 | unknown | 0/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| On a resumed worktree whose tracked ledger under .tdd/ carries an uncommitted append and whose default branch has moved, preflight step 3's discard followed by rebase-onto-default.sh exits 0 and the append is present afterwards (uncommitted or committed); running the same discard and rebase a second time on that tree also exits 0 — pinned by a case that runs rebase-onto-default.sh after the resume's discard on a real git repo with such an append and a moved default branch ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 274 | 0.48 |
| A ledger tick written by a Green before its step's green commit, with the run killed before that commit, does not survive the resume: after preflight step 3's discard and rebase, the step reads unticked in the ledger and carries no ⟂ refactor pending mark, while other uncommitted .tdd/ appends are still kept — pinned by a case that writes the tick with tick-ledger.sh --refactor-pending, leaves the green code uncommitted (the kill), and runs the resume's discard ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 93 | 0.41 |
| When the saved .tdd/ appends cannot be re-applied after the resume rebase, the resume stops with exit 2 and a stderr message naming the file whose appends failed and the path where they were kept; the saved appends exist at that path and the resume never continues with them dropped — pinned by a case that makes the re-apply fail ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 109 | 0.44 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 168 | 167 | 1 | 8 | 31 | 1 | 2 | 5 | 0 | 2 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 8 | 1 | 1 | 41 | 1 | 1 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | 31 | 7 | 1 | 1 | 1 | 1 | 0 | 2 | 1 | 5 | 0 | 0 | 8 | 1 | 10 | 0 | 10 | 178 | 10 | 11 | 19 | 8 | 11 |
| fast | 55 | 51 | 53 | 56 | 54 | 55 | 55 | 58 | 56 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 2 | 10 | 0 | 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 121 | 238 | 45567 | 6052505 | 974353 | 4.96 |
