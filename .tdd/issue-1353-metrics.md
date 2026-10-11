### 📊 Metrics — issue 1353

Wall time for the issue: 3843 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1447.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 793 | 12489 | 32192 | 0.14 |
| migrate | 4 | 1 | 1 | 0 | 529 | 208 | 39 | 78 | 18639 | 2186512 | 209580 | 2.09 |
| diff | 4 | 2 | 0 | 0 | 1666 | 907 | 31 | 64 | 11961 | 2087591 | 151178 | 6.92 |
| expand | 2 | 1 | 0 | 0 | 142 | 58 | 14 | 28 | 5225 | 649239 | 85190 | 0.71 |
| contract-a | 2 | 1 | 0 | 0 | 480 | 96 | 20 | 38 | 8459 | 1068960 | 111300 | 1.02 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 1289 | 112 | 40 | 78 | 12301 | 1752990 | 288433 | 1.45 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 1536 | 1163 | 65 | 132 | 32776 | 4251801 | 301007 | 9.42 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| migrate | 0 | 0.00 | 529 | 2.09 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 142 | 0.71 |
| contract-a | 0 | 0.00 | 480 | 1.02 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Each of harvest_usage, push_branch, run_conductor, supervise, timed_test_run and verify writes its event by calling `veri/event.py`'s function in-process, passing the event's context (issue, step, role and the rest of `CONTEXT`) explicitly, and gives its full answer — exit code, stdout, stderr, and the files and events `event.sh` writes, byte-identical to today — in a case that refuses starting `event.sh` as a process at the process boundary; migrate moves one caller per commit with test files frozen, contract (a) rewrites against the function, or deletes under mutation parity, the tests that faked `event.sh` for these callers, with production frozen ⟦phases: migrate, contract-a⟧ ⟦criterion 1⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 50 | 11 | 22 | 4565 | 553322 | 102598 | 0.86 | unknown | 1/2 | unknown | unknown |  |  | full |
| Before any production change, the tests in test_harvest_usage.py, test_push_branch.py, test_run_conductor.py, test_supervise.py, test_timed_test_run.py and test_verify.py that pin event.sh's argv or exit status assert the record appended to .tdd/events.jsonl instead, green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 828 | 14 | 30 | 4896 | 1204000 | 53570 | 6.03 | 1258 | n/a | n/a | n/a |  |  | full |
| Each of harvest_usage, push_branch, run_conductor, supervise, timed_test_run and verify gives its full answer when starting event.sh as a process would fail, in a case that refuses that start at the process boundary ⟦phases: expand, migrate, contract-a⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 14 | 28 | 5225 | 649239 | 85190 | 0.71 | unknown | unknown | unknown | unknown |  |  | full |
| Each of harvest_usage, push_branch, run_conductor, supervise, timed_test_run and verify gives its full answer when starting event.sh as a process would fail, in a case that refuses that start at the process boundary ⟦phases: expand, migrate, contract-a⟧ ⟦added⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 158 | 28 | 56 | 14074 | 1633190 | 106982 | 1.23 | unknown | unknown | unknown | unknown |  |  | full |
| Each of harvest_usage, push_branch, run_conductor, supervise, timed_test_run and verify gives its full answer when starting event.sh as a process would fail, in a case that refuses that start at the process boundary ⟦phases: expand, migrate, contract-a⟧ ⟦added⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 20 | 38 | 8459 | 1068960 | 111300 | 1.02 | unknown | unknown | unknown | unknown |  |  | full |
| No test of harvest_usage, push_branch, run_conductor, supervise, timed_test_run or verify fakes event.sh at the process boundary any longer, each such test rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 17 | 34 | 7065 | 883591 | 97608 | 0.89 | 473 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 41 | 39 | 39 | 26 | 25 | 26 | 23 | 24 |
| affected | 314 | 311 | 39 | 1 | 108 | 0 | 44 | 290 | 0 | 18 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 105 | 210 | 45077 | 6004791 | 589440 | 10.87 |
