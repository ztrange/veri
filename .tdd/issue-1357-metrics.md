### 📊 Metrics — issue 1357

Wall time for the issue: 3011 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1492.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 865 | 12489 | 32823 | 0.14 |
| diff | 8 | 3 | 1 | 0 | 1380 | 348 | 100 | 196 | 42164 | 5838640 | 403919 | 2.87 |
| expand | 2 | 1 | 0 | 0 | 80 | 22 | 9 | 18 | 2736 | 372796 | 79332 | 0.38 |
| migrate | 3 | 1 | 0 | 0 | 219 | 57 | 19 | 38 | 6463 | 852826 | 126199 | 0.65 |
| contract-a | 2 | 1 | 0 | 0 | 123 | 36 | 14 | 26 | 4213 | 611406 | 88231 | 0.46 |
| red | 1 | 0 | 0 | 0 | 56 | 26 | 6 | 12 | 3907 | 298809 | 50572 | 0.27 |
| pin | 1 | 1 | 0 | 0 | 17 | 12 | 4 | 8 | 1539 | 161956 | 41037 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 509 | 161 | 53 | 104 | 19439 | 2347920 | 373494 | 1.92 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 836 | 166 | 45 | 88 | 19130 | 3060816 | 122104 | 1.23 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 539 | 180 | 55 | 108 | 23318 | 2740186 | 326515 | 1.81 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 983 | 1.75 | 0 | 0.00 |
| expand | 0 | 0.00 | 80 | 0.38 |
| migrate | 0 | 0.00 | 219 | 0.65 |
| contract-a | 0 | 0.00 | 123 | 0.46 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, every case in tests/py/test_supervise.py that pins harvest-usage.sh's path, argv, stdout redirection or exit status asserts its effect instead — one usage record in .tdd/events.jsonl carrying the leaf's role and the leaf environment's VERI_SKILL_COMMIT, and harvest's diagnostic for a log with no closing result record on supervise's stderr ahead of the supervise[<name>]: status line — green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 222 | 61 | 118 | 26187 | 3788031 | 214821 | 1.75 | 1038 | 1/2 | unknown | unknown |  |  | full |
| supervise gives its full answer — exit code, stdout, stderr, and the usage event harvest writes to .tdd/events.jsonl — when starting harvest-usage.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/harvest_usage.py gains that takes the leaf's environment explicitly and writes its diagnostics to supervise's stderr ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 9 | 18 | 2736 | 372796 | 79332 | 0.38 | unknown | unknown | unknown | unknown |  |  | full |
| supervise gives its full answer — exit code, stdout, stderr, and the usage event harvest writes to .tdd/events.jsonl — when starting harvest-usage.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/harvest_usage.py gains that takes the leaf's environment explicitly and writes its diagnostics to supervise's stderr ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 3 | 1 | 0 | 0 | 0 | 0 | 57 | 19 | 38 | 6463 | 852826 | 126199 | 0.65 | unknown | unknown | unknown | unknown |  |  | full |
| Before the migrate phase, the two killed-leaf cases in tests/py/test_supervise.py that fake subprocess.run so harvest-usage.sh never runs — the log ending in a result record with no usage key, and the log that is a directory — let the real harvest-usage.sh run and assert what it writes to supervise's stderr ahead of the supervise[<name>]: status line, green against today's code and unchanged by an in-process harvest call, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦added⟧ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 22 | 44 | 10440 | 1230387 | 101285 | 0.63 | 228 | n/a | n/a | n/a |  |  | full |
| supervise gives its full answer — exit code, stdout, stderr, and the usage event harvest writes to .tdd/events.jsonl — when starting harvest-usage.sh as a process would fail, in a case that refuses that start at the process boundary, by calling a function veri/harvest_usage.py gains that takes the leaf's environment explicitly and writes its diagnostics to supervise's stderr ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 14 | 26 | 4213 | 611406 | 88231 | 0.46 | unknown | unknown | unknown | unknown |  |  | full |
| A case in tests/py/test_supervise.py refuses any start of harvest-usage.sh at the process boundary and asserts supervise's exit code, stdout and stderr, and the usage record harvest appends to .tdd/events.jsonl, for a watched leaf whose log ends in a closing result record and for one whose log has none, are what they were when harvest-usage.sh ran as a process ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 10 | 20 | 5446 | 460765 | 91609 | 0.47 | unknown | unknown | unknown | unknown |  |  | pin |
| No test of supervise fakes harvest-usage.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 17 | 34 | 5537 | 820222 | 87813 | 0.49 | 214 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 26 | 26 | 25 | 25 | 25 | 25 | 25 | 24 | 24 | 25 | 25 |  |  |  |  |  |  |
| affected | 17 | 16 | 15 | 26 | 1 | 27 | 16 | 25 | 7 | 6 | 25 | 15 | 17 | 16 | 24 | 14 | 25 |
| target | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 153 | 300 | 61887 | 8148922 | 822113 | 4.97 |
