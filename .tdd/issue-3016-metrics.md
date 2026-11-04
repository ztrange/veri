### 📊 Metrics — issue 3016

Wall time for the issue: 4036 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 3 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.53 over 66 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90188 tokens, largest 142094 tokens
Conductor context: first turn 142516 tokens, largest 187579 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90188 |
| 2 | $0.09 | 97338 |
| 3 | $0.04 | 98998 |
| 4 | $0.04 | 100660 |
| 5 | $0.04 | 101228 |
| 6 | $0.03 | 101559 |
| 7 | $0.03 | 101904 |
| 8 | $0.03 | 102205 |
| 9 | $0.04 | 102473 |
| 10 | $0.03 | 103074 |
| 11 | $0.03 | 103365 |
| 12 | $0.06 | 107027 |
| 13 | $0.07 | 111603 |
| 14 | $0.07 | 115747 |
| 15 | $0.07 | 121240 |
| 16 | $0.06 | 123749 |
| 17 | $0.04 | 124687 |
| 18 | $0.04 | 125207 |
| 19 | $0.04 | 126180 |
| 20 | $0.04 | 127478 |
| 21 | $0.05 | 128290 |
| 22 | $0.05 | 130020 |
| 23 | $0.04 | 131349 |
| 24 | $0.04 | 132113 |
| 25 | $0.05 | 133133 |
| 26 | $0.04 | 134339 |
| 27 | $0.05 | 135085 |
| 28 | $0.04 | 135683 |
| 29 | $0.04 | 136333 |
| 30 | $0.04 | 137024 |
| 31 | $0.04 | 137333 |
| 32 | $0.04 | 138128 |
| 33 | $0.05 | 138584 |
| 34 | $0.06 | 141771 |
| 35 | $0.04 | 142094 |
| 36 | $0.03 | 142516 |
| 37 | $0.04 | 143368 |
| 38 | $0.04 | 144169 |
| 39 | $0.03 | 144588 |
| 40 | $0.04 | 145732 |
| 41 | $0.04 | 147508 |
| 42 | $0.04 | 149138 |
| 43 | $0.04 | 149956 |
| 44 | $0.03 | 150535 |
| 45 | $0.04 | 151880 |
| 46 | $0.05 | 154821 |
| 47 | $0.04 | 155665 |
| 48 | $0.04 | 157189 |
| 49 | $0.10 | 165215 |
| 50 | $0.05 | 167253 |
| 51 | $0.04 | 168086 |
| 52 | $0.05 | 169639 |
| 53 | $0.04 | 170657 |
| 54 | $0.04 | 171986 |
| 55 | $0.04 | 173206 |
| 56 | $0.04 | 173840 |
| 57 | $0.04 | 174268 |
| 58 | $0.05 | 175873 |
| 59 | $0.04 | 176714 |
| 60 | $0.05 | 178092 |
| 61 | $0.04 | 178951 |
| 62 | $0.04 | 179734 |
| 63 | $0.05 | 180933 |
| 64 | $0.04 | 181581 |
| 65 | $0.04 | 182472 |
| 66 | $0.08 | 187579 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 29 | 13 | 1 | 2 | 791 | 0 | 32091 | 0.09 |
| red | 11 | 4 | 0 | 0 | 831 | 377 | 64 | 126 | 26774 | 1951678 | 308184 | 1.56 |
| green | 8 | 1 | 3 | 0 | 1044 | 270 | 41 | 70 | 14157 | 1008415 | 156097 | 0.63 |
| refactor | 1 | 0 | 0 | 0 | 18 | 4 | 2 | 4 | 137 | 48887 | 14640 | 0.04 |
| pin | 3 | 0 | 3 | 0 | 123 | 69 | 9 | 18 | 4345 | 238052 | 47764 | 0.19 |
| exhausted | 1 | 0 | 0 | 0 | 114 | 23 | 5 | 10 | 2079 | 127050 | 33750 | 0.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 6 | 6 | 0 | 1196 | 353 | 44 | 86 | 16369 | 1150962 | 226793 | 0.85 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 783 | 337 | 64 | 116 | 25859 | 1794433 | 288688 | 1.31 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 180 | 66 | 14 | 28 | 6055 | 428687 | 77045 | 0.59 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 653 | 1.35 |
| green | 0 | 0.00 | 775 | 0.50 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 123 | 0.19 |
| exhausted | 0 | 0.00 | 114 | 0.24 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| pin-recheck replays a `--before` record against the step's tick commit, resolved from the `.tdd/issue-<n>-mutations.md` file's issue number via `git log -1 --format=%H -- .tdd/issue-<n>.md`, not against the `green` the record carries: a medium case (real git and pin-recheck.sh) whose record's `green` is an earlier commit than the ledger's tick commit, and whose replay still restores the files changed between `before` and the tick and reports the kill or stay-green correctly; existing cases with no ledger commit keep their behaviour ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 133 | 21 | 38 | 6350 | 543190 | 106425 | 0.38 | 1033 | unknown | 0/5 | nothing-left |  |  | full |
| `mutation-probe.sh --before` run when the step has no tick commit yet does not stamp HEAD as `green`: a medium case (real git and mutation-probe.sh) that probes at a plan-only HEAD, with the record at `.tdd/issue-<n>-mutations.md` and a ledger `.tdd/issue-<n>.md` whose step is unticked, and asserts the record's `green` is absent or is not that HEAD; the existing cases whose record path names no issue ledger keep their recorded `green` ⟦criterion 2⟧ | 19 | 3 | 6 | 0 | 0 | 0 | 610 | 100 | 190 | 41142 | 2830892 | 454010 | 2.27 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| pin-recheck replays a `--before` record against the step's tick commit, resolved from the `.tdd/issue-<n>-mutations.md` file's issue number via `git log -1 --format=%H -- .tdd/issue-<n>.md`, not against the `green` the record carries: a medium case (real git and pin-recheck.sh) whose record's `green` is an earlier commit than the ledger's tick commit, and whose replay still restores the files changed between `before` and the tick and reports the kill or stay-green correctly; existing cases with no ledger commit keep their behaviour ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 18 | 0.04 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 8 | 12 | 10 | 7 | 6 | 11 | 19 | 13 | 5 | 6 | 5 | 6 | 13 | 7 | 11 | 5 | 7 | 42 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 39 | 51 | 53 | 48 | 46 | 35 | 37 | 73 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 4 | 4 | 4 | 5 | 4 | 3 | 4 | 8 | 6 | 5 | 6 | 6 | 4 | 5 | 5 | 5 | 6 | 7 | 7 | 4 | 5 | 4 | 4 | 7 | 5 | 8 | 5 | 4 | 4 | 3 | 3 | 4 | 4 | 5 | 4 | 6 | 9 | 6 | 4 | 3 | 4 | 8 | 7 | 6 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 122 | 230 | 48283 | 3374082 | 592526 | 6.28 (estimate) |
