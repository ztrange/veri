### 📊 Metrics — issue 3289

Wall time for the issue: 199 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 15 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.15 over 109 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78727 tokens, largest 166922 tokens
Conductor context: first turn 77040 tokens, largest 117927 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78727 |
| 2 | $0.07 | 84517 |
| 3 | $0.04 | 86153 |
| 4 | $0.03 | 87714 |
| 5 | $0.03 | 88037 |
| 6 | $0.03 | 88714 |
| 7 | $0.03 | 88876 |
| 8 | $0.03 | 89033 |
| 9 | $0.03 | 89534 |
| 10 | $0.03 | 89824 |
| 11 | $0.03 | 90352 |
| 12 | $0.03 | 90987 |
| 13 | $0.04 | 92448 |
| 14 | $0.05 | 95597 |
| 15 | $0.05 | 97670 |
| 16 | $0.03 | 98580 |
| 17 | $0.05 | 101618 |
| 18 | $0.06 | 105061 |
| 19 | $0.04 | 106514 |
| 20 | $0.04 | 108383 |
| 21 | $0.04 | 109280 |
| 22 | $0.04 | 109687 |
| 23 | $0.03 | 110269 |
| 24 | $0.04 | 110835 |
| 25 | $0.03 | 111332 |
| 26 | $0.04 | 112105 |
| 27 | $0.04 | 113359 |
| 28 | $0.04 | 114201 |
| 29 | $0.03 | 114487 |
| 30 | $0.04 | 115224 |
| 31 | $0.03 | 115702 |
| 32 | $0.04 | 116277 |
| 33 | $0.04 | 117084 |
| 34 | $0.04 | 118435 |
| 35 | $0.04 | 119125 |
| 36 | $0.09 | 127346 |
| 37 | $0.05 | 128568 |
| 38 | $0.04 | 129124 |
| 39 | $0.03 | 129597 |
| 40 | $0.04 | 129950 |
| 41 | $0.04 | 130516 |
| 42 | $0.04 | 131664 |
| 43 | $0.04 | 132086 |
| 44 | $0.04 | 132428 |
| 45 | $0.04 | 133235 |
| 46 | $0.04 | 134024 |
| 47 | $0.06 | 137330 |
| 48 | $0.04 | 137819 |
| 49 | $0.04 | 138008 |
| 50 | $0.04 | 138386 |
| 51 | $0.04 | 139379 |
| 52 | $0.04 | 139837 |
| 53 | $0.05 | 140324 |
| 54 | $0.04 | 141322 |
| 55 | $0.04 | 141697 |
| 56 | $0.04 | 142160 |
| 57 | $0.05 | 143297 |
| 58 | $0.04 | 144019 |
| 59 | $0.04 | 144506 |
| 60 | $0.04 | 144709 |
| 61 | $0.04 | 145252 |
| 62 | $0.05 | 146359 |
| 63 | $0.16 | 161480 |
| 64 | $0.04 | 161754 |
| 65 | $0.04 | 161988 |
| 66 | $0.05 | 162533 |
| 67 | $0.04 | 162730 |
| 68 | $0.04 | 162913 |
| 69 | $0.04 | 163127 |
| 70 | $0.05 | 163442 |
| 71 | $0.04 | 163717 |
| 72 | $0.04 | 164039 |
| 73 | $0.05 | 164267 |
| 74 | $0.05 | 165184 |
| 75 | $0.05 | 166238 |
| 76 | $0.04 | 166922 |
| 77 | $0.48 | 77040 |
| 78 | $0.06 | 82972 |
| 79 | $0.03 | 84846 |
| 80 | $0.02 | 85803 |
| 81 | $0.04 | 88683 |
| 82 | $0.02 | 89159 |
| 83 | $0.02 | 89540 |
| 84 | $0.02 | 89968 |
| 85 | $0.02 | 90278 |
| 86 | $0.02 | 90718 |
| 87 | $0.02 | 91292 |
| 88 | $0.02 | 91634 |
| 89 | $0.03 | 92492 |
| 90 | $0.05 | 96803 |
| 91 | $0.02 | 97330 |
| 92 | $0.02 | 97989 |
| 93 | $0.02 | 98421 |
| 94 | $0.02 | 98695 |
| 95 | $0.02 | 98971 |
| 96 | $0.02 | 99362 |
| 97 | $0.02 | 99728 |
| 98 | $0.05 | 103046 |
| 99 | $0.03 | 104358 |
| 100 | $0.03 | 105991 |
| 101 | $0.03 | 106693 |
| 102 | $0.03 | 108353 |
| 103 | $0.03 | 108838 |
| 104 | $0.03 | 109450 |
| 105 | $0.03 | 110028 |
| 106 | $0.03 | 110786 |
| 107 | $0.04 | 112406 |
| 108 | $0.03 | 113261 |
| 109 | $0.06 | 117927 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 2 | 840 | $0.02 |
| ✅ Done | 1 | 420 | $0.01 |
| 🔴 Red | 1 | 420 | $0.01 |
| 🟢 Green | 1 | 420 | $0.01 |
| 🛠️ Refactor | 1 | 420 | $0.01 |
| 🔎 verify-green | 1 | 420 | $0.01 |
| 🔎 verify-refactor | 1 | 420 | $0.01 |
| 🔎 verify-<phase> (revised) | 1 | 420 | $0.01 |
| 🗺️ Plan | 2 | 440 | $0.01 |
| 🗺️ verify-plan | 3 | 460 | $0.01 |
| ▶️ Resuming | 1 | 2 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 11 | 3402 | $0.07 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 5 | 1 | 3 | 0 | 69 | 61 | 11 | 22 | 7796 | 167633 | 72236 | 0.28 |
| red | 5 | 1 | 0 | 0 | 137 | 87 | 30 | 58 | 11488 | 552085 | 106242 | 0.44 |
| green | 4 | 1 | 1 | 0 | 460 | 84 | 25 | 48 | 8952 | 457208 | 65476 | 0.38 |
| refactor | 1 | 0 | 0 | 0 | 5 | 3 | 2 | 4 | 257 | 22937 | 13990 | 0.04 |
| pin | 3 | 3 | 0 | 0 | 66 | 44 | 15 | 30 | 4525 | 233455 | 43443 | 0.18 |
| diff | 2 | 1 | 0 | 0 | 62 | 20 | 9 | 18 | 1939 | 129244 | 24453 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 7 | 4 | 0 | 517 | 164 | 46 | 90 | 18750 | 717853 | 163598 | 0.67 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 137 | 88 | 31 | 62 | 11563 | 567118 | 117092 | 0.47 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 145 | 47 | 15 | 28 | 4644 | 277591 | 45150 | 0.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 460 | 0.38 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Retiring a step with `tick-ledger.sh --unpinnable` removes from the ledger's `.tdd/issue-<n>-mutations.md` a mutation record whose command's `TESTS=` names a test case that does not exist in the tree (the case's function absent from its test file); a case pins it ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 116 | 39 | 74 | 12623 | 671296 | 123222 | 0.59 | 645 | 1/2 | 0/5 | nothing-left |  |  | full |
| Retiring a step with `tick-ledger.sh --already-holds` likewise removes from the ledger's `.tdd/issue-<n>-mutations.md` a mutation record whose command's `TESTS=` names a test case that does not exist in the tree; a case pins it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 3460 | 173225 | 34149 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| Retiring a step with `tick-ledger.sh --unpinnable` keeps in the ledger's `.tdd/issue-<n>-mutations.md` a mutation record whose command's `TESTS=` names a test case that does exist in the tree; a case pins it ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 12 | 24 | 4332 | 207608 | 34111 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| After a step is retired with `tick-ledger.sh --unpinnable`, `pin-recheck.sh` run on a range touching the record's mutated file no longer prints "base run failed" for the record dropped by the retire; a case pins it (a process case is allowed, since pin-recheck runs git) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 22 | 4807 | 213556 | 37669 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| `.tdd/issue-3235-mutations.md` no longer holds the record pinning `test_a_run_with_no_refactor_event_and_no_structural_pass_event_prints_no_refactor_totals_section` (`grep -c` of that name on the file prints 0), every other record of that file left byte-for-byte as it was, and the deletion committed so the tree matches HEAD after the leaf exits; no production or test change ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 20 | 9 | 18 | 1939 | 129244 | 24453 | 0.09 | 103 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Retiring a step with `tick-ledger.sh --unpinnable` removes from the ledger's `.tdd/issue-<n>-mutations.md` a mutation record whose command's `TESTS=` names a test case that does not exist in the tree (the case's function absent from its test file); a case pins it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| Retiring a step with `tick-ledger.sh --unpinnable` removes from the ledger's `.tdd/issue-<n>-mutations.md` a mutation record whose command's `TESTS=` names a test case that does not exist in the tree (the case's function absent from its test file); a case pins it ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 2 | ? | ? | nothing-left 1, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 3 | 7 | 2 | 3 | 2 | 2 | 5 |
| fast | 20 | 21 | 24 | 39 | 21 | 20 | 19 | 19 |  |
| target | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 92 | 180 | 34957 | 1562562 | 325840 | 6.56 (estimate) |
