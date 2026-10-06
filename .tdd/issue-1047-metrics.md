### 📊 Metrics — issue 1047

Wall time for the issue: 1084 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1053.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 760 | 11866 | 29655 | 0.13 |
| red | 2 | 1 | 0 | 0 | 64 | 57 | 13 | 22 | 5990 | 478883 | 86541 | 0.73 |
| green | 2 | 1 | 0 | 0 | 89 | 44 | 12 | 24 | 4014 | 509636 | 78818 | 0.64 |
| refactor | 2 | 1 | 0 | 0 | 56 | 33 | 10 | 20 | 2893 | 403274 | 78618 | 0.59 |
| diff | 2 | 1 | 0 | 0 | 77 | 38 | 12 | 24 | 3287 | 490934 | 73842 | 0.59 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 149 | 82 | 24 | 46 | 7850 | 909915 | 184905 | 1.00 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 146 | 96 | 24 | 46 | 9094 | 984678 | 162569 | 1.68 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| For a step argument "a—b" that reaches preserve-attempt as a non-UTF-8 locale's decoding of its UTF-8 bytes (simulated by injecting the decoded argv and that locale's filesystem encoding), the ref name and the .tdd/attempts/ file name are byte-identical to those written for the same step under LC_ALL=C and under a UTF-8 locale ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 134 | 35 | 66 | 12897 | 1391793 | 243977 | 1.96 | 301 | unknown | 0/5 | nothing-left |  |  | full |
| The #1032 locale case in tests/py/test_preserve_attempt.py, which pins the UTF-8 and C names to #1046's one-dash-per-character rule, stays unchanged and green ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 12 | 24 | 3287 | 490934 | 73842 | 0.59 | 101 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| For a step argument "a—b" that reaches preserve-attempt as a non-UTF-8 locale's decoding of its UTF-8 bytes (simulated by injecting the decoded argv and that locale's filesystem encoding), the ref name and the .tdd/attempts/ file name are byte-identical to those written for the same step under LC_ALL=C and under a UTF-8 locale ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 56 | 0.59 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 2 | 2 | 0 | 0 | 0 | 0 | 2 | 3 | 2 | 0 |
| fast | 15 | 15 | 15 | 15 | 15 |  |  |  |  |  |  |  |
| target | 0 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 92 | 16944 | 1894593 | 347474 | 2.68 |
