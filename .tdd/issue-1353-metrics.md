### 📊 Metrics — issue 1353

Wall time for the issue: 151 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 2 planned.
Outcome: the run bailed — no-verdict, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 793 | 12489 | 32192 | 0.14 |
| migrate | 2 | 0 | 1 | 0 | 55 | 50 | 11 | 22 | 4565 | 553322 | 102598 | 0.86 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 1 | 1 | 0 | 16 | 12 | 4 | 8 | 1415 | 118367 | 69640 | 0.30 |
| developer | claude-opus-5-5 | 1 | 0 | 0 | 0 | 47 | 44 | 8 | 16 | 3943 | 447444 | 65150 | 0.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| migrate | 0 | 0.00 | 55 | 0.86 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Each of harvest_usage, push_branch, run_conductor, supervise, timed_test_run and verify writes its event by calling `veri/event.py`'s function in-process, passing the event's context (issue, step, role and the rest of `CONTEXT`) explicitly, and gives its full answer — exit code, stdout, stderr, and the files and events `event.sh` writes, byte-identical to today — in a case that refuses starting `event.sh` as a process at the process boundary; migrate moves one caller per commit with test files frozen, contract (a) rewrites against the function, or deletes under mutation parity, the tests that faked `event.sh` for these callers, with production frozen ⟦phases: migrate, contract-a⟧ ⟦criterion 1⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 50 | 11 | 22 | 4565 | 553322 | 102598 | 0.86 | unknown | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 12 | 24 | 5358 | 565811 | 134790 | 0.99 |
