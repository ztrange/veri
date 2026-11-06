### 📊 Metrics — issue 3052

Wall time for the issue: 2606 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3119.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.28 over 80 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 91076 tokens, largest 158601 tokens
Conductor context: first turn 91076 tokens, largest 119351 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 91076 |
| 2 | $0.09 | 98584 |
| 3 | $0.03 | 99740 |
| 4 | $0.05 | 101443 |
| 5 | $0.04 | 103508 |
| 6 | $0.04 | 104263 |
| 7 | $0.03 | 104631 |
| 8 | $0.04 | 104998 |
| 9 | $0.03 | 105766 |
| 10 | $0.05 | 107201 |
| 11 | $0.04 | 108616 |
| 12 | $0.07 | 113427 |
| 13 | $0.03 | 113967 |
| 14 | $0.04 | 114651 |
| 15 | $0.04 | 115116 |
| 16 | $0.04 | 115988 |
| 17 | $0.04 | 116549 |
| 18 | $0.03 | 117253 |
| 19 | $0.04 | 117692 |
| 20 | $0.05 | 119130 |
| 21 | $0.03 | 119861 |
| 22 | $0.05 | 120891 |
| 23 | $0.05 | 123960 |
| 24 | $0.04 | 124670 |
| 25 | $0.04 | 125001 |
| 26 | $0.04 | 125831 |
| 27 | $0.04 | 126677 |
| 28 | $0.05 | 127635 |
| 29 | $0.03 | 127954 |
| 30 | $0.05 | 128693 |
| 31 | $0.04 | 129726 |
| 32 | $0.04 | 130869 |
| 33 | $0.05 | 131973 |
| 34 | $0.04 | 132474 |
| 35 | $0.04 | 132957 |
| 36 | $0.04 | 133658 |
| 37 | $0.04 | 134009 |
| 38 | $0.05 | 135598 |
| 39 | $0.04 | 136759 |
| 40 | $0.05 | 137915 |
| 41 | $0.04 | 138581 |
| 42 | $0.04 | 138936 |
| 43 | $0.10 | 147017 |
| 44 | $0.05 | 148244 |
| 45 | $0.05 | 148729 |
| 46 | $0.04 | 149054 |
| 47 | $0.05 | 150159 |
| 48 | $0.05 | 152324 |
| 49 | $0.08 | 156930 |
| 50 | $0.05 | 157724 |
| 51 | $0.05 | 158601 |
| 52 | $0.59 | 91076 |
| 53 | $0.08 | 98582 |
| 54 | $0.03 | 99718 |
| 55 | $0.03 | 101580 |
| 56 | $0.04 | 104108 |
| 57 | $0.03 | 104777 |
| 58 | $0.02 | 105222 |
| 59 | $0.02 | 105474 |
| 60 | $0.02 | 105845 |
| 61 | $0.02 | 106174 |
| 62 | $0.03 | 107214 |
| 63 | $0.03 | 107793 |
| 64 | $0.03 | 108404 |
| 65 | $0.02 | 108766 |
| 66 | $0.03 | 109457 |
| 67 | $0.05 | 113491 |
| 68 | $0.03 | 114633 |
| 69 | $0.03 | 115283 |
| 70 | $0.03 | 115618 |
| 71 | $0.03 | 115965 |
| 72 | $0.03 | 116262 |
| 73 | $0.03 | 117051 |
| 74 | $0.03 | 117292 |
| 75 | $0.03 | 117567 |
| 76 | $0.03 | 118204 |
| 77 | $0.03 | 118579 |
| 78 | $0.03 | 118857 |
| 79 | $0.03 | 119351 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 781 | 0 | 31416 | 0.09 |
| red | 5 | 1 | 0 | 0 | 371 | 176 | 38 | 74 | 18301 | 1354861 | 172704 | 0.92 |
| pin | 2 | 1 | 1 | 0 | 124 | 72 | 17 | 34 | 5916 | 503115 | 53358 | 0.24 |
| green | 2 | 1 | 0 | 0 | 328 | 34 | 12 | 24 | 2589 | 352916 | 31869 | 0.14 |
| refactor | 1 | 0 | 0 | 0 | 5 | 3 | 2 | 4 | 160 | 48220 | 13400 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 4 | 1 | 0 | 376 | 107 | 26 | 52 | 8372 | 723714 | 115847 | 0.45 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 285 | 85 | 23 | 46 | 9460 | 759204 | 105152 | 0.43 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 179 | 102 | 21 | 40 | 9915 | 776194 | 81748 | 0.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 179 | 0.55 |
| pin | 0 | 0.00 | 71 | 0.15 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a `⟦diff-checked⟧` step makes an earlier step's frozen case call a new helper (a medium case, real git repo, in skills/tdd/scripts/tests/py/test_tests_frozen_process.py), `tests-frozen.sh rerecord-earlier` rewrites that case's record so its `body:` and `helpers:` lines both match HEAD, and `tests-frozen.sh check-earlier` then exits 0 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 14 | 28 | 7448 | 462182 | 66835 | 0.29 | unknown | unknown | unknown | unknown |  |  | pin |
| A record rewritten by `tests-frozen.sh rerecord-earlier` for an earlier case that calls no helper at HEAD carries no `helpers:` line for that case afterwards (a medium case, real git repo, in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 75 | 24 | 48 | 6511 | 728540 | 87240 | 0.36 | 788 | unknown | 0/5 | nothing-left |  |  | full |
| `tests-frozen.sh check-earlier` still exits 1 and names an earlier frozen case on stdout when only the assertion lines of a helper that case calls changed and no re-record was made (a medium case, real git repo, in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 3⟧ | 3 | 0 | 1 | 0 | 0 | 0 | 141 | 31 | 60 | 13007 | 1068390 | 117256 | 0.70 | unknown | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A record rewritten by `tests-frozen.sh rerecord-earlier` for an earlier case that calls no helper at HEAD carries no `helpers:` line for that case afterwards (a medium case, real git repo, in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 50 | 7 | 5 | 46 | 45 | 58 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 7 | 5 | 5 | 5 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 5 | 5 | 5 | 5 | 6 | 7 | 8 | 6 | 6 | 6 | 5 | 5 | 5 | 5 | 4 | 4 | 5 | 5 | 3 | 5 | 5 | 5 | 5 | 6 | 6 | 6 | 5 | 6 |
| fast | 38 | 40 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 70 | 138 | 27747 | 2259112 | 302747 | 5.71 (estimate) |
