### 📊 Metrics — issue 1843

Wall time for the issue: 1233 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1885.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 542 | 17463 | 12342 | 0.04 |
| red | 3 | 1 | 0 | 0 | 77 | 60 | 17 | 34 | 7218 | 524235 | 57509 | 0.27 |
| green | 2 | 1 | 0 | 0 | 70 | 33 | 13 | 24 | 3148 | 340090 | 28043 | 0.14 |
| refactor | 2 | 1 | 0 | 0 | 43 | 22 | 11 | 22 | 1916 | 310766 | 27004 | 0.12 |
| pin | 1 | 1 | 0 | 0 | 15 | 12 | 4 | 8 | 1321 | 105855 | 13731 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 88 | 51 | 17 | 34 | 5276 | 446358 | 69027 | 0.27 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 125 | 82 | 29 | 56 | 8869 | 852051 | 69602 | 0.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| mutation-parity.sh judges a pairs-table row whose suite is a bash suite (a path not ending in `.py`) and whose old case name contains `::` with the bash runner, so the row gets a verdict (proven/unproven/owed) and the check does not exit 2; pinned by a case ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 93 | 36 | 70 | 9370 | 1019123 | 91611 | 0.42 | 274 | unknown | 1/5 | nothing-structural |  |  | full |
| mutation-parity.sh still judges a pairs-table row whose suite is a `.py` file with the pytest runner, as today, so a pytest suite row keeps getting its verdict; pinned by a case ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 4233 | 261823 | 34676 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| mutation-parity.sh judges a pairs-table row whose suite is a bash suite (a path not ending in `.py`) and whose old case name contains `::` with the bash runner, so the row gets a verdict (proven/unproven/owed) and the check does not exit 2; pinned by a case ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 43 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 0 | 9 | 9 | 9 | 2 | 4 |
| fast | 5 | 5 | 6 |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 46 | 90 | 14145 | 1298409 | 138629 | 0.62 |
