### 📊 Metrics — issue 1359

Wall time for the issue: 1983 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1481.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 891 | 12489 | 32487 | 0.14 |
| diff | 4 | 2 | 0 | 0 | 215 | 102 | 27 | 54 | 13937 | 1296949 | 184192 | 1.01 |
| expand | 2 | 1 | 0 | 0 | 343 | 30 | 12 | 22 | 3837 | 481261 | 81153 | 0.41 |
| migrate | 2 | 1 | 0 | 0 | 67 | 32 | 13 | 26 | 3607 | 578773 | 80639 | 0.42 |
| contract-a | 2 | 1 | 0 | 0 | 360 | 31 | 11 | 22 | 3672 | 491329 | 85114 | 0.43 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 234 | 92 | 28 | 56 | 11072 | 1181064 | 240534 | 1.19 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 760 | 110 | 36 | 70 | 14872 | 1679737 | 223051 | 1.21 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 343 | 0.41 |
| migrate | 0 | 0.00 | 67 | 0.42 |
| contract-a | 0 | 0.00 | 360 | 0.43 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, the tests in tests/py/test_refactor_overflow.py that pin refactor-owed.sh list's path, argv or exit status assert, from an owed file written in the case's own scratch tree, the body refactor-overflow passes to gh and refactor-overflow's exit code instead, an exit 3 driven by an owed file holding no structural candidate, green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 13 | 26 | 9231 | 657213 | 99784 | 0.56 | 152 | n/a | n/a | n/a |  |  | full |
| refactor_overflow gives its full answer — exit code, stdout, stderr, and the files and events refactor-owed.sh writes — when starting refactor-owed.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/refactor_owed.py gains that returns the exit code and the listed lines ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 12 | 22 | 3837 | 481261 | 81153 | 0.41 | unknown | unknown | unknown | unknown |  |  | full |
| refactor_overflow gives its full answer — exit code, stdout, stderr, and the files and events refactor-owed.sh writes — when starting refactor-owed.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/refactor_owed.py gains that returns the exit code and the listed lines ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 13 | 26 | 3607 | 578773 | 80639 | 0.42 | unknown | unknown | unknown | unknown |  |  | full |
| refactor_overflow gives its full answer — exit code, stdout, stderr, and the files and events refactor-owed.sh writes — when starting refactor-owed.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/refactor_owed.py gains that returns the exit code and the listed lines ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 11 | 22 | 3672 | 491329 | 85114 | 0.43 | unknown | unknown | unknown | unknown |  |  | full |
| No test of refactor_overflow fakes refactor-owed.sh at the process boundary any longer, each such test rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 14 | 28 | 4706 | 639736 | 84408 | 0.45 | 119 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 24 | 24 | 25 | 24 | 24 | 24 |  |  |  |  |  |  |  |  |
| affected | 1 | 282 | 0 | 3 | 1 | 301 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 64 | 126 | 25944 | 2860801 | 463585 | 2.40 |
