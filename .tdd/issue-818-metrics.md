### 📊 Metrics — issue 818

Wall time for the issue: 2236 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/943.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 11 | 2 | 4 | 1129 | 61902 | 40400 | 0.36 |
| red | 4 | 2 | 0 | 0 | 171 | 139 | 39 | 78 | 13073 | 2154483 | 204150 | 2.33 |
| green | 4 | 2 | 0 | 0 | 480 | 146 | 46 | 86 | 14602 | 2164925 | 185737 | 2.21 |
| refactor | 4 | 2 | 0 | 0 | 176 | 64 | 22 | 44 | 6192 | 994802 | 174976 | 1.72 |
| diff | 2 | 1 | 0 | 0 | 62 | 40 | 10 | 20 | 3474 | 432698 | 84464 | 0.83 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 8 | 8 | 0 | 0 | 466 | 198 | 54 | 106 | 19159 | 2466929 | 348347 | 3.66 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 439 | 202 | 65 | 126 | 19311 | 3341881 | 341380 | 3.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `run-affordable.sh`, when `step-cost.sh --steps` fails with a status other than 0 or 3 (e.g. 1, from an uncaught exception), exits 2 with nothing on stdout ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 52 | 102 | 16467 | 2635560 | 285662 | 3.14 | 473 | unknown | 0/5 | nothing-left |  |  | full |
| `transform-touches-tests.sh`, when `git log <base-sha>..HEAD` fails although `<base-sha>` resolves to a commit (e.g. a missing object in the range), exits 2 — never 0 ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 183 | 55 | 106 | 17400 | 2678650 | 279201 | 3.12 | 520 | unknown | 0/5 | nothing-left |  |  | full |
| the branch's diff changes no existing assertion in those suites, except one that pinned the very outcome criterion 1 or 2 fixes, changed only to that criterion's expected exit code (and stdout/stderr where the criterion names it) ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 10 | 20 | 3474 | 432698 | 84464 | 0.83 | 80 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `run-affordable.sh`, when `step-cost.sh --steps` fails with a status other than 0 or 3 (e.g. 1, from an uncaught exception), exits 2 with nothing on stdout ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 85 | 0.84 |
| `transform-touches-tests.sh`, when `git log <base-sha>..HEAD` fails although `<base-sha>` resolves to a commit (e.g. a missing object in the range), exits 2 — never 0 ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 91 | 0.88 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 3 | 3 | 2 | 3 | 2 | 3 | 22 | 25 | 3 | 5 |
| fast | 40 | 40 | 40 | 40 | 37 | 38 | 45 | 42 |  |  |  |  |
| target | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 119 | 232 | 38470 | 5808810 | 689727 | 7.45 |
