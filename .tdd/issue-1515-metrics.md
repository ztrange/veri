### 📊 Metrics — issue 1515

Wall time for the issue: 770 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1917.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 20 | 1 | 2 | 712 | 17463 | 12428 | 0.04 |
| cover | 2 | 0 | 0 | 0 | 94 | 55 | 16 | 32 | 5103 | 462449 | 30177 | 0.17 |
| transform | 2 | 1 | 0 | 0 | 84 | 43 | 13 | 26 | 4014 | 380191 | 29946 | 0.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 58 | 25 | 4 | 8 | 1285 | 91456 | 25378 | 0.09 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 142 | 93 | 26 | 52 | 8544 | 768647 | 47173 | 0.28 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: move the duplicated `_solvable()` (scope label, then priority label, `(2, [])` when either is unusable, else the solvable listing) into one `solvable_in_scope()` in `skills/tdd/scripts/veri/solvable_issues.py`, called by `orchestrate.py` and `parallel_conductors.py`, neither of which defines `_solvable()` any more; predicate, false before and true after: `grep -q '^def solvable_in_scope(' skills/tdd/scripts/veri/solvable_issues.py && grep -q 'solvable_in_scope' skills/tdd/scripts/veri/orchestrate.py && grep -q 'solvable_in_scope' skills/tdd/scripts/veri/parallel_conductors.py && ! grep -q '^def _solvable(' skills/tdd/scripts/veri/orchestrate.py skills/tdd/scripts/veri/parallel_conductors.py` ⟦criterion 2⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 98 | 29 | 58 | 9117 | 842640 | 60123 | 0.33 | 189 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 0 | 23 | 1 | 1 | 6 | 0 | 6 | 29 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 30 | 60 | 9829 | 860103 | 72551 | 0.37 |
