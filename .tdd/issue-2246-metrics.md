### 📊 Metrics — issue 2246

Wall time for the issue: 2032 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 3 planned.
Outcome: the run bailed — killed-stuck, a system failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.58 over 30 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89473 |
| 2 | $0.03 | 90511 |
| 3 | $0.03 | 92479 |
| 4 | $0.02 | 92791 |
| 5 | $0.02 | 93252 |
| 6 | $0.02 | 93559 |
| 7 | $0.02 | 94127 |
| 8 | $0.02 | 94751 |
| 9 | $0.03 | 95698 |
| 10 | $0.05 | 99231 |
| 11 | $0.04 | 101566 |
| 12 | $0.05 | 105472 |
| 13 | $0.08 | 113248 |
| 14 | $0.04 | 115261 |
| 15 | $0.03 | 116217 |
| 16 | $0.03 | 116781 |
| 17 | $0.03 | 117746 |
| 18 | $0.04 | 119243 |
| 19 | $0.03 | 120227 |
| 20 | $0.03 | 121106 |
| 21 | $0.03 | 121912 |
| 22 | $0.03 | 123009 |
| 23 | $0.03 | 123263 |
| 24 | $0.03 | 123517 |
| 25 | $0.03 | 123799 |
| 26 | $0.05 | 126843 |
| 27 | $0.06 | 130939 |
| 28 | $0.03 | 131686 |
| 29 | $0.03 | 132243 |
| 30 | $0.03 | 133067 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1177 | 17442 | 13473 | 0.05 |
| red | 2 | 1 | 0 | 0 | 35 | 21 | 7 | 14 | 2518 | 193443 | 33223 | 0.13 |
| green | 1 | 0 | 0 | 1 | 1802 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 29 | 19 | 4 | 8 | 2258 | 94321 | 28445 | 0.10 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 18 | 11 | 4 | 8 | 1437 | 116564 | 18251 | 0.07 |
| developer | not recorded | 1 | 0 | 0 | 1 | 1802 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 35 | 0.13 |
| green | 0 | 0.00 | 1802 | 0.00 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Every pytest case runs with TMPDIR, and tempfile.gettempdir(), naming a directory inside its own tmp_path, set by the autouse hermetic_environment fixture, so a process the case starts (run-conductor.sh's veri-run-<n>- directory included) makes its temporary entries there: pinned by a small unit case in skills/tdd/scripts/tests/py/unit/test_conftest_guards.py ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 1⟧ | 3 | 1 | 0 | 1 | 1 | 0 | 21 | 7 | 14 | 2518 | 193443 | 33223 | 0.13 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 4 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 8 | 16 | 3695 | 210885 | 46696 | 0.17 |
