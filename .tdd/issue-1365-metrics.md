### 📊 Metrics — issue 1365

Wall time for the issue: 3356 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1543.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 15 | 1 | 2 | 1539 | 12193 | 42998 | 0.19 |
| diff | 4 | 2 | 0 | 0 | 466 | 106 | 27 | 54 | 11399 | 1408216 | 200476 | 1.06 |
| expand | 4 | 1 | 1 | 0 | 570 | 114 | 27 | 52 | 9477 | 1304803 | 188108 | 1.25 |
| migrate | 2 | 1 | 0 | 0 | 206 | 42 | 13 | 26 | 4485 | 646218 | 92175 | 0.48 |
| contract-a | 2 | 1 | 0 | 0 | 268 | 49 | 13 | 24 | 4922 | 598072 | 97260 | 0.50 |
| red | 1 | 0 | 0 | 0 | 58 | 45 | 11 | 22 | 5607 | 653154 | 56374 | 0.35 |
| pin | 1 | 1 | 0 | 0 | 19 | 12 | 3 | 6 | 1536 | 122522 | 44966 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 764 | 154 | 40 | 76 | 15134 | 1776644 | 363449 | 1.78 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 454 | 153 | 39 | 78 | 17533 | 2126040 | 258492 | 1.42 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 388 | 76 | 16 | 32 | 6298 | 842494 | 100416 | 0.82 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 570 | 1.25 |
| migrate | 0 | 0.00 | 206 | 0.48 |
| contract-a | 0 | 0.00 | 268 | 0.50 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Test-only step, changing no production file and green against today's code: the tests/py/test_dashboard.py cases that pin metrics.sh's argv or working directory (the /api/metrics cases for live runs 31, 35 and run directory 7) assert instead that /api/metrics answers, for a live run, the report metrics renders from that run's own .tdd/events.jsonl and .tdd/issue-<n>.md, with the dashboard's working directory left unchanged; a reverted probe deleting dashboard.py:116's call to metrics.sh turns each rewritten case red; the commit lists only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 13 | 26 | 6577 | 700657 | 105292 | 0.56 | 235 | n/a | n/a | n/a |  |  | full |
| dashboard's /api/metrics recomputes a live run's report by calling a function of veri/metrics.py that returns the report for an explicit events path and ledger path, never changing the working directory, instead of starting metrics.sh; the shim metrics.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 114 | 27 | 52 | 9477 | 1304803 | 188108 | 1.25 | unknown | 1/2 | unknown | unknown |  |  | full |
| dashboard's /api/metrics recomputes a live run's report by calling a function of veri/metrics.py that returns the report for an explicit events path and ledger path, never changing the working directory, instead of starting metrics.sh; the shim metrics.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 13 | 26 | 4485 | 646218 | 92175 | 0.48 | unknown | unknown | unknown | unknown |  |  | full |
| dashboard's /api/metrics recomputes a live run's report by calling a function of veri/metrics.py that returns the report for an explicit events path and ledger path, never changing the working directory, instead of starting metrics.sh; the shim metrics.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 13 | 24 | 4922 | 598072 | 97260 | 0.50 | unknown | unknown | unknown | unknown |  |  | full |
| dashboard's /api/metrics gives its full answer for a live run — exit code, stdout, stderr, and the files and events metrics writes — when starting metrics.sh as a process is refused at the process boundary, by calling metrics's function in-process (dashboard.py:116); the case that refuses that start is its own test, since the migrate phase freezes tests ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 14 | 28 | 7143 | 775676 | 101340 | 0.55 | unknown | unknown | unknown | unknown |  |  | pin |
| No test of dashboard fakes metrics.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 14 | 28 | 4822 | 707559 | 95184 | 0.50 | 304 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 60 | 62 | 65 | 70 | 70 | 68 | 62 | 70 |  |  |  |
| affected | 1 | 59 | 64 | 108 | 2 | 66 | 9 | 63 | 70 | 3 | 67 |
| target | 1 | 0 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 95 | 186 | 38965 | 4745178 | 722357 | 4.03 |
