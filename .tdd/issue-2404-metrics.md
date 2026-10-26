### 📊 Metrics — issue 2404

Wall time for the issue: 673 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2412.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.45 over 28 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87762 tokens, largest 123294 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87762 |
| 2 | $0.03 | 89871 |
| 3 | $0.03 | 91782 |
| 4 | $0.02 | 92084 |
| 5 | $0.02 | 92456 |
| 6 | $0.02 | 93129 |
| 7 | $0.02 | 93838 |
| 8 | $0.04 | 96750 |
| 9 | $0.10 | 106470 |
| 10 | $0.03 | 107727 |
| 11 | $0.03 | 108859 |
| 12 | $0.03 | 109602 |
| 13 | $0.03 | 111021 |
| 14 | $0.03 | 112067 |
| 15 | $0.04 | 113708 |
| 16 | $0.03 | 114687 |
| 17 | $0.03 | 115770 |
| 18 | $0.03 | 117027 |
| 19 | $0.03 | 117761 |
| 20 | $0.03 | 118628 |
| 21 | $0.03 | 119329 |
| 22 | $0.03 | 119717 |
| 23 | $0.03 | 120940 |
| 24 | $0.03 | 121387 |
| 25 | $0.03 | 121677 |
| 26 | $0.03 | 121953 |
| 27 | $0.03 | 122720 |
| 28 | $0.03 | 123294 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 4 | 1 | 2 | 535 | 0 | 32895 | 0.09 |
| red | 2 | 1 | 0 | 0 | 44 | 32 | 12 | 24 | 4012 | 373898 | 63968 | 0.24 |
| green | 2 | 1 | 0 | 0 | 94 | 19 | 8 | 16 | 2061 | 230050 | 31985 | 0.12 |
| refactor | 1 | 0 | 0 | 0 | 6 | 4 | 2 | 4 | 182 | 50055 | 16149 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 59 | 27 | 10 | 20 | 3130 | 263229 | 67327 | 0.23 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 91 | 32 | 13 | 26 | 3660 | 390774 | 77670 | 0.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A ⟦fixture-repair⟧ step naming a fixture file the record holds a whole-file digest for but no per-case body records for gets no exemption: after the file's entire contents are replaced, `tests-frozen.sh check --step` exits 1 and names the file — pinned by a medium case (real git repo in tmp_path, driving the CLI via run_cli) in skills/tdd/scripts/tests/py/test_tests_frozen_process.py ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 55 | 22 | 44 | 6255 | 654003 | 112102 | 0.41 | 233 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A ⟦fixture-repair⟧ step naming a fixture file the record holds a whole-file digest for but no per-case body records for gets no exemption: after the file's entire contents are replaced, `tests-frozen.sh check --step` exits 1 and names the file — pinned by a medium case (real git repo in tmp_path, driving the CLI via run_cli) in skills/tdd/scripts/tests/py/test_tests_frozen_process.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 4 | 4 | 4 | 4 |
| fast | 17 | 17 | 16 |  |
| target | 2 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 23 | 46 | 6790 | 654003 | 144997 | 0.50 |
