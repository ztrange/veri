### 📊 Metrics — issue 1478

Wall time for the issue: 553 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1916.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 2 | 4 | 618 | 47310 | 13295 | 0.04 |
| cover | 1 | 0 | 0 | 0 | 16 | 12 | 4 | 6 | 778 | 75414 | 12369 | 0.05 |
| transform | 2 | 1 | 0 | 0 | 30 | 24 | 12 | 18 | 2413 | 241011 | 24749 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 19 | 14 | 5 | 10 | 1297 | 120104 | 24494 | 0.09 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 37 | 30 | 13 | 18 | 2512 | 243631 | 25919 | 0.11 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Move Method: `leaf_role.py` gains the revise predicate `is_revise(name)` (true for `revise-*` names and `develop-exhausted`), and `leaf_model.py`'s `resolve` asks it instead of matching leaf names itself; no test file changes. Predicate: `grep -q '^def is_revise(' skills/tdd/scripts/veri/leaf_role.py && ! grep -qE 'startswith\("revise-"\)|develop-exhausted' skills/tdd/scripts/veri/leaf_model.py` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 36 | 16 | 24 | 3191 | 316425 | 37118 | 0.16 | 108 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 18 | 28 | 3809 | 363735 | 50413 | 0.20 |
