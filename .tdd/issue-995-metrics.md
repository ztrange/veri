### 📊 Metrics — issue 995

Wall time for the issue: 3106 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1039.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 5 | 1 | 2 | 418 | 11453 | 37957 | 0.31 |
| red | 3 | 0 | 0 | 0 | 626 | 172 | 29 | 54 | 17061 | 1574544 | 175469 | 2.06 |
| pin | 3 | 3 | 0 | 0 | 417 | 79 | 16 | 32 | 7450 | 769809 | 144660 | 1.46 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 4 | 4 | 0 | 0 | 426 | 84 | 17 | 34 | 7868 | 781262 | 182617 | 1.77 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 626 | 172 | 29 | 54 | 17061 | 1574544 | 175469 | 2.06 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| build-verify-prompt.test.sh's six diff refusal cases (non-hex base, no --step, no step base, non-hex step base, uppercase step base, 6-character step base) pass --fast-cmd (and --step where the case is not about --step) and each asserts its named check's own stderr message, so each goes red when that check is deleted from build-verify-prompt.sh ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 87 | 15 | 28 | 9313 | 773786 | 106685 | 1.19 | unknown | unknown | unknown | unknown |  |  | pin |
| verify.test.sh's diff arms "with no --step" and "with a non-hex base sha" pass --fast-cmd for both verify.sh and run-verdict.sh and assert the named check's stderr message, so each arm goes red when that check is deleted from build-verify-prompt.sh ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 91 | 16 | 32 | 8481 | 889927 | 110349 | 1.23 | unknown | unknown | unknown | unknown |  |  | pin |
| build-develop-prompt.test.sh's "diff missing test-cmd" case passes an empty test command plus the fast command as the 5th argument and asserts "missing <test-cmd>" on stderr, so it goes red when need test_cmd is deleted from build-develop-prompt.sh ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 14 | 26 | 6717 | 680640 | 103095 | 1.10 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 6 | 88 | 7 | 7 |  |  |  |  |  |  |
| target | 7 | 7 | 7 | 4 | 7 | 7 | 89 | 91 | 91 | 8 | 7 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 46 | 88 | 24929 | 2355806 | 358086 | 3.83 |
