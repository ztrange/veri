### 📊 Metrics — issue 1721

Wall time for the issue: 1168 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 8 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1016 | 0 | 30529 | 0.09 |
| red | 5 | 2 | 0 | 0 | 117 | 96 | 32 | 62 | 10755 | 958488 | 112378 | 0.48 |
| green | 6 | 1 | 1 | 0 | 709 | 180 | 51 | 104 | 13874 | 1637532 | 117999 | 0.94 |
| refactor | 2 | 1 | 0 | 0 | 34 | 10 | 5 | 10 | 917 | 124104 | 26717 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 23 | 17 | 5 | 10 | 1491 | 136935 | 14253 | 0.06 |
| exhausted | 1 | 0 | 0 | 0 | 25 | 21 | 3 | 6 | 924 | 74852 | 12489 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 425 | 105 | 28 | 56 | 8156 | 729379 | 105361 | 0.50 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 248 | 104 | 36 | 72 | 11845 | 1175451 | 119845 | 0.54 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 245 | 123 | 33 | 66 | 8976 | 1027081 | 89159 | 0.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 37 | 0.14 |
| green | 0 | 0.00 | 292 | 0.71 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 25 | 0.10 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `run-finished.sh <issue>` for an issue with no run under `.tdd/wt/` exits 2 and says on stderr that there is no run for that issue; the new script (a `/bin/sh` shim over a `veri/` module, as `status.sh` is) has a no-argument usage line with exit 2 and a declared caller, so the repo-wide audits stay green ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 100 | 31 | 62 | 8275 | 922543 | 106530 | 0.52 | 586 | unknown | 0/5 | nothing-left |  |  | full |
| `run-finished.sh <issue>` exits 0 and prints nothing when the run's state is `done` as `status.sh` reports it, the ledger in the run's worktree has no unchecked step and no `⟂ refactor pending` mark, and the run's PR body has no unticked `⟦human-owed⟧` line ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 14 | 28 | 5594 | 457266 | 39846 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| When the run's state as `status.sh` reports it is not `done`, `run-finished.sh <issue>` exits 1 and prints the line `not-done <state>` ⟦criterion 2⟧ | 7 | 1 | 1 | 0 | 0 | 0 | 170 | 51 | 102 | 14092 | 1552102 | 137460 | 0.95 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `run-finished.sh <issue>` for an issue with no run under `.tdd/wt/` exits 2 and says on stderr that there is no run for that issue; the new script (a `/bin/sh` shim over a `veri/` module, as `status.sh` is) has a no-argument usage line with exit 2 and a declared caller, so the repo-wide audits stay green ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 106 | 18 | 0 | 1 | 1 | 1 | 0 |
| fast | 19 | 17 | 16 | 16 | 16 | 16 | 16 |  |  |
| target | 0 | 0 | 1 | 1 | 0 | 0 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 194 | 28977 | 2931911 | 314365 | 1.76 |
