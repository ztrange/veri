### 📊 Metrics — issue 1634

Wall time for the issue: 5710 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1642.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 37 | 31 | 2 | 4 | 3070 | 24386 | 81731 | 0.36 |
| red | 5 | 2 | 0 | 0 | 163 | 137 | 33 | 66 | 13891 | 1758628 | 267100 | 1.38 |
| green | 4 | 2 | 0 | 0 | 280 | 123 | 26 | 48 | 10018 | 1268991 | 199308 | 1.02 |
| refactor | 4 | 2 | 0 | 0 | 166 | 78 | 20 | 40 | 6569 | 978259 | 189634 | 0.92 |
| diff | 6 | 3 | 0 | 0 | 3229 | 299 | 75 | 146 | 27458 | 4543649 | 307114 | 2.22 |
| pin | 1 | 1 | 0 | 0 | 23 | 17 | 6 | 12 | 1830 | 289749 | 45544 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 11 | 1 | 0 | 1766 | 283 | 60 | 118 | 22742 | 2896621 | 519500 | 2.86 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 2132 | 402 | 102 | 198 | 40094 | 5967041 | 570931 | 3.28 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The unit-tier admission guard fails when a planted suite under tests/unit/ runs a script under skills/tdd/scripts/ as a subprocess rather than sourcing it and mocking what it shells out to, naming that suite as `<suite>:<line>` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 143 | 31 | 62 | 15097 | 1633695 | 316140 | 1.58 | 398 | unknown | 2/5 | nothing-structural |  |  | full |
| The unit-tier admission guard lets a planted subprocess-running `<suite>:<line>` through only when its exemption-table entry carries a reason, and fails naming the entry when the reason is empty ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 38 | 72 | 11693 | 1820588 | 288422 | 1.45 | 387 | unknown | 1/5 | nothing-structural |  |  | full |
| missing-argument-exit.test.sh moves from skills/tdd/scripts/tests/unit/ to skills/tdd/scripts/tests/, where `make test` still runs it with the same case count, and CLAUDE.md's unit-tier suite counts say so ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 21 | 38 | 6329 | 1039337 | 101061 | 0.57 | 327 | n/a | n/a | n/a |  |  | full |
| scratch-copy-libs.test.sh moves from skills/tdd/scripts/tests/unit/ to skills/tdd/scripts/tests/, where `make test` still runs it with the same case count, and CLAUDE.md's unit-tier suite counts say so ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 102 | 20 | 42 | 5849 | 1230847 | 63971 | 0.70 | 1696 | n/a | n/a | n/a |  |  | full |
| Every other suite under skills/tdd/scripts/tests/unit/ that the admission guard names either meets the bar (sources the script and mocks what it shells out to) or moves to skills/tdd/scripts/tests/ with the same case count under `make test`, and CLAUDE.md's unit-tier counts and admission-bar sentence say so; with none named, nothing changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 134 | 34 | 66 | 15280 | 2273465 | 142082 | 0.95 | 1329 | n/a | n/a | n/a |  |  | full |
| The unit-tier admission guard passes over the real skills/tdd/scripts/tests/unit/, naming no offender — a regression pin: by this step the moves above have landed, so its Red reports the case passing against the code and it is pinned through verify-pin's mutation ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 16 | 32 | 5518 | 841344 | 97024 | 0.53 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The unit-tier admission guard fails when a planted suite under tests/unit/ runs a script under skills/tdd/scripts/ as a subprocess rather than sourcing it and mocking what it shells out to, naming that suite as `<suite>:<line>` ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 78 | 0.45 |
| The unit-tier admission guard lets a planted subprocess-running `<suite>:<line>` through only when its exemption-table entry carries a reason, and fails naming the entry when the reason is empty ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 88 | 0.47 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 118 | 295 | 543 | 542 | 1 |
| fast | 35 | 33 | 32 | 32 | 32 | 33 | 23 | 23 | 24 | 17 | 17 | 7 | 6 |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 162 | 316 | 62836 | 8863662 | 1090431 | 6.14 |
