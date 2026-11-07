### 📊 Metrics — issue 3235

Wall time for the issue: 28 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 8 planned.
Outcome: the run bailed — step-added-off-route, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1046 | 0 | 18765 | 0.06 |
| red | 11 | 5 | 1 | 0 | 331 | 178 | 53 | 100 | 20213 | 827053 | 163847 | 0.90 |
| green | 10 | 1 | 2 | 0 | 749 | 219 | 71 | 130 | 23319 | 1199795 | 173966 | 1.06 |
| refactor | 1 | 0 | 0 | 0 | 5 | 3 | 2 | 4 | 140 | 17673 | 18652 | 0.05 |
| pin | 1 | 1 | 0 | 0 | 13 | 8 | 3 | 4 | 1115 | 21505 | 13495 | 0.05 |
| red-contradicted | 1 | 0 | 0 | 0 | 29 | 24 | 6 | 12 | 2587 | 113616 | 19512 | 0.09 |
| red-missing | 1 | 0 | 0 | 0 | 16 | 11 | 3 | 6 | 1521 | 44008 | 15233 | 0.06 |
| exhausted | 1 | 0 | 0 | 0 | 37 | 13 | 3 | 6 | 1027 | 39086 | 12334 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 8 | 3 | 0 | 517 | 134 | 40 | 76 | 14601 | 573406 | 130247 | 0.53 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 348 | 166 | 55 | 102 | 18798 | 927392 | 170681 | 0.81 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 326 | 165 | 47 | 86 | 17569 | 761938 | 134876 | 1.01 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 258 | 0.69 |
| green | 327 | 0.34 | 422 | 0.72 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 29 | 0.09 |
| red-missing | 0 | 0.00 | 16 | 0.06 |
| exhausted | 0 | 0.00 | 37 | 0.09 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| metrics.sh prints a `#### Refactor totals` section, after `#### Structural pass`, with one row per step that has a `refactor` event, holding passes (the count of its `refactor` events), transforms (the sum of those events' `transforms`), landed nothing (its passes whose `transforms` is 0) and stopped (each `stopped` reason with its count, e.g. `nothing-left 2, budget 1`) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 102 | 36 | 64 | 10983 | 528004 | 117678 | 0.53 | 529 | 1/2 | 0/5 | nothing-left |  |  | full |
| Guard: a run with two `refactor` passes on one step (transforms 2 then 0, stopped `budget` then `nothing-left`) shows passes 2, transforms 2, landed nothing 1 and stopped `budget 1, nothing-left 1` for that step, a case that fails against a report keeping only the last pass's figures ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 8 | 12 | 3142 | 86053 | 30843 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| The `#### Refactor totals` section ends with one `issue` row whose passes, transforms, landed nothing and stopped are the sums over every step's figures, the stop reasons counted over all passes ⟦criterion 2⟧ | 17 | 4 | 2 | 0 | 0 | 0 | 330 | 97 | 186 | 35797 | 1648679 | 268518 | 1.64 | unknown | red 2/2, green 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| metrics.sh prints a `#### Refactor totals` section, after `#### Structural pass`, with one row per step that has a `refactor` event, holding passes (the count of its `refactor` events), transforms (the sum of those events' `transforms`), landed nothing (its passes whose `transforms` is 0) and stopped (each `stopped` reason with its count, e.g. `nothing-left 2, budget 1`) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 |
| fast | 20 | 24 | 30 | 31 | 28 | 20 | 21 | 21 | 20 | 21 | 20 | 23 | 19 |  |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 1 | 1 | 2 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 142 | 264 | 50968 | 2262736 | 435804 | 2.35 |
