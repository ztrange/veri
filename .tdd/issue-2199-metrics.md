### 📊 Metrics — issue 2199

Wall time for the issue: 3275 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2256.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.04 over 85 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89183 |
| 2 | $0.03 | 90296 |
| 3 | $0.03 | 92198 |
| 4 | $0.02 | 92468 |
| 5 | $0.02 | 92836 |
| 6 | $0.02 | 93401 |
| 7 | $0.02 | 93959 |
| 8 | $0.02 | 94526 |
| 9 | $0.03 | 95561 |
| 10 | $0.05 | 99665 |
| 11 | $0.11 | 110338 |
| 12 | $0.04 | 112644 |
| 13 | $0.07 | 118371 |
| 14 | $0.06 | 123433 |
| 15 | $0.05 | 125999 |
| 16 | $0.03 | 126868 |
| 17 | $0.04 | 128172 |
| 18 | $0.04 | 130465 |
| 19 | $0.05 | 133724 |
| 20 | $0.03 | 134144 |
| 21 | $0.03 | 134835 |
| 22 | $0.03 | 135630 |
| 23 | $0.03 | 135872 |
| 24 | $0.03 | 136826 |
| 25 | $0.04 | 138067 |
| 26 | $0.03 | 138375 |
| 27 | $0.03 | 139099 |
| 28 | $0.04 | 140151 |
| 29 | $0.04 | 141433 |
| 30 | $0.04 | 142287 |
| 31 | $0.04 | 143207 |
| 32 | $0.03 | 143952 |
| 33 | $0.04 | 144884 |
| 34 | $0.03 | 145483 |
| 35 | $0.04 | 146444 |
| 36 | $0.03 | 147034 |
| 37 | $0.04 | 147944 |
| 38 | $0.04 | 149242 |
| 39 | $0.04 | 150352 |
| 40 | $0.04 | 151947 |
| 41 | $0.05 | 153908 |
| 42 | $0.04 | 155601 |
| 43 | $0.04 | 156768 |
| 44 | $0.04 | 157897 |
| 45 | $0.04 | 159118 |
| 46 | $0.04 | 160196 |
| 47 | $0.05 | 162307 |
| 48 | $0.04 | 163389 |
| 49 | $0.05 | 165166 |
| 50 | $0.04 | 166081 |
| 51 | $0.04 | 167248 |
| 52 | $0.04 | 168472 |
| 53 | $0.04 | 169574 |
| 54 | $0.05 | 171467 |
| 55 | $0.04 | 172367 |
| 56 | $0.05 | 173992 |
| 57 | $0.04 | 174915 |
| 58 | $0.05 | 177123 |
| 59 | $0.05 | 179555 |
| 60 | $0.04 | 180560 |
| 61 | $0.04 | 180870 |
| 62 | $0.04 | 181640 |
| 63 | $0.04 | 182147 |
| 64 | $0.04 | 182473 |
| 65 | $0.04 | 183242 |
| 66 | $0.04 | 183788 |
| 67 | $0.04 | 184791 |
| 68 | $0.04 | 185041 |
| 69 | $0.04 | 185392 |
| 70 | $0.04 | 185779 |
| 71 | $0.05 | 186784 |
| 72 | $0.04 | 187191 |
| 73 | $0.04 | 187725 |
| 74 | $0.04 | 188648 |
| 75 | $0.05 | 189591 |
| 76 | $0.04 | 190090 |
| 77 | $0.04 | 190824 |
| 78 | $0.04 | 191401 |
| 79 | $0.04 | 192013 |
| 80 | $0.05 | 193278 |
| 81 | $0.04 | 194049 |
| 82 | $0.05 | 195024 |
| 83 | $0.04 | 195650 |
| 84 | $0.04 | 196245 |
| 85 | $0.05 | 196980 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 1 | 2 | 1482 | 0 | 31085 | 0.09 |
| red | 9 | 4 | 0 | 0 | 385 | 189 | 46 | 90 | 21162 | 1407454 | 207470 | 0.87 |
| green | 8 | 4 | 0 | 0 | 643 | 134 | 42 | 84 | 13707 | 1245841 | 134653 | 0.60 |
| refactor | 8 | 4 | 0 | 0 | 236 | 68 | 24 | 48 | 5131 | 617784 | 107625 | 0.38 |
| pin | 1 | 1 | 0 | 0 | 42 | 16 | 4 | 8 | 1446 | 105967 | 14203 | 0.06 |
| cover | 3 | 0 | 0 | 0 | 115 | 48 | 15 | 30 | 5210 | 403971 | 65007 | 0.26 |
| predicate | 2 | 0 | 0 | 0 | 26 | 19 | 7 | 14 | 1711 | 179065 | 24141 | 0.10 |
| structural | 2 | 0 | 0 | 0 | 73 | 23 | 10 | 20 | 2459 | 270627 | 26203 | 0.12 |
| transform | 2 | 2 | 0 | 0 | 54 | 17 | 7 | 14 | 1454 | 158875 | 41929 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 16 | 0 | 0 | 753 | 178 | 52 | 104 | 16330 | 1306243 | 255663 | 0.93 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 837 | 348 | 104 | 206 | 37432 | 3083341 | 396653 | 1.67 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tests-frozen.sh record --step <s> <test-file>` run again for a step whose record already holds a `body:` entry for a case, when that case is committed at HEAD unchanged, keeps that case's `body:` entry with its digest at the current content, instead of writing a file-only record with no case (a git repo in tmp_path: a medium case marked process) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 91 | 29 | 56 | 8770 | 822960 | 121831 | 0.47 | 495 | unknown | 1/5 | nothing-left |  |  | full |
| `tests-frozen.sh rerecord-earlier <ledger> --step <s>`, for a step `<s>` marked `⟦diff-checked⟧`, rewrites each earlier step's record entry whose case's content changed at the case's current content and exits 0, so that a later step's `tests-frozen.sh check-earlier` exits 0 and names nothing for that case (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 25 | 50 | 9075 | 727920 | 100755 | 0.42 | 349 | unknown | 0/5 | structural-owed |  |  | full |
| `tick-ledger.sh` ticking a step marked `⟦diff-checked⟧` re-records, as `rerecord-earlier` does, every earlier step's frozen case that step changed, so after the ⟦diff-checked⟧ step's tick a later step's `tests-frozen.sh check-earlier` exits 0 for the edited case, with no extra conductor command (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 27 | 54 | 8372 | 771354 | 98426 | 0.41 | 371 | unknown | 0/5 | structural-owed |  |  | full |
| A frozen case changed by a step not marked `⟦diff-checked⟧` still trips `check-earlier`: `tick-ledger.sh` ticking such a step, and `tests-frozen.sh rerecord-earlier` given such a step (exit 3, nothing to do), leave every earlier record unchanged, and a later step's `check-earlier` exits 1 naming the case and its owning step (a git repo in tmp_path: a medium case marked process) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 23 | 46 | 8117 | 641060 | 94790 | 0.38 | 392 | unknown | 0/5 | structural-owed |  |  | full |
| The fresh record the ⟦diff-checked⟧ tick writes is computed by the `tests_frozen` beside the `tick-ledger.sh` that ran (the run's pinned skill snapshot), never by a `tests_frozen` in the working tree: with two copies of the scripts directory whose `tests_frozen` digest a case differently, the tick and `check-earlier` run from the snapshot copy pass for the re-recorded case though the checkout copy would digest it otherwise (a medium case marked process) ⟦criterion 4⟧ | 11 | 3 | 0 | 0 | 0 | 0 | 166 | 51 | 102 | 17946 | 1426290 | 205429 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tests-frozen.sh record --step <s> <test-file>` run again for a step whose record already holds a `body:` entry for a case, when that case is committed at HEAD unchanged, keeps that case's `body:` entry with its digest at the current content, instead of writing a file-only record with no case (a git repo in tmp_path: a medium case marked process) ⟦criterion 3⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 85 | 0.11 |
| `tests-frozen.sh rerecord-earlier <ledger> --step <s>`, for a step `<s>` marked `⟦diff-checked⟧`, rewrites each earlier step's record entry whose case's content changed at the case's current content and exits 0, so that a later step's `tests-frozen.sh check-earlier` exits 0 and names nothing for that case (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 53 | 0.10 |
| `tick-ledger.sh` ticking a step marked `⟦diff-checked⟧` re-records, as `rerecord-earlier` does, every earlier step's frozen case that step changed, so after the ⟦diff-checked⟧ step's tick a later step's `tests-frozen.sh check-earlier` exits 0 for the edited case, with no extra conductor command (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 50 | 0.09 |
| A frozen case changed by a step not marked `⟦diff-checked⟧` still trips `check-earlier`: `tick-ledger.sh` ticking such a step, and `tests-frozen.sh rerecord-earlier` given such a step (exit 3, nothing to do), leave every earlier record unchanged, and a later step's `check-earlier` exits 1 naming the case and its owning step (a git repo in tmp_path: a medium case marked process) ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 48 | 0.09 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 12 | 14 | 14 | 30 | 20 | 18 | 13 | 13 | 14 | 15 | 13 | 9 | 9 | 10 | 24 | 10 | 19 | 16 | 13 | 16 | 12 | 10 | 11 | 13 | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 |
| fast | 15 | 25 | 17 | 16 | 18 | 14 | 14 | 15 | 15 | 15 | 20 | 14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 9 | 9 | 8 | 10 | 11 | 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 156 | 310 | 53762 | 4389584 | 652316 | 2.61 |
