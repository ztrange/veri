### 📊 Metrics — issue 2808

Wall time for the issue: 3042 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2812.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.47 over 26 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87289 tokens, largest 131203 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87289 |
| 2 | $0.07 | 94292 |
| 3 | $0.03 | 95639 |
| 4 | $0.04 | 97661 |
| 5 | $0.02 | 98088 |
| 6 | $0.02 | 98554 |
| 7 | $0.02 | 98917 |
| 8 | $0.02 | 99357 |
| 9 | $0.04 | 101962 |
| 10 | $0.04 | 104278 |
| 11 | $0.04 | 106755 |
| 12 | $0.04 | 108894 |
| 13 | $0.03 | 109805 |
| 14 | $0.03 | 110608 |
| 15 | $0.04 | 112239 |
| 16 | $0.03 | 113121 |
| 17 | $0.03 | 114570 |
| 18 | $0.09 | 122378 |
| 19 | $0.05 | 125980 |
| 20 | $0.03 | 126864 |
| 21 | $0.04 | 128172 |
| 22 | $0.03 | 128890 |
| 23 | $0.03 | 129338 |
| 24 | $0.03 | 129710 |
| 25 | $0.03 | 130285 |
| 26 | $0.03 | 131203 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 651 | 0 | 32094 | 0.09 |
| red | 3 | 1 | 0 | 0 | 154 | 75 | 20 | 40 | 9983 | 666519 | 88697 | 0.39 |
| green | 2 | 1 | 0 | 0 | 247 | 33 | 14 | 26 | 3646 | 393707 | 34110 | 0.16 |
| refactor | 1 | 0 | 0 | 0 | 6 | 3 | 2 | 4 | 160 | 49089 | 14332 | 0.04 |
| pin | 1 | 1 | 0 | 0 | 28 | 12 | 5 | 10 | 1245 | 145055 | 17150 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 193 | 38 | 14 | 28 | 4156 | 369601 | 81709 | 0.28 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 250 | 90 | 28 | 54 | 11529 | 884769 | 104674 | 0.47 |

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
| `rerecord-refactored` rewrites the record of a step whose ledger line ends in `⟂ refactor pending`: a case in `skills/tdd/scripts/tests/py/test_tests_frozen_record_check_process.py` records a step, marks it pending, refactors its case with its assertions unchanged, writes a passing `.tdd/verdict-refactor.exit`, runs `rerecord-refactored`, and finds the new body digest in the record; it fails on the current code ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 78 | 28 | 54 | 9039 | 837920 | 113061 | 0.46 | 480 | unknown | 0/5 | nothing-left |  |  | full |
| After that re-record, `check-earlier` on the next step answers exit 0 for the refactored case: a case in `skills/tdd/scripts/tests/py/test_tests_frozen_record_check_process.py` drives the same path and then runs `check-earlier --step <next step>`; it fails on the code before the previous step's fix, so on this step's tree it is a pin whose mutation is reverting that fix ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 13 | 26 | 5995 | 416450 | 41228 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `rerecord-refactored` rewrites the record of a step whose ledger line ends in `⟂ refactor pending`: a case in `skills/tdd/scripts/tests/py/test_tests_frozen_record_check_process.py` records a step, marks it pending, refactors its case with its assertions unchanged, writes a passing `.tdd/verdict-refactor.exit`, runs `rerecord-refactored`, and finds the new body digest in the record; it fails on the current code ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 6 | 7 | 7 | 24 |
| fast | 34 | 34 | 36 |  |
| target | 6 | 6 | 6 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 42 | 82 | 15685 | 1254370 | 186383 | 2.22 (estimate) |
