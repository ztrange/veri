### 📊 Metrics — issue 1363

Wall time for the issue: 2030 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1493.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 2 | 4 | 1006 | 57634 | 38899 | 0.17 |
| diff | 4 | 2 | 0 | 0 | 251 | 87 | 29 | 56 | 10822 | 1320885 | 171909 | 0.93 |
| migrate | 2 | 1 | 0 | 0 | 378 | 32 | 12 | 22 | 3759 | 476912 | 80730 | 0.41 |
| contract-a | 2 | 1 | 0 | 0 | 343 | 26 | 11 | 22 | 3229 | 469896 | 79238 | 0.40 |
| red | 1 | 0 | 0 | 0 | 26 | 23 | 6 | 12 | 3297 | 284442 | 45529 | 0.24 |
| pin | 1 | 1 | 0 | 0 | 13 | 10 | 3 | 6 | 1157 | 105666 | 40024 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 200 | 85 | 26 | 52 | 9786 | 1065629 | 242772 | 1.18 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 821 | 101 | 37 | 70 | 13484 | 1649806 | 213557 | 1.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| migrate | 0 | 0.00 | 378 | 0.41 |
| contract-a | 0 | 0.00 | 343 | 0.40 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, tests/py/test_tick_issue_criterion.py asserts the issue body tick-issue-criterion PATCHes through gh and its exit code, with no assertion on tick-criterion.sh's path, stdin or exit status; a no-match exit 3 is driven by a matcher no unchecked criterion carries; green against today's code, in a commit touching only paths under skills/tdd/scripts/tests/, and a reverted probe deleting tick_issue_criterion.py:23's call to the sibling turns each rewritten case red ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 17 | 32 | 6954 | 789241 | 89590 | 0.51 | 197 | n/a | n/a | n/a |  |  | full |
| tick_issue_criterion gives its full answer — exit code, stdout, stderr, and the issue body it PATCHes — when starting tick-criterion.sh as a process would fail, in a case that refuses that start at the process boundary, by calling ledger.ledger_tick in-process ⟦phases: migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 12 | 22 | 3759 | 476912 | 80730 | 0.41 | unknown | unknown | unknown | unknown |  |  | full |
| tick_issue_criterion gives its full answer — exit code, stdout, stderr, and the issue body it PATCHes — when starting tick-criterion.sh as a process would fail, in a case that refuses that start at the process boundary, by calling ledger.ledger_tick in-process ⟦phases: migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 11 | 22 | 3229 | 469896 | 79238 | 0.40 | unknown | unknown | unknown | unknown |  |  | full |
| A case in tests/py/test_tick_issue_criterion.py refuses every process start but gh at subprocess.run and still gets tick_issue_criterion.main's full answer: exit 0 with the ticked body PATCHed, exit 3 with the no-match stderr line and no PATCH ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 9 | 18 | 4454 | 390108 | 85553 | 0.43 | unknown | unknown | unknown | unknown |  |  | pin |
| No test of tick_issue_criterion fakes tick-criterion.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 12 | 24 | 3868 | 531644 | 82319 | 0.42 | 104 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 26 | 27 | 24 | 25 | 24 | 23 |  |  |  |  |
| affected | 0 | 25 | 290 | 1 | 0 | 287 | 1 | 1 | 1 | 1 |
| target | 0 | 0 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 63 | 122 | 23270 | 2715435 | 456329 | 2.33 |
