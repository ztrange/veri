### 📊 Metrics — issue 1469

Wall time for the issue: 2784 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1532.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 779 | 12193 | 36482 | 0.15 |
| diff | 4 | 2 | 0 | 0 | 704 | 107 | 24 | 48 | 12603 | 1228028 | 207043 | 1.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 293 | 36 | 11 | 22 | 3929 | 469587 | 128704 | 0.60 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 420 | 77 | 14 | 28 | 9453 | 770634 | 114821 | 0.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| No case in pytest-leg.test.sh waits on a real clock: the per-case timeout case runs under an injected VERI_PYTEST_TIMEOUT small enough that its over-time case does not sleep, and still shows that case failing, named as a timeout, while the leg reports the other case passed ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 12 | 24 | 3522 | 572770 | 90852 | 0.46 | 290 | n/a | n/a | n/a |  |  | full |
| Cases in pytest-leg.test.sh that assert on the same target's output under the same planted tree share one run of that target instead of each starting its own make, every assertion the suite made before still holds, and each still goes red against a broken Makefile pytest leg ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 12 | 24 | 9081 | 655258 | 116191 | 0.62 | 492 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| fast | 66 | 60 | 61 |
| affected | 41 | 41 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 25 | 50 | 13382 | 1240221 | 243525 | 1.23 |
