### 📊 Metrics — issue 3292

Wall time for the issue: 263 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 15 planned.
Outcome: the run bailed — step-added-off-route, a process failure.
Lane: ready-for-agent:mu
Suite flakes: skills/tdd/scripts/tests/py/test_run_conductor_process.py.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $9.98 over 191 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78707 tokens, largest 166271 tokens
Conductor context: first turn 77023 tokens, largest 140413 tokens
Conductor context: first turn 76998 tokens, largest 144937 tokens
Conductor context: first turn 77012 tokens, largest 125479 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78707 |
| 2 | $0.07 | 84495 |
| 3 | $0.04 | 86384 |
| 4 | $0.04 | 87982 |
| 5 | $0.04 | 88577 |
| 6 | $0.03 | 88925 |
| 7 | $0.03 | 89256 |
| 8 | $0.03 | 89655 |
| 9 | $0.03 | 89944 |
| 10 | $0.03 | 90549 |
| 11 | $0.03 | 90918 |
| 12 | $0.05 | 92894 |
| 13 | $0.04 | 95277 |
| 14 | $0.04 | 96388 |
| 15 | $0.05 | 98672 |
| 16 | $0.04 | 100267 |
| 17 | $0.04 | 100740 |
| 18 | $0.03 | 101655 |
| 19 | $0.04 | 102150 |
| 20 | $0.03 | 102932 |
| 21 | $0.04 | 103442 |
| 22 | $0.11 | 113104 |
| 23 | $0.03 | 113764 |
| 24 | $0.04 | 114215 |
| 25 | $0.04 | 114847 |
| 26 | $0.04 | 115496 |
| 27 | $0.04 | 116417 |
| 28 | $0.04 | 117781 |
| 29 | $0.04 | 118068 |
| 30 | $0.04 | 118758 |
| 31 | $0.04 | 119429 |
| 32 | $0.04 | 120786 |
| 33 | $0.04 | 121650 |
| 34 | $0.04 | 122149 |
| 35 | $0.04 | 122785 |
| 36 | $0.04 | 123591 |
| 37 | $0.05 | 125095 |
| 38 | $0.04 | 125944 |
| 39 | $0.04 | 126361 |
| 40 | $0.05 | 128076 |
| 41 | $0.04 | 128985 |
| 42 | $0.05 | 130822 |
| 43 | $0.04 | 131776 |
| 44 | $0.05 | 132609 |
| 45 | $0.04 | 133608 |
| 46 | $0.04 | 134321 |
| 47 | $0.05 | 135170 |
| 48 | $0.04 | 135961 |
| 49 | $0.05 | 138054 |
| 50 | $0.07 | 141387 |
| 51 | $0.04 | 142096 |
| 52 | $0.05 | 143226 |
| 53 | $0.05 | 144353 |
| 54 | $0.04 | 145448 |
| 55 | $0.16 | 160539 |
| 56 | $0.05 | 160849 |
| 57 | $0.04 | 161135 |
| 58 | $0.05 | 161951 |
| 59 | $0.05 | 162375 |
| 60 | $0.04 | 162744 |
| 61 | $0.05 | 163034 |
| 62 | $0.04 | 163397 |
| 63 | $0.05 | 163673 |
| 64 | $0.05 | 164665 |
| 65 | $0.05 | 165638 |
| 66 | $0.05 | 166271 |
| 67 | $0.49 | 77023 |
| 68 | $0.07 | 83191 |
| 69 | $0.06 | 87092 |
| 70 | $0.04 | 88985 |
| 71 | $0.06 | 92036 |
| 72 | $0.06 | 96394 |
| 73 | $0.03 | 96905 |
| 74 | $0.04 | 97420 |
| 75 | $0.03 | 97799 |
| 76 | $0.03 | 98287 |
| 77 | $0.04 | 98787 |
| 78 | $0.03 | 99549 |
| 79 | $0.04 | 100486 |
| 80 | $0.04 | 101248 |
| 81 | $0.03 | 101662 |
| 82 | $0.04 | 102004 |
| 83 | $0.03 | 102823 |
| 84 | $0.04 | 103705 |
| 85 | $0.04 | 104529 |
| 86 | $0.04 | 105378 |
| 87 | $0.04 | 106772 |
| 88 | $0.04 | 107616 |
| 89 | $0.03 | 107987 |
| 90 | $0.04 | 108745 |
| 91 | $0.04 | 109414 |
| 92 | $0.04 | 110084 |
| 93 | $0.03 | 110729 |
| 94 | $0.04 | 111834 |
| 95 | $0.04 | 112207 |
| 96 | $0.04 | 113209 |
| 97 | $0.04 | 114027 |
| 98 | $0.04 | 114946 |
| 99 | $0.04 | 115818 |
| 100 | $0.06 | 119081 |
| 101 | $0.04 | 119994 |
| 102 | $0.04 | 120668 |
| 103 | $0.05 | 122183 |
| 104 | $0.04 | 123168 |
| 105 | $0.04 | 123786 |
| 106 | $0.05 | 124861 |
| 107 | $0.10 | 133735 |
| 108 | $0.08 | 138522 |
| 109 | $0.04 | 139319 |
| 110 | $0.05 | 140413 |
| 111 | $0.49 | 76998 |
| 112 | $0.07 | 82936 |
| 113 | $0.05 | 86826 |
| 114 | $0.05 | 88745 |
| 115 | $0.05 | 91818 |
| 116 | $0.03 | 92343 |
| 117 | $0.03 | 92853 |
| 118 | $0.03 | 93025 |
| 119 | $0.03 | 93189 |
| 120 | $0.03 | 93404 |
| 121 | $0.03 | 93685 |
| 122 | $0.03 | 94103 |
| 123 | $0.04 | 94801 |
| 124 | $0.03 | 95103 |
| 125 | $0.03 | 95703 |
| 126 | $0.07 | 100189 |
| 127 | $0.03 | 101086 |
| 128 | $0.04 | 101749 |
| 129 | $0.03 | 102160 |
| 130 | $0.03 | 102760 |
| 131 | $0.09 | 110221 |
| 132 | $0.05 | 112186 |
| 133 | $0.04 | 112868 |
| 134 | $0.06 | 116164 |
| 135 | $0.04 | 116884 |
| 136 | $0.04 | 118012 |
| 137 | $0.04 | 118853 |
| 138 | $0.03 | 119193 |
| 139 | $0.04 | 119924 |
| 140 | $0.04 | 120616 |
| 141 | $0.04 | 120931 |
| 142 | $0.04 | 121544 |
| 143 | $0.04 | 122738 |
| 144 | $0.04 | 123762 |
| 145 | $0.04 | 124550 |
| 146 | $0.04 | 125433 |
| 147 | $0.05 | 126420 |
| 148 | $0.05 | 128361 |
| 149 | $0.03 | 128827 |
| 150 | $0.05 | 129716 |
| 151 | $0.04 | 130415 |
| 152 | $0.05 | 131882 |
| 153 | $0.04 | 132753 |
| 154 | $0.04 | 133316 |
| 155 | $0.04 | 134582 |
| 156 | $0.05 | 135695 |
| 157 | $0.04 | 136399 |
| 158 | $0.04 | 136941 |
| 159 | $0.04 | 137557 |
| 160 | $0.04 | 137940 |
| 161 | $0.06 | 139831 |
| 162 | $0.04 | 140591 |
| 163 | $0.05 | 142625 |
| 164 | $0.05 | 143067 |
| 165 | $0.04 | 144184 |
| 166 | $0.05 | 144937 |
| 167 | $0.48 | 77012 |
| 168 | $0.06 | 82946 |
| 169 | $0.05 | 86810 |
| 170 | $0.03 | 88758 |
| 171 | $0.05 | 92898 |
| 172 | $0.02 | 93476 |
| 173 | $0.02 | 94126 |
| 174 | $0.02 | 94468 |
| 175 | $0.02 | 95028 |
| 176 | $0.02 | 95420 |
| 177 | $0.02 | 95832 |
| 178 | $0.03 | 96804 |
| 179 | $0.03 | 97677 |
| 180 | $0.05 | 101999 |
| 181 | $0.03 | 102683 |
| 182 | $0.03 | 103366 |
| 183 | $0.02 | 103864 |
| 184 | $0.04 | 106163 |
| 185 | $0.03 | 106876 |
| 186 | $0.10 | 117118 |
| 187 | $0.03 | 117810 |
| 188 | $0.03 | 118055 |
| 189 | $0.03 | 118700 |
| 190 | $0.04 | 120709 |
| 191 | $0.06 | 125479 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 4 | 1968 | $0.04 |
| ✅ Done | 1 | 499 | $0.01 |
| 🔴 Red | 4 | 1988 | $0.04 |
| 🟢 Green | 7 | 3449 | $0.07 |
| 🛠️ Refactor | 2 | 998 | $0.02 |
| 🔎 verify-green | 7 | 3449 | $0.07 |
| 🔎 verify-refactor | 2 | 998 | $0.02 |
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 1 | 499 | $0.01 |
| 🗺️ verify-plan | 6 | 2495 | $0.05 |
| ▶️ Resuming | 3 | 998 | $0.02 |
| ⛔ Bailed | 1 | 519 | $0.01 |
| ⏹️ Stopped | 1 | 471 | $0.01 |
| Total | 27 | 12415 | $0.25 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 6 | 4 | 2 | 0 | 93 | 77 | 12 | 24 | 9811 | 157787 | 132933 | 0.45 |
| diff | 4 | 2 | 0 | 0 | 149 | 36 | 15 | 30 | 3631 | 218393 | 67522 | 0.23 |
| red | 11 | 4 | 0 | 0 | 291 | 146 | 50 | 92 | 18696 | 939528 | 254114 | 0.92 |
| green | 14 | 3 | 4 | 0 | 1142 | 222 | 71 | 136 | 22826 | 1264579 | 242563 | 1.05 |
| refactor | 4 | 1 | 0 | 0 | 62 | 25 | 12 | 24 | 2522 | 173548 | 66494 | 0.21 |
| pin | 3 | 2 | 1 | 0 | 57 | 40 | 10 | 20 | 4581 | 151048 | 49023 | 0.18 |
| red-missing | 1 | 0 | 0 | 0 | 39 | 32 | 6 | 10 | 4232 | 104562 | 23009 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 23 | 16 | 7 | 0 | 1179 | 292 | 79 | 152 | 33038 | 1223545 | 397621 | 1.45 |
| developer | claude-sonnet-5-5 | 17 | 0 | 0 | 0 | 459 | 229 | 80 | 150 | 28659 | 1459116 | 377704 | 1.38 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 195 | 57 | 17 | 34 | 4602 | 326784 | 60333 | 0.32 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 76 | 0.13 |
| red | 0 | 0.00 | 188 | 0.58 |
| green | 0 | 0.00 | 900 | 0.79 |
| refactor | 0 | 0.00 | 5 | 0.06 |
| pin | 0 | 0.00 | 57 | 0.18 |
| red-missing | 0 | 0.00 | 39 | 0.11 |
| develop-red | 0 | 0.00 | 0 | 0.00 |
| develop-diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The case test_main_2878_prints_revise_and_exits_3_for_an_unparseable_wrong_test_once_the_step_log_holds_a_reroute_event is removed from skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py, its revise expectation being superseded by criterion 1; no other case and no production file changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 14 | 6 | 12 | 1466 | 71362 | 30491 | 0.10 | 174 | n/a | n/a | n/a |  |  | full |
| wrong-test-route.sh given a green report whose WRONG_TEST: line names no case, on a step whose events log already holds a reroute event (the free reroute spent), prints repair <the step's own case> and exits 0, not revise; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins the printed route ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 47 | 19 | 34 | 5362 | 338738 | 102765 | 0.34 | 353 | unknown | 0/5 | nothing-left |  |  | full |
| wrong-test-route.sh given a green report that says WRONG_TEST in prose without any WRONG_TEST: line and names no case prints repair <the step's own case> and exits 0, not revise; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 80 | 32 | 62 | 8992 | 557981 | 100464 | 0.40 | 447 | unknown | 1/5 | nothing-structural |  |  | full |
| wrong-test-route.sh given a green report whose WRONG_TEST: line body is none still prints revise and exits 3 on a step whose free reroute is already spent; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it ⟦criterion 3⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 39 | 11 | 20 | 5058 | 191349 | 37637 | 0.16 | unknown | unknown | unknown | unknown |  |  | full |
| wrong-test-route.sh given a green report whose WRONG_TEST names no case, on a step whose events log holds a first reroute event and, after it, a `kind=repair` reroute event (the one extra repair past the free reroute already spent), prints `repair-exhausted <the step's own case>` and exits 1, never `revise`, while with only the first reroute event it still prints `repair <the step's own case>`; no new budget knob and nothing read from `VERI_MISSING_REROUTE_BUDGET`; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it, red without the bound ⟦added⟧ ⟦criterion 1⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 114 | 36 | 68 | 14154 | 605697 | 178469 | 0.65 | unknown | unknown | unknown | unknown |  |  | already-satisfied |
| wrong-test-route.sh given a green report whose WRONG_TEST names no case, on a step whose events log holds a first reroute event and, after it, a `kind=repair` reroute event (the one extra repair past the free reroute already spent), prints `repair-exhausted <the step's own case>` and exits 1, never `revise`, while with only the first reroute event it still prints `repair <the step's own case>`; the green adds the bound WITHOUT a `case is None and` guard on the rerouted path (unreachable there: `rerouted` forces `case` to None and `older` to []; verify-green rejected it as an equivalent mutant) and leaves the live non-rerouted `case is None and` guard at wrong_test_route.py:300 alone, so no case need pin a guard; no new budget knob and nothing read from `VERI_MISSING_REROUTE_BUDGET`; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it, red without the bound ⟦added⟧ ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 185 | 51 | 98 | 19291 | 939500 | 215868 | 0.92 | unknown | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| the case test_main_1621_refuses_a_wrong_test_naming_no_case_only_its_own_red_or_a_missing_case_and_a_bad_argument_list in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py compares its nine bad-argument stderr results against the module's own `wrong_test_route.USAGE + "\n"` instead of a verbatim usage literal, so a later change to the usage text turns it no red; its name, its other assertions and every production file are unchanged ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 9 | 18 | 2165 | 147031 | 37031 | 0.13 | unknown | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| wrong-test-route.sh given a green report whose WRONG_TEST: line names no case, on a step whose events log already holds a reroute event (the free reroute spent), prints repair <the step's own case> and exits 0, not revise; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins the printed route ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| wrong-test-route.sh given a green report that says WRONG_TEST in prose without any WRONG_TEST: line and names no case prints repair <the step's own case> and exits 0, not revise; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 50 | 0.11 |
| wrong-test-route.sh given a green report whose WRONG_TEST names no case, on a step whose events log holds a first reroute event and, after it, a `kind=repair` reroute event (the one extra repair past the free reroute already spent), prints `repair-exhausted <the step's own case>` and exits 1, never `revise`, while with only the first reroute event it still prints `repair <the step's own case>`; the green adds the bound WITHOUT a `case is None and` guard on the rerouted path (unreachable there: `rerouted` forces `case` to None and `older` to []; verify-green rejected it as an equivalent mutant) and leaves the live non-rerouted `case is None and` guard at wrong_test_route.py:300 alone, so no case need pin a guard; no new budget knob and nothing read from `VERI_MISSING_REROUTE_BUDGET`; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it, red without the bound ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.06 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| wrong-test-route.sh given a green report whose WRONG_TEST: line names no case, on a step whose events log already holds a reroute event (the free reroute spent), prints repair <the step's own case> and exits 0, not revise; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins the printed route ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| wrong-test-route.sh given a green report that says WRONG_TEST in prose without any WRONG_TEST: line and names no case prints repair <the step's own case> and exits 0, not revise; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it ⟦criterion 2⟧ | 1 | 1 | 0 | nothing-structural 1 |
| wrong-test-route.sh given a green report whose WRONG_TEST names no case, on a step whose events log holds a first reroute event and, after it, a `kind=repair` reroute event (the one extra repair past the free reroute already spent), prints `repair-exhausted <the step's own case>` and exits 1, never `revise`, while with only the first reroute event it still prints `repair <the step's own case>`; the green adds the bound WITHOUT a `case is None and` guard on the rerouted path (unreachable there: `rerouted` forces `case` to None and `older` to []; verify-green rejected it as an equivalent mutant) and leaves the live non-rerouted `case is None and` guard at wrong_test_route.py:300 alone, so no case need pin a guard; no new budget knob and nothing read from `VERI_MISSING_REROUTE_BUDGET`; a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py pins it, red without the bound ⟦added⟧ ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 4 | ? | ? | nothing-left 2, nothing-structural 2 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 26 | 21 | 20 | 19 | 22 | 21 | 29 | 24 | 25 | 24 | 21 | 20 | 22 | 22 | 27 | 24 | 24 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 3 | 2 | 1 | 2 | 1 | 2 | 1 | 3 | 2 | 3 | 2 | 3 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 16 | 3 | 2 | 1 | 1 | 2 | 1 | 1 | 0 | 1 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 3 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 17 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 21 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 0 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 0 | 2 | 2 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 0 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 19 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 28 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 176 | 336 | 66299 | 3009445 | 835658 | 13.12 (estimate) |
