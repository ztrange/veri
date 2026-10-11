### 📊 Metrics — issue 1354

Wall time for the issue: 4107 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run bailed — killed-stuck, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 2 | 4 | 1089 | 57851 | 38885 | 0.17 |
| diff | 4 | 2 | 0 | 0 | 1460 | 542 | 87 | 170 | 73824 | 10186282 | 361691 | 3.20 |
| expand | 2 | 1 | 0 | 0 | 119 | 52 | 13 | 26 | 4346 | 604019 | 86302 | 0.71 |
| migrate | 7 | 0 | 3 | 1 | 5893 | 292 | 66 | 128 | 27923 | 3460153 | 234689 | 2.63 |
| exhausted | 1 | 0 | 0 | 0 | 65 | 53 | 12 | 24 | 4682 | 683663 | 58631 | 0.70 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 4 | 3 | 0 | 1348 | 157 | 52 | 100 | 18319 | 2441151 | 226007 | 1.33 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 1333 | 499 | 73 | 144 | 68714 | 9578581 | 273435 | 2.74 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 1 | 4866 | 291 | 55 | 108 | 24831 | 2972236 | 280756 | 3.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 119 | 0.71 |
| migrate | 0 | 0.00 | 5893 | 2.63 |
| exhausted | 0 | 0.00 | 65 | 0.70 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, the tests in test_orchestrate.py, test_parallel_conductors.py and test_status.py (orchestrate.test.sh no longer exists on main) that pin solvable-issues.sh's path, argv, exit status or call count assert instead what each caller does with the solvable set — the conductors orchestrate and parallel-conductors launch, the scope count status prints for a label — taking that set from open-issue and PR listings served by VERI_GH_JSON fixtures or a faked gh, an exit 3 driven by a listing with no labelled open issue and an exit 2 by a listing the selection cannot read, green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 469 | 68 | 134 | 64273 | 9114801 | 252503 | 2.56 | 1034 | n/a | n/a | n/a |  |  | full |
| Each of orchestrate, parallel_conductors and status gives its full answer — exit code, stdout, stderr, and the files and events — when starting solvable-issues.sh as a process would fail, in a case that refuses that start at the process boundary, after solvable_issues gains a function taking the label explicitly and returning the exit code and the ordered issue numbers ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 13 | 26 | 4346 | 604019 | 86302 | 0.71 | unknown | unknown | unknown | unknown |  |  | full |
| Each of orchestrate, parallel_conductors and status gives its full answer — exit code, stdout, stderr, and the files and events — when starting solvable-issues.sh as a process would fail, in a case that refuses that start at the process boundary, after solvable_issues gains a function taking the label explicitly and returning the exit code and the ordered issue numbers ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 8 | 0 | 3 | 1 | 1 | 0 | 345 | 78 | 152 | 32605 | 4143816 | 293320 | 3.33 | unknown | 2/2 | unknown | unknown |  |  | full |
| Before the migrate phase, the tests in test_orchestrate.py, test_parallel_conductors.py and test_status.py that serve a solvable-set listing through run_over_listing (tests/py/conftest.py) also serve it to the test process itself — VERI_GH_JSON set with monkeypatch.setenv, and parallel_conductors' listing (issues.json) placed in the fixture directory that module reads — so a caller that computes the solvable set in-process sees the same listing as the child did; green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 19 | 36 | 9551 | 1071481 | 109188 | 0.64 | 494 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 38 | 24 | 27 | 25 | 25 | 25 | 26 | 25 | 26 |  |  |  |  |
| affected | 314 | 7 | 5 | 310 | 1 | 5 | 25 | 314 | 12 | 329 | 302 | 300 | 300 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 180 | 352 | 111864 | 14991968 | 780198 | 7.41 |
