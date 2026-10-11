### 📊 Metrics — issue 1355

Wall time for the issue: 2578 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1480.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 824 | 12489 | 32629 | 0.14 |
| diff | 4 | 2 | 0 | 0 | 509 | 167 | 45 | 84 | 22078 | 2469288 | 210739 | 1.31 |
| expand | 2 | 1 | 0 | 0 | 679 | 42 | 14 | 28 | 5236 | 651962 | 84511 | 0.46 |
| migrate | 2 | 1 | 0 | 0 | 235 | 33 | 12 | 24 | 4274 | 541705 | 83867 | 0.43 |
| contract-a | 2 | 1 | 0 | 0 | 110 | 32 | 12 | 24 | 3941 | 555440 | 88086 | 0.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 526 | 101 | 35 | 68 | 11834 | 1518069 | 243456 | 1.24 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 1015 | 179 | 49 | 94 | 24519 | 2712815 | 256376 | 1.54 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 679 | 0.46 |
| migrate | 0 | 0.00 | 235 | 0.43 |
| contract-a | 0 | 0.00 | 110 | 0.45 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, the tests in test_supervise.py and test_verify.py that pin preserve-attempt.sh's path, argv or exit status assert the preserved attempt instead — the refs/veri/attempts/<issue>/<step>/<phase>-<attempt> ref written through git (faked at git, or real in a @pytest.mark.process case), no such ref where nothing is preserved, and a failed preservation driven by git update-ref failing — green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 127 | 29 | 54 | 17392 | 1774620 | 126541 | 0.86 | 323 | n/a | n/a | n/a |  |  | full |
| Each of supervise and verify gives its full answer — exit code, stdout, stderr, and the ref and leaf files preserve-attempt writes — when starting preserve-attempt.sh as a process would fail, in a case that refuses that start at the process boundary ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 14 | 28 | 5236 | 651962 | 84511 | 0.46 | unknown | unknown | unknown | unknown |  |  | full |
| Each of supervise and verify gives its full answer — exit code, stdout, stderr, and the ref and leaf files preserve-attempt writes — when starting preserve-attempt.sh as a process would fail, in a case that refuses that start at the process boundary ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 12 | 24 | 4274 | 541705 | 83867 | 0.43 | unknown | unknown | unknown | unknown |  |  | full |
| Each of supervise and verify gives its full answer — exit code, stdout, stderr, and the ref and leaf files preserve-attempt writes — when starting preserve-attempt.sh as a process would fail, in a case that refuses that start at the process boundary ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 12 | 24 | 3941 | 555440 | 88086 | 0.45 | unknown | unknown | unknown | unknown |  |  | full |
| No test of supervise or verify fakes preserve-attempt.sh at the process boundary any longer, each such test rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 16 | 30 | 4686 | 694668 | 84198 | 0.45 | 245 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 25 | 26 | 26 | 25 | 25 | 26 | 25 |  |  |  |  |
| affected | 19 | 14 | 6 | 300 | 303 | 4 | 26 | 107 | 26 | 21 | 18 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 84 | 162 | 36353 | 4230884 | 499832 | 2.79 |
