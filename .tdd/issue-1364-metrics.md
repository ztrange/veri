### 📊 Metrics — issue 1364

Wall time for the issue: 3321 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1533.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 909 | 12193 | 37775 | 0.16 |
| diff | 4 | 2 | 0 | 0 | 474 | 125 | 32 | 64 | 15298 | 1798439 | 208887 | 1.17 |
| expand | 2 | 1 | 0 | 0 | 193 | 49 | 11 | 22 | 3542 | 532642 | 92472 | 0.46 |
| migrate | 2 | 1 | 0 | 0 | 745 | 33 | 11 | 22 | 3372 | 530335 | 93115 | 0.46 |
| contract-a | 2 | 1 | 0 | 0 | 196 | 49 | 14 | 28 | 5793 | 724517 | 100372 | 0.53 |
| red | 1 | 0 | 0 | 0 | 22 | 16 | 4 | 8 | 2015 | 189795 | 50084 | 0.24 |
| pin | 1 | 1 | 0 | 0 | 16 | 11 | 4 | 8 | 1211 | 175463 | 47473 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 548 | 132 | 36 | 72 | 12322 | 1716428 | 318973 | 1.57 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 1109 | 159 | 41 | 82 | 19818 | 2246956 | 311205 | 1.67 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 193 | 0.46 |
| migrate | 0 | 0.00 | 745 | 0.46 |
| contract-a | 0 | 0.00 | 196 | 0.53 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Test-only step, changing no production file and green against today's code: the tests that pin status.sh's argv or replace it with a stub (tests/py/test_dashboard.py, and tests/dashboard.test.sh's case "/api/events answers while an /api/runs request is still blocked inside status.sh") assert instead that /api/runs answers the document status renders for a run fabricated under the main tree, with git the only faked boundary; the blocked-request case holds /api/runs inside a process status itself starts; a reverted probe deleting dashboard.py:44's call to status turns each rewritten case red; the commit lists only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 86 | 19 | 38 | 11320 | 1163224 | 118462 | 0.70 | 310 | n/a | n/a | n/a |  |  | full |
| dashboard's /api/runs calls a function of veri/status.py returning the JSON document in-process instead of starting status.sh, with status's diagnostics kept off the dashboard's stderr; dashboard gives its full answer — exit code, stdout, stderr, and the files and events status writes — in a case that refuses starting status.sh at the process boundary; the shim status.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 11 | 22 | 3542 | 532642 | 92472 | 0.46 | unknown | unknown | unknown | unknown |  |  | full |
| dashboard's /api/runs calls a function of veri/status.py returning the JSON document in-process instead of starting status.sh, with status's diagnostics kept off the dashboard's stderr; dashboard gives its full answer — exit code, stdout, stderr, and the files and events status writes — in a case that refuses starting status.sh at the process boundary; the shim status.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 11 | 22 | 3372 | 530335 | 93115 | 0.46 | unknown | unknown | unknown | unknown |  |  | full |
| dashboard's /api/runs calls a function of veri/status.py returning the JSON document in-process instead of starting status.sh, with status's diagnostics kept off the dashboard's stderr; dashboard gives its full answer — exit code, stdout, stderr, and the files and events status writes — in a case that refuses starting status.sh at the process boundary; the shim status.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 14 | 28 | 5793 | 724517 | 100372 | 0.53 | unknown | unknown | unknown | unknown |  |  | full |
| dashboard's /api/runs gives its full answer — exit code, stdout, stderr, and the files and events status writes — when starting status.sh as a process is refused at the process boundary, by calling status's function in-process (dashboard.py:44); the case that refuses that start is its own test, since the migrate phase freezes tests ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 3226 | 365258 | 97557 | 0.46 | unknown | unknown | unknown | unknown |  |  | pin |
| No test of dashboard fakes status.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 13 | 26 | 3978 | 635215 | 90425 | 0.47 | 221 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 60 | 65 | 67 | 65 | 62 | 68 | 69 |  |  |  |  |
| affected | 6 | 62 | 5 | 632 | 8 | 67 | 6 | 5 | 5 | 3 | 1 |
| target | 1 | 1 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 77 | 154 | 32140 | 3963384 | 630178 | 3.24 |
