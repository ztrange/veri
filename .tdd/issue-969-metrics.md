### 📊 Metrics — issue 969

Wall time for the issue: 2743 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1151.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 7 | 2 | 4 | 698 | 62816 | 40674 | 0.35 |
| red | 1 | 0 | 0 | 0 | 54 | 46 | 8 | 14 | 4593 | 364749 | 51694 | 0.58 |
| pin | 1 | 1 | 0 | 0 | 35 | 27 | 6 | 12 | 3011 | 287936 | 47993 | 0.50 |
| diff | 2 | 1 | 0 | 0 | 198 | 31 | 11 | 22 | 3212 | 483657 | 80850 | 0.81 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 3 | 3 | 0 | 0 | 174 | 52 | 14 | 28 | 5589 | 617392 | 129507 | 1.27 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 125 | 59 | 13 | 24 | 5925 | 581766 | 91704 | 0.97 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In the leaf-count case of tests/py/test_metrics.py, the many-pin and many-sat fixture steps each carry more launch events than two-leaf (at least the old bash fixture's four red-phase launches across two attempts plus the verdict-pin launch), and the case still asserts {"many-pin": "pin", "many-sat": "already-satisfied", "two-leaf": "full"} ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 14 | 26 | 7604 | 652685 | 99687 | 1.08 | unknown | unknown | unknown | unknown |  |  | pin |
| veri/metrics.py is unchanged on the branch ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 11 | 22 | 3212 | 483657 | 80850 | 0.81 | 220 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 2 |
| target | 0 | 1 |  |  |
| fast | 52 | 49 | 51 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 27 | 52 | 11514 | 1199158 | 221211 | 2.24 |
