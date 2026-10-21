### 📊 Metrics — issue 1775

Wall time for the issue: 2758 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1995.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.04 over 50 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 85220 |
| 2 | $0.03 | 86545 |
| 3 | $0.03 | 88516 |
| 4 | $0.02 | 88856 |
| 5 | $0.02 | 89272 |
| 6 | $0.02 | 89571 |
| 7 | $0.02 | 89940 |
| 8 | $0.02 | 90489 |
| 9 | $0.02 | 90971 |
| 10 | $0.02 | 91322 |
| 11 | $0.02 | 91978 |
| 12 | $0.03 | 92944 |
| 13 | $0.03 | 93940 |
| 14 | $0.04 | 96340 |
| 15 | $0.04 | 98618 |
| 16 | $0.03 | 99432 |
| 17 | $0.04 | 101406 |
| 18 | $0.03 | 102455 |
| 19 | $0.03 | 103034 |
| 20 | $0.03 | 104397 |
| 21 | $0.02 | 104904 |
| 22 | $0.09 | 112943 |
| 23 | $0.03 | 113345 |
| 24 | $0.03 | 113935 |
| 25 | $0.03 | 114349 |
| 26 | $0.03 | 115823 |
| 27 | $0.03 | 116277 |
| 28 | $0.03 | 117044 |
| 29 | $0.03 | 117435 |
| 30 | $0.03 | 117844 |
| 31 | $0.03 | 118222 |
| 32 | $0.03 | 119315 |
| 33 | $0.03 | 119770 |
| 34 | $0.03 | 120684 |
| 35 | $0.03 | 121716 |
| 36 | $0.04 | 124129 |
| 37 | $0.03 | 124593 |
| 38 | $0.03 | 125505 |
| 39 | $0.03 | 126277 |
| 40 | $0.03 | 126848 |
| 41 | $0.03 | 127327 |
| 42 | $0.03 | 127946 |
| 43 | $0.03 | 129093 |
| 44 | $0.05 | 131525 |
| 45 | $0.03 | 132308 |
| 46 | $0.03 | 132556 |
| 47 | $0.03 | 132930 |
| 48 | $0.03 | 133376 |
| 49 | $0.03 | 133748 |
| 50 | $0.03 | 134291 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1007 | 17463 | 12867 | 0.04 |
| red | 5 | 1 | 0 | 0 | 217 | 146 | 31 | 62 | 11643 | 971738 | 90312 | 0.44 |
| green | 2 | 1 | 0 | 0 | 119 | 42 | 13 | 24 | 3068 | 346445 | 29893 | 0.14 |
| refactor | 2 | 1 | 0 | 0 | 45 | 14 | 5 | 10 | 780 | 122739 | 24051 | 0.08 |
| pin | 3 | 3 | 0 | 0 | 65 | 43 | 13 | 26 | 3924 | 343373 | 40218 | 0.17 |
| diff | 2 | 1 | 0 | 0 | 528 | 51 | 13 | 26 | 4297 | 366430 | 49348 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 234 | 97 | 28 | 54 | 8381 | 693587 | 108100 | 0.42 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 752 | 208 | 48 | 96 | 16338 | 1474601 | 138589 | 0.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On a step whose ledger line carries `⟦guard-subject: <path>⟧` naming a test file (a guard suite or a sourced test helper such as `skills/tdd/scripts/tests/lib/harness.sh`), an edit to that file made after `tests-frozen.sh record --step` passes `tests-frozen.sh check --step` (exit 0) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 105 | 31 | 60 | 7951 | 896005 | 91230 | 0.40 | 332 | unknown | 0/5 | nothing-left |  |  | full |
| On a step whose ledger line carries two `⟦guard-subject: <path>⟧` markers, edits to both named files pass `tests-frozen.sh check --step` (exit 0) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 10 | 20 | 3695 | 280097 | 29891 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| On a `⟦guard-subject: <path>⟧` step, an edit to an unrecorded test file other than the named path still makes `tests-frozen.sh check --step` exit 1, printing that file's path ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 61 | 10 | 20 | 3998 | 285868 | 31693 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| On a `⟦guard-subject: <path>⟧` step, an edit to the test file Red wrote, which `record --step` recorded, still makes `tests-frozen.sh check --step` exit 1, printing that file's path, even when the edit to the named guard-subject file is also present ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 22 | 3771 | 322325 | 31660 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's Scope & plan section states when to mark a step `⟦guard-subject: <path>⟧` (its criterion is about behaviour living in a guard suite or a sourced test helper, so Green must edit that file), that the case pinning the behaviour stays frozen, and SCRIPTS.md's and tests-frozen.sh's own description of `check --step` name the exemption ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 13 | 26 | 4297 | 366430 | 49348 | 0.20 | 575 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| On a step whose ledger line carries `⟦guard-subject: <path>⟧` naming a test file (a guard suite or a sourced test helper such as `skills/tdd/scripts/tests/lib/harness.sh`), an edit to that file made after `tests-frozen.sh record --step` passes `tests-frozen.sh check --step` (exit 0) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 45 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 7 | 7 | 0 | 7 | 9 | 7 | 8 | 7 | 0 | 384 |
| fast | 21 | 19 | 19 | 18 | 18 |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 2 | 1 | 2 | 2 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 76 | 150 | 24719 | 2168188 | 246689 | 1.08 |
