### 📊 Metrics — issue 2374

Wall time for the issue: 1994 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2409.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.27 over 58 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87637 tokens, largest 137568 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87637 |
| 2 | $0.02 | 88141 |
| 3 | $0.03 | 89575 |
| 4 | $0.02 | 90311 |
| 5 | $0.02 | 90744 |
| 6 | $0.02 | 91039 |
| 7 | $0.02 | 91371 |
| 8 | $0.02 | 92027 |
| 9 | $0.02 | 92421 |
| 10 | $0.03 | 93730 |
| 11 | $0.03 | 94550 |
| 12 | $0.02 | 95093 |
| 13 | $0.02 | 95444 |
| 14 | $0.02 | 96111 |
| 15 | $0.02 | 96645 |
| 16 | $0.02 | 97133 |
| 17 | $0.02 | 97748 |
| 18 | $0.03 | 98994 |
| 19 | $0.02 | 99480 |
| 20 | $0.03 | 100846 |
| 21 | $0.08 | 108932 |
| 22 | $0.03 | 109760 |
| 23 | $0.03 | 110413 |
| 24 | $0.03 | 111200 |
| 25 | $0.03 | 112071 |
| 26 | $0.03 | 112905 |
| 27 | $0.03 | 113738 |
| 28 | $0.03 | 114138 |
| 29 | $0.03 | 114793 |
| 30 | $0.03 | 115657 |
| 31 | $0.03 | 116402 |
| 32 | $0.03 | 116864 |
| 33 | $0.03 | 117999 |
| 34 | $0.03 | 118725 |
| 35 | $0.03 | 119564 |
| 36 | $0.03 | 120359 |
| 37 | $0.03 | 121100 |
| 38 | $0.03 | 121745 |
| 39 | $0.03 | 122988 |
| 40 | $0.03 | 123637 |
| 41 | $0.03 | 124533 |
| 42 | $0.04 | 126172 |
| 43 | $0.04 | 127570 |
| 44 | $0.03 | 128352 |
| 45 | $0.03 | 129138 |
| 46 | $0.03 | 130172 |
| 47 | $0.03 | 131055 |
| 48 | $0.03 | 131774 |
| 49 | $0.04 | 133145 |
| 50 | $0.03 | 133738 |
| 51 | $0.04 | 134949 |
| 52 | $0.03 | 135372 |
| 53 | $0.03 | 135638 |
| 54 | $0.03 | 135970 |
| 55 | $0.03 | 136516 |
| 56 | $0.03 | 136845 |
| 57 | $0.03 | 137225 |
| 58 | $0.03 | 137568 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 621 | 0 | 30325 | 0.08 |
| red | 6 | 2 | 0 | 0 | 176 | 122 | 29 | 58 | 12015 | 814895 | 143320 | 0.79 |
| green | 6 | 2 | 1 | 0 | 336 | 75 | 27 | 52 | 6719 | 716745 | 70472 | 0.38 |
| refactor | 2 | 0 | 0 | 0 | 18 | 12 | 5 | 10 | 1075 | 125724 | 27772 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 210 | 57 | 19 | 38 | 5591 | 478632 | 86332 | 0.32 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 262 | 134 | 32 | 64 | 12568 | 914726 | 144228 | 0.87 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 67 | 24 | 11 | 20 | 2271 | 264006 | 41329 | 0.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 235 | 0.26 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `merge-lock.sh gate --pid 1` (no `--` and no command) exits 2, writes the gate usage line to stderr, prints no `Traceback`, and creates no `.tdd/` ⟦criterion 1⟧ | 8 | 2 | 1 | 0 | 0 | 0 | 127 | 35 | 70 | 11601 | 957778 | 151058 | 0.81 | 565 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh gate --pid 1 --` (a `--` with no command after it) exits 2, writes the gate usage line to stderr, prints no `Traceback`, and creates no `.tdd/` ⟦criterion 1⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 82 | 26 | 50 | 8208 | 699586 | 90506 | 0.45 | 322 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `merge-lock.sh gate --pid 1` (no `--` and no command) exits 2, writes the gate usage line to stderr, prints no `Traceback`, and creates no `.tdd/` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.05 |
| `merge-lock.sh gate --pid 1 --` (a `--` with no command after it) exits 2, writes the gate usage line to stderr, prints no `Traceback`, and creates no `.tdd/` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 5 | 4 | 10 | 4 | 14 | 12 | 8 | 8 | 4 | 4 | 5 |
| fast | 24 | 24 | 27 | 34 | 25 | 25 |  |  |  |  |  |  |
| target | 3 | 2 | 4 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 62 | 122 | 20430 | 1657364 | 271889 | 1.34 |
