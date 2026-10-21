### 📊 Metrics — issue 1928

Wall time for the issue: 1071 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2020.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 4 | 1 | 2 | 507 | 0 | 29277 | 0.08 |
| diff | 2 | 1 | 0 | 0 | 92 | 65 | 15 | 30 | 5905 | 439883 | 51765 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 35 | 22 | 4 | 8 | 1373 | 74177 | 42844 | 0.13 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 64 | 47 | 12 | 24 | 5039 | 365706 | 38198 | 0.18 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| No case under skills/tdd/scripts/tests/py/ loops over TUNABLES to delenv them, whatever its loop variable is called: the six loops in test_parallel_conductors.py (spelled with `tunable` or `var`, including the two over TUNABLES + ("VERI_GH_DRIVER",)) are removed, test files only and production untouched, every case keeping its name and outcome — where a loop sits in a helper a case calls more than once, the scrub it still does between calls is kept in a form that does not loop over TUNABLES ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 15 | 30 | 5905 | 439883 | 51765 | 0.23 | 128 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| fast | 5 | 5 |
| affected | 3 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 16 | 32 | 6412 | 439883 | 81042 | 0.31 |
