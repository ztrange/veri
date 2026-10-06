### 📊 Metrics — issue 1032

Wall time for the issue: 1290 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1046.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 2 | 4 | 1255 | 54006 | 36450 | 0.17 |
| red | 3 | 1 | 0 | 0 | 123 | 109 | 21 | 40 | 9437 | 1013594 | 146792 | 1.39 |
| green | 2 | 1 | 0 | 0 | 95 | 38 | 12 | 24 | 4061 | 516520 | 79647 | 0.65 |
| refactor | 2 | 1 | 0 | 0 | 49 | 27 | 8 | 16 | 2791 | 305496 | 79131 | 0.58 |
| pin | 1 | 1 | 0 | 0 | 22 | 16 | 4 | 8 | 1433 | 149622 | 37253 | 0.19 |
| diff | 2 | 1 | 0 | 0 | 74 | 35 | 11 | 22 | 3405 | 452777 | 77488 | 0.60 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 179 | 94 | 25 | 50 | 9477 | 960473 | 230306 | 1.21 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 196 | 141 | 33 | 64 | 12905 | 1531542 | 226455 | 2.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The locale-rule case in tests/py/test_preserve_attempt.py changes to the locale-independent rule: for the step argument "a—b ⟦x⟧/c'd" the ref name and the .tdd/attempts/ file name preserve-attempt writes are byte-identical under LC_ALL=C, LC_ALL=en_US.UTF-8, LC_ALL=en_US, and with none of LC_ALL/LC_CTYPE/LANG set ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 126 | 33 | 64 | 12160 | 1356133 | 243194 | 1.94 | 314 | unknown | 0/5 | nothing-left |  |  | full |
| For a step argument holding multi-byte UTF-8 characters, '/', an apostrophe and spaces, the ref preserve-attempt.sh creates is accepted by git check-ref-format ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 12 | 24 | 5562 | 629099 | 99629 | 0.87 | unknown | unknown | unknown | unknown |  |  | pin |
| The existing contract cases in tests/preserve-attempt.test.sh and tests/py/test_preserve_attempt.py stay unchanged and green, the locale-rule case alone excepted ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 22 | 3405 | 452777 | 77488 | 0.60 | 95 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The locale-rule case in tests/py/test_preserve_attempt.py changes to the locale-independent rule: for the step argument "a—b ⟦x⟧/c'd" the ref name and the .tdd/attempts/ file name preserve-attempt writes are byte-identical under LC_ALL=C, LC_ALL=en_US.UTF-8, LC_ALL=en_US, and with none of LC_ALL/LC_CTYPE/LANG set ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 49 | 0.58 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 2 | 1 | 0 | 0 | 2 | 0 | 2 | 2 | 0 |
| fast | 15 | 15 | 16 | 15 | 15 |  |  |  |  |  |  |  |
| target | 15 | 0 | 1 | 2 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 58 | 114 | 22382 | 2492015 | 456761 | 3.58 |
