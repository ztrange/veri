### 📊 Metrics — issue 2609

Wall time for the issue: 3030 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2611.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.73 over 69 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 84165 tokens, largest 151616 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.53 | 84165 |
| 2 | $0.07 | 90608 |
| 3 | $0.03 | 91640 |
| 4 | $0.02 | 91918 |
| 5 | $0.03 | 93441 |
| 6 | $0.03 | 94346 |
| 7 | $0.02 | 94738 |
| 8 | $0.02 | 95083 |
| 9 | $0.02 | 95370 |
| 10 | $0.02 | 95957 |
| 11 | $0.03 | 96797 |
| 12 | $0.03 | 98543 |
| 13 | $0.02 | 99048 |
| 14 | $0.03 | 99730 |
| 15 | $0.02 | 100109 |
| 16 | $0.03 | 100751 |
| 17 | $0.02 | 101313 |
| 18 | $0.02 | 101841 |
| 19 | $0.03 | 102421 |
| 20 | $0.03 | 103672 |
| 21 | $0.03 | 104647 |
| 22 | $0.02 | 105045 |
| 23 | $0.03 | 105761 |
| 24 | $0.03 | 106432 |
| 25 | $0.02 | 106709 |
| 26 | $0.03 | 107396 |
| 27 | $0.03 | 108009 |
| 28 | $0.04 | 110899 |
| 29 | $0.03 | 111687 |
| 30 | $0.03 | 112304 |
| 31 | $0.04 | 115111 |
| 32 | $0.03 | 116073 |
| 33 | $0.03 | 116442 |
| 34 | $0.03 | 116849 |
| 35 | $0.04 | 118651 |
| 36 | $0.03 | 119515 |
| 37 | $0.03 | 120037 |
| 38 | $0.03 | 121241 |
| 39 | $0.04 | 122646 |
| 40 | $0.03 | 123710 |
| 41 | $0.05 | 127423 |
| 42 | $0.04 | 129456 |
| 43 | $0.04 | 130865 |
| 44 | $0.03 | 131760 |
| 45 | $0.03 | 132742 |
| 46 | $0.03 | 133746 |
| 47 | $0.04 | 135959 |
| 48 | $0.03 | 136515 |
| 49 | $0.03 | 137221 |
| 50 | $0.03 | 138080 |
| 51 | $0.03 | 138853 |
| 52 | $0.03 | 139319 |
| 53 | $0.04 | 140403 |
| 54 | $0.03 | 141040 |
| 55 | $0.04 | 142224 |
| 56 | $0.04 | 143062 |
| 57 | $0.04 | 144960 |
| 58 | $0.04 | 145805 |
| 59 | $0.04 | 146577 |
| 60 | $0.04 | 147540 |
| 61 | $0.04 | 149058 |
| 62 | $0.03 | 149318 |
| 63 | $0.03 | 149618 |
| 64 | $0.03 | 150144 |
| 65 | $0.03 | 150387 |
| 66 | $0.03 | 150611 |
| 67 | $0.03 | 150908 |
| 68 | $0.03 | 151266 |
| 69 | $0.03 | 151616 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 709 | 0 | 31374 | 0.09 |
| red | 6 | 3 | 0 | 0 | 184 | 143 | 28 | 50 | 12049 | 717615 | 150592 | 0.72 |
| green | 5 | 2 | 0 | 0 | 395 | 131 | 32 | 64 | 11360 | 1020460 | 93036 | 0.45 |
| red-supersede | 1 | 0 | 0 | 0 | 109 | 99 | 11 | 22 | 9297 | 579301 | 61075 | 0.30 |
| pin | 1 | 0 | 1 | 0 | 26 | 21 | 5 | 10 | 2029 | 144669 | 18674 | 0.08 |
| refactor | 2 | 0 | 0 | 0 | 18 | 11 | 4 | 8 | 529 | 96802 | 27515 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 303 | 105 | 24 | 48 | 8065 | 628699 | 125857 | 0.46 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 76 | 61 | 13 | 24 | 7049 | 359568 | 82049 | 0.46 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 362 | 245 | 44 | 84 | 20859 | 1570580 | 174360 | 0.80 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| pin | 26 | 0.08 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Two grade-prose.sh calls in one tree, for two different units, each leave their own cost readable afterwards: neither call's grader log nor its cost line is overwritten by the other's. Pinned by a case (in tests/py/unit/test_grade_prose.py, in-process, faking only the leaf launch) driving two grading calls with a stub grader that prints a distinct cost per call, then reading both costs back ⟦criterion 1⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 330 | 61 | 120 | 29185 | 2082603 | 265598 | 1.31 | 824 | 1/2 | 0/5 | nothing-left |  |  | full |
| A row retry within one grade-prose.sh call (launch_rows, the follow-up launch for missing requirement rows) leaves the first attempt's grader log and cost readable too, not overwritten by the retry's launch. Pinned by a case (in tests/py/unit/test_grade_prose.py, in-process, faking only the leaf launch) whose stub grader prints a distinct cost per launch ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 75 | 19 | 34 | 6079 | 476244 | 85294 | 0.32 | 376 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Two grade-prose.sh calls in one tree, for two different units, each leave their own cost readable afterwards: neither call's grader log nor its cost line is overwritten by the other's. Pinned by a case (in tests/py/unit/test_grade_prose.py, in-process, faking only the leaf launch) driving two grading calls with a stub grader that prints a distinct cost per call, then reading both costs back ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.04 |
| A row retry within one grade-prose.sh call (launch_rows, the follow-up launch for missing requirement rows) leaves the first attempt's grader log and cost readable too, not overwritten by the retry's launch. Pinned by a case (in tests/py/unit/test_grade_prose.py, in-process, faking only the leaf launch) whose stub grader prints a distinct cost per launch ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 2 | 3 | 3 | 95 |
| target | 3 | 2 | 3 |  |  |  |  |  |  |  |  |  |
| fast | 26 | 25 | 29 | 29 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 156 | 35973 | 2558847 | 382266 | 4.45 (estimate) |
