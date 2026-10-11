### 📊 Metrics — issue 1354

Wall time for the issue: 7933 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1474.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 2 | 4 | 1089 | 57851 | 38885 | 0.17 |
| diff | 10 | 5 | 0 | 0 | 3537 | 978 | 181 | 358 | 128219 | 17044293 | 747506 | 5.98 |
| expand | 2 | 1 | 0 | 0 | 119 | 52 | 13 | 26 | 4346 | 604019 | 86302 | 0.71 |
| migrate | 13 | 0 | 6 | 1 | 8102 | 545 | 126 | 246 | 53911 | 6643910 | 484761 | 4.86 |
| exhausted | 2 | 0 | 0 | 0 | 442 | 133 | 28 | 56 | 11211 | 1600554 | 121594 | 1.52 |
| red | 4 | 2 | 0 | 0 | 86 | 69 | 23 | 46 | 8558 | 1082697 | 184374 | 0.93 |
| green | 6 | 2 | 1 | 0 | 334 | 131 | 40 | 78 | 15626 | 1866922 | 232591 | 1.56 |
| refactor | 4 | 2 | 0 | 0 | 119 | 54 | 23 | 46 | 6106 | 1036382 | 166443 | 0.83 |
| rebase | 2 | 1 | 0 | 0 | 922 | 48 | 20 | 38 | 5439 | 978438 | 92144 | 0.52 |
| predicate | 2 | 0 | 0 | 0 | 23 | 18 | 7 | 14 | 2074 | 268093 | 77573 | 0.36 |
| structural | 1 | 0 | 0 | 0 | 303 | 14 | 6 | 12 | 1882 | 267166 | 40805 | 0.21 |
| transform | 1 | 1 | 0 | 0 | 41 | 10 | 4 | 8 | 1077 | 157286 | 39506 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 22 | 15 | 7 | 0 | 3843 | 429 | 147 | 286 | 49881 | 6787927 | 780219 | 4.30 |
| developer | claude-sonnet-5-5 | 14 | 0 | 0 | 0 | 3696 | 1028 | 205 | 408 | 134883 | 18276812 | 921534 | 6.86 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 1 | 6499 | 603 | 121 | 238 | 54774 | 6542872 | 610731 | 6.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 119 | 0.71 |
| migrate | 0 | 0.00 | 8102 | 4.86 |
| exhausted | 0 | 0.00 | 442 | 1.52 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 215 | 1.10 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, the tests in test_orchestrate.py, test_parallel_conductors.py and test_status.py (orchestrate.test.sh no longer exists on main) that pin solvable-issues.sh's path, argv, exit status or call count assert instead what each caller does with the solvable set — the conductors orchestrate and parallel-conductors launch, the scope count status prints for a label — taking that set from open-issue and PR listings served by VERI_GH_JSON fixtures or a faked gh, an exit 3 driven by a listing with no labelled open issue and an exit 2 by a listing the selection cannot read, green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 469 | 68 | 134 | 64273 | 9114801 | 252503 | 2.56 | 1034 | n/a | n/a | n/a |  |  | full |
| Each of orchestrate, parallel_conductors and status gives its full answer — exit code, stdout, stderr, and the files and events — when starting solvable-issues.sh as a process would fail, in a case that refuses that start at the process boundary, after solvable_issues gains a function taking the label explicitly and returning the exit code and the ordered issue numbers ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 13 | 26 | 4346 | 604019 | 86302 | 0.71 | unknown | unknown | unknown | unknown |  |  | full |
| Each of orchestrate, parallel_conductors and status gives its full answer — exit code, stdout, stderr, and the files and events — when starting solvable-issues.sh as a process would fail, in a case that refuses that start at the process boundary, after solvable_issues gains a function taking the label explicitly and returning the exit code and the ordered issue numbers ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 15 | 0 | 6 | 1 | 1 | 0 | 678 | 154 | 302 | 65122 | 8244464 | 606355 | 6.38 | unknown | 4/2 | unknown | unknown |  | exhausted | full |
| Before the migrate phase, the tests in test_orchestrate.py, test_parallel_conductors.py and test_status.py that serve a solvable-set listing through run_over_listing (tests/py/conftest.py) also serve it to the test process itself — VERI_GH_JSON set with monkeypatch.setenv, and parallel_conductors' listing (issues.json) placed in the fixture directory that module reads — so a caller that computes the solvable set in-process sees the same listing as the child did; green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 19 | 36 | 9551 | 1071481 | 109188 | 0.64 | 494 | n/a | n/a | n/a |  |  | full |
| Before the migrate phase, the fakes in test_orchestrate.py, test_parallel_conductors.py and test_status.py answer each process boundary by what is asked (the command and its arguments), never by the order of the calls, so moving or adding a call in solvable_issues (e.g. main_working_tree()) leaves every case's answer unchanged; and parallel_conductors' cases serve the same PR listing (prs.json) to the test process as to the child; green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 99 | 25 | 50 | 10912 | 1502601 | 114631 | 0.72 | 891 | n/a | n/a | n/a |  |  | full |
| Test-only step, changing no production file and green against today's code: every test of orchestrate, parallel_conductors and status puts the solvable set in the listings before the caller asks for it, either through `VERI_GH_JSON` set in the test process's own environment or through a faked `gh` on the test process's PATH that serves successive answers. No answer is written, and no `VERI_GH_JSON` is set, by a fake of `subprocess.run` that runs when a process starts. So each case gives the same answer whether the solvable set is computed in a child process or in-process. ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 286 | 54 | 108 | 37181 | 4597026 | 171136 | 1.52 | 1108 | n/a | n/a | n/a |  |  | full |
| `solvable_issues.solvable` returns exit code 2 and no numbers when the open-issue or PR listing is not readable JSON, the same answer `solvable-issues.sh` gives as a process, rather than raising `JSONDecodeError` to its caller. ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 32 | 64 | 10683 | 1436839 | 258147 | 1.28 | 298 | unknown | 0/5 | nothing-left |  |  | full |
| Each of orchestrate, parallel_conductors and status calls `solvable_issues.solvable` in-process rather than starting `solvable-issues.sh`, with every test of those callers frozen. Its exit code, stdout, stderr and the files and events stay byte-identical, shown by `make test` passing, including in a case that refuses that start at the process boundary. ⟦added⟧ ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 166 | 54 | 106 | 19607 | 2549162 | 325261 | 2.03 | 461 | 1/2 | 1/5 | structural-owed |  |  | full |
| No test of orchestrate, parallel_conductors or status fakes solvable-issues.sh at the process boundary any longer, each such test rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 141 | 52 | 102 | 16774 | 2429367 | 350076 | 1.81 | 160 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `solvable_issues.solvable` returns exit code 2 and no numbers when the open-issue or PR listing is not readable JSON, the same answer `solvable-issues.sh` gives as a process, rather than raising `JSONDecodeError` to its caller. ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.39 |
| Each of orchestrate, parallel_conductors and status calls `solvable_issues.solvable` in-process rather than starting `solvable-issues.sh`, with every test of those callers frozen. Its exit code, stdout, stderr and the files and events stay byte-identical, shown by `make test` passing, including in a case that refuses that start at the process boundary. ⟦added⟧ ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 67 | 0.44 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 38 | 24 | 27 | 25 | 25 | 25 | 26 | 25 | 26 | 25 | 25 | 26 | 25 | 23 | 25 | 23 | 24 | 24 | 25 | 25 | 25 | 25 | 25 | 25 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 314 | 7 | 5 | 310 | 1 | 5 | 25 | 314 | 12 | 329 | 302 | 300 | 300 | 331 | 308 | 1 | 304 | 4 | 295 | 4 | 299 | 325 | 1 | 0 | 5 | 1 | 0 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 1 | 0 | 1 | 12 | 285 | 24 |
| target | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 288 | 285 | 296 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 473 | 932 | 239538 | 31607611 | 2312484 | 17.82 |
