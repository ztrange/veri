### 📊 Metrics — issue 1954

Wall time for the issue: 1957 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1994.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.66 over 41 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85218 |
| 2 | $0.03 | 86443 |
| 3 | $0.03 | 88364 |
| 4 | $0.02 | 88627 |
| 5 | $0.02 | 89067 |
| 6 | $0.02 | 89391 |
| 7 | $0.02 | 89748 |
| 8 | $0.02 | 90044 |
| 9 | $0.02 | 90701 |
| 10 | $0.04 | 92828 |
| 11 | $0.04 | 95111 |
| 12 | $0.03 | 96565 |
| 13 | $0.02 | 97015 |
| 14 | $0.02 | 97539 |
| 15 | $0.02 | 98100 |
| 16 | $0.02 | 98341 |
| 17 | $0.02 | 98996 |
| 18 | $0.03 | 100388 |
| 19 | $0.03 | 101292 |
| 20 | $0.03 | 102476 |
| 21 | $0.04 | 104907 |
| 22 | $0.03 | 105552 |
| 23 | $0.02 | 105895 |
| 24 | $0.03 | 106636 |
| 25 | $0.04 | 108377 |
| 26 | $0.03 | 109082 |
| 27 | $0.02 | 109390 |
| 28 | $0.03 | 109964 |
| 29 | $0.03 | 110428 |
| 30 | $0.03 | 111991 |
| 31 | $0.03 | 112784 |
| 32 | $0.03 | 113702 |
| 33 | $0.03 | 114798 |
| 34 | $0.03 | 116253 |
| 35 | $0.03 | 117075 |
| 36 | $0.03 | 117363 |
| 37 | $0.03 | 117695 |
| 38 | $0.03 | 117996 |
| 39 | $0.03 | 118309 |
| 40 | $0.03 | 118659 |
| 41 | $0.03 | 119002 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 14 | 2 | 4 | 1179 | 46949 | 15683 | 0.06 |
| red | 3 | 0 | 0 | 0 | 89 | 66 | 18 | 24 | 5852 | 354446 | 53991 | 0.23 |
| pin | 3 | 3 | 0 | 0 | 49 | 29 | 9 | 18 | 2577 | 224950 | 37769 | 0.14 |
| diff | 2 | 1 | 0 | 0 | 110 | 48 | 7 | 14 | 1521 | 178832 | 23901 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 102 | 56 | 14 | 28 | 4503 | 346671 | 66005 | 0.24 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 164 | 101 | 22 | 32 | 6626 | 458506 | 65339 | 0.28 |

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
| replaces_case.parse() answers None for a replaces clause in which only a quote-then-separator remains inside a name, `replaces 'a', b' in t/x.test.sh`; pinned by a small in-process unit case in tests/py/unit/test_replaces_case.py that goes red with only the quote-then-separator half (`quote + _JOINT`) of the guard at replaces_case.py:32 deleted; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 9 | 14 | 2814 | 190592 | 29253 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| replaces_case.parse() answers None for a replaces clause in which only a separator-then-quote remains inside a name, `replaces 'a, 'b' in t/x.test.sh`; pinned by a small in-process unit case in tests/py/unit/test_replaces_case.py that goes red with only the separator-then-quote half (`_JOINT + quote`) of the guard at replaces_case.py:32 deleted; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 9 | 14 | 2879 | 190995 | 29585 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| replaces-case-survivors.sh exits 3 with nothing on stdout or stderr for a ⟦replaces-case⟧ step whose clause refusal() passes but parse() cannot read (a quoted clause with no ` in <suite>` after it, such as `replaces 'a', 'b'`); pinned by a small in-process unit case in tests/py/unit/test_replaces_case_survivors.py that goes red with that `return 3` in replaces_case_survivors.py deleted; no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 9 | 14 | 2736 | 197809 | 32922 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| .tdd/issue-1882-refactor-owed.md's `applied` row cites a0444a589 together with its subject "refactor: one replaces_case.refusal shared by both replaces-clause scripts (#1882)" in place of the pre-rebase sha b4a8ca78e…; the rest of that file unchanged ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 7 | 14 | 1521 | 178832 | 23901 | 0.09 | 162 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 2 | 2 |  |  |  |
| target | 2 | 2 | 2 | 2 | 1 | 2 |
| fast | 18 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 36 | 60 | 11129 | 805177 | 131344 | 0.52 |
