### 📊 Metrics — issue 1991

Wall time for the issue: 684 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2108.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 2 | 4 | 717 | 46653 | 13104 | 0.04 |
| red | 3 | 1 | 0 | 0 | 84 | 62 | 13 | 26 | 4878 | 362440 | 47016 | 0.20 |
| green | 2 | 1 | 0 | 0 | 59 | 28 | 12 | 20 | 2640 | 271829 | 28333 | 0.12 |
| refactor | 2 | 1 | 0 | 0 | 28 | 13 | 6 | 12 | 920 | 149802 | 25912 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 22 | 15 | 5 | 10 | 1201 | 130871 | 13054 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 102 | 51 | 17 | 34 | 4106 | 428751 | 64943 | 0.25 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 101 | 74 | 21 | 38 | 6250 | 532844 | 62476 | 0.27 |

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
| A unit whose only table is indented four spaces (an indented code block in GFM, outside any fence) reads as having no table: requirements.py's claims refuses it with "unit has no table", while a table indented up to three spaces is still read as the unit's list (small unit-tier case in tests/py/unit/test_requirements.py, run in-process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 74 | 26 | 48 | 6404 | 640560 | 84695 | 0.34 | 216 | unknown | 0/5 | nothing-left |  |  | full |
| A four-space-indented example table placed after a unit's real table (separated by a blank line, outside any fence) is not refused as a "second table": requirements.py's claims returns only the real table's rows (small unit-tier case in tests/py/unit/test_requirements.py, run in-process) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 10 | 20 | 3235 | 274382 | 29620 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A unit whose only table is indented four spaces (an indented code block in GFM, outside any fence) reads as having no table: requirements.py's claims refuses it with "unit has no table", while a table indented up to three spaces is still read as the unit's list (small unit-tier case in tests/py/unit/test_requirements.py, run in-process) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 28 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 3 | 11 | 3 | 3 |
| fast | 5 | 5 | 6 |  |  |  |
| target | 2 | 3 | 2 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 38 | 72 | 10356 | 961595 | 127419 | 0.52 |
