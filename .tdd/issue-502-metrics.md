### 📊 Metrics — issue 502

Wall time for the issue: 6730 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/529.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 17 | 2 | 4 | 1742 | 56175 | 36239 | 0.34 |
| red | 15 | 6 | 0 | 0 | 915 | 710 | 160 | 308 | 70753 | 8487549 | 780422 | 9.36 |
| green | 20 | 6 | 4 | 0 | 3879 | 805 | 183 | 360 | 78486 | 8615496 | 785891 | 9.58 |
| refactor | 12 | 6 | 0 | 0 | 680 | 371 | 95 | 186 | 37066 | 4393485 | 513102 | 5.73 |
| pin | 3 | 3 | 0 | 0 | 141 | 75 | 21 | 42 | 7318 | 889531 | 121441 | 1.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3852 | 8.55 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| SKILL.md's `refactor` mark carries a pass index `pass=<k>`: 1 for a step's first refactor pass, and one more each time the triangulation path resumes the refactor loop and reaches the refactor sub-step again | 6 | 3 | 0 | 0 | 0 | 0 | 227 | 53 | 104 | 22404 | 2562468 | 277091 | 3.18 | 713 | unknown | 1/5 | nothing-structural |  |  | full |
| metrics.sh renders a per-pass section keyed by step and pass: a step whose log carries two `refactor` marks (pass=1 and pass=2) shows two rows, each with its own transforms against budget and its own stop reason ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 328 | 76 | 148 | 31788 | 3499986 | 363738 | 4.25 | 1697 | 2/2 | 0/5 | nothing-left |  |  | full |
| A step whose log carries one `refactor` mark (with or without a `pass=` key) renders as it does today: its By-step row keeps the same refactor and stopped cells, and it appears once in the per-pass section ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 19 | 38 | 8424 | 965086 | 92937 | 1.11 | unknown | unknown | unknown | unknown |  |  | pin |
| Each per-pass row carries that pass's verify-refactor verdict, the wall seconds and the cost of that pass's refactor-phase leaves ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 444 | 94 | 184 | 45508 | 4668695 | 435185 | 5.33 | 1966 | 2/2 | 3/5 | structural-owed |  |  | full |
| Each per-pass row carries its own verdict, wall seconds and cost on a log in the order SKILL.md writes it: that pass's refactor leaf, then its verify-refactor verdict, then the conductor's `refactor` mark for the pass ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 250 | 57 | 112 | 24302 | 2791693 | 282494 | 3.30 | 453 | unknown | 2/5 | nothing-structural |  |  | full |
| Each per-pass row carries the count of refactor-phase revises spent in that pass | 6 | 3 | 0 | 0 | 0 | 0 | 213 | 55 | 108 | 19813 | 2645243 | 272920 | 3.11 | 410 | unknown | 1/5 | nothing-structural |  |  | full |
| On a log in the order SKILL.md writes it — a pass's first verify-refactor verdict, then its `refactor` mark, then that pass's revise loop (revise marks, revise-refactor leaves, re-verify verdicts) — the revises, the wall seconds and the cost of that revise loop count toward that pass and not the next one, and the pass's verdict is its last verify-refactor verdict ⟦added⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 211 | 56 | 108 | 21017 | 2629603 | 266060 | 3.08 | 444 | unknown | 1/5 | nothing-structural |  |  | full |
| The per-pass section is part of metrics.sh's `### 📊 Metrics` block whichever mark ended the run — done, bail or stop — so it reaches the issue thread with the rest of the metrics ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 117 | 25 | 48 | 11732 | 1392409 | 110367 | 1.40 | unknown | unknown | unknown | unknown |  |  | pin |
| No existing table's key column or column names change, and the per-pass section adds no column named `kind` (prose says run kind) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 88 | 24 | 46 | 8635 | 1230878 | 100064 | 1.22 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 113 | 0 | 112 | 113 | 1 | 1 | 6 | 6 | 6 | 6 | 7 | 6 | 6 | 6 | 6 | 6 | 6 | 0 | 0 | 59 | 17 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 6 | 7 | 6 | 6 | 6 | 6 | 6 | 0 | 7 | 6 | 7 | 0 | 6 | 7 | 7 | 6 | 6 | 0 | 0 | 66 | 7 | 7 | 0 | 7 | 7 | 7 |
| fast | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 6 | 6 | 6 | 7 | 6 | 6 | 6 | 0 | 6 | 6 | 7 | 7 | 0 | 7 | 7 | 7 | 8 | 7 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 473 | 473 | 473 | 476 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 461 | 900 | 195365 | 22442236 | 2237095 | 26.30 |
