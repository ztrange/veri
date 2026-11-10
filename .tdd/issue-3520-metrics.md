### 📊 Metrics — issue 3520

Wall time for the issue: 3735 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 10 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3522.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $6.82 over 141 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78458 tokens, largest 187312 tokens
Conductor context: first turn 78410 tokens, largest 158901 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78458 |
| 2 | $0.07 | 84438 |
| 3 | $0.03 | 85711 |
| 4 | $0.05 | 87626 |
| 5 | $0.03 | 88135 |
| 6 | $0.02 | 88408 |
| 7 | $0.03 | 88815 |
| 8 | $0.03 | 89081 |
| 9 | $0.03 | 89681 |
| 10 | $0.03 | 89944 |
| 11 | $0.04 | 90696 |
| 12 | $0.03 | 91132 |
| 13 | $0.05 | 94304 |
| 14 | $0.05 | 96684 |
| 15 | $0.06 | 101360 |
| 16 | $0.05 | 103761 |
| 17 | $0.04 | 104590 |
| 18 | $0.04 | 106410 |
| 19 | $0.04 | 106903 |
| 20 | $0.03 | 107695 |
| 21 | $0.04 | 108200 |
| 22 | $0.05 | 110455 |
| 23 | $0.03 | 111118 |
| 24 | $0.05 | 113561 |
| 25 | $0.04 | 114094 |
| 26 | $0.04 | 114695 |
| 27 | $0.04 | 115742 |
| 28 | $0.05 | 119155 |
| 29 | $0.04 | 119801 |
| 30 | $0.04 | 119979 |
| 31 | $0.03 | 120485 |
| 32 | $0.04 | 120947 |
| 33 | $0.04 | 122000 |
| 34 | $0.04 | 122801 |
| 35 | $0.04 | 123388 |
| 36 | $0.04 | 123595 |
| 37 | $0.03 | 123829 |
| 38 | $0.04 | 124746 |
| 39 | $0.04 | 125514 |
| 40 | $0.04 | 126167 |
| 41 | $0.04 | 127053 |
| 42 | $0.04 | 127750 |
| 43 | $0.04 | 128454 |
| 44 | $0.04 | 128824 |
| 45 | $0.04 | 129853 |
| 46 | $0.04 | 130493 |
| 47 | $0.04 | 131164 |
| 48 | $0.05 | 132347 |
| 49 | $0.04 | 133011 |
| 50 | $0.04 | 133606 |
| 51 | $0.04 | 134719 |
| 52 | $0.05 | 135435 |
| 53 | $0.11 | 144617 |
| 54 | $0.04 | 145003 |
| 55 | $0.05 | 146616 |
| 56 | $0.04 | 147487 |
| 57 | $0.05 | 148488 |
| 58 | $0.05 | 149558 |
| 59 | $0.09 | 156636 |
| 60 | $0.05 | 157310 |
| 61 | $0.04 | 157911 |
| 62 | $0.05 | 158430 |
| 63 | $0.05 | 159454 |
| 64 | $0.16 | 175252 |
| 65 | $0.05 | 175534 |
| 66 | $0.05 | 175940 |
| 67 | $0.04 | 176126 |
| 68 | $0.05 | 176284 |
| 69 | $0.05 | 176725 |
| 70 | $0.05 | 177762 |
| 71 | $0.05 | 178978 |
| 72 | $0.06 | 180010 |
| 73 | $0.05 | 181086 |
| 74 | $0.05 | 182420 |
| 75 | $0.05 | 183032 |
| 76 | $0.05 | 183578 |
| 77 | $0.05 | 183815 |
| 78 | $0.05 | 184107 |
| 79 | $0.05 | 184452 |
| 80 | $0.05 | 184937 |
| 81 | $0.05 | 186032 |
| 82 | $0.06 | 186949 |
| 83 | $0.04 | 187132 |
| 84 | $0.05 | 187312 |
| 85 | $0.49 | 78410 |
| 86 | $0.06 | 84386 |
| 87 | $0.04 | 86707 |
| 88 | $0.03 | 88626 |
| 89 | $0.04 | 91374 |
| 90 | $0.02 | 91946 |
| 91 | $0.02 | 92442 |
| 92 | $0.02 | 92750 |
| 93 | $0.02 | 93001 |
| 94 | $0.02 | 93279 |
| 95 | $0.02 | 94053 |
| 96 | $0.05 | 98489 |
| 97 | $0.03 | 99350 |
| 98 | $0.02 | 99990 |
| 99 | $0.02 | 100428 |
| 100 | $0.04 | 102678 |
| 101 | $0.03 | 103436 |
| 102 | $0.07 | 109865 |
| 103 | $0.03 | 110443 |
| 104 | $0.02 | 110745 |
| 105 | $0.03 | 111339 |
| 106 | $0.04 | 114119 |
| 107 | $0.04 | 115937 |
| 108 | $0.03 | 116554 |
| 109 | $0.03 | 116990 |
| 110 | $0.03 | 118099 |
| 111 | $0.03 | 118717 |
| 112 | $0.03 | 119473 |
| 113 | $0.03 | 120682 |
| 114 | $0.03 | 121794 |
| 115 | $0.03 | 122359 |
| 116 | $0.03 | 123048 |
| 117 | $0.03 | 123710 |
| 118 | $0.03 | 124468 |
| 119 | $0.03 | 125358 |
| 120 | $0.03 | 126469 |
| 121 | $0.15 | 142359 |
| 122 | $0.03 | 142756 |
| 123 | $0.03 | 143242 |
| 124 | $0.04 | 144232 |
| 125 | $0.03 | 144751 |
| 126 | $0.04 | 145610 |
| 127 | $0.03 | 146331 |
| 128 | $0.03 | 146711 |
| 129 | $0.06 | 150884 |
| 130 | $0.05 | 153257 |
| 131 | $0.03 | 153607 |
| 132 | $0.04 | 154663 |
| 133 | $0.04 | 156142 |
| 134 | $0.04 | 156834 |
| 135 | $0.04 | 157419 |
| 136 | $0.03 | 157604 |
| 137 | $0.04 | 158101 |
| 138 | $0.03 | 158326 |
| 139 | $0.03 | 158641 |
| 140 | $0.03 | 158901 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 1 | 446 | $0.01 |
| 🟢 Green | 1 | 446 | $0.01 |
| 🛠️ Refactor | 1 | 446 | $0.01 |
| 🔎 verify-green | 1 | 446 | $0.01 |
| 🔎 verify-refactor | 1 | 446 | $0.01 |
| 🔎 verify-<phase> (revised) | 1 | 446 | $0.01 |
| 🗺️ Plan | 1 | 446 | $0.01 |
| 🗺️ verify-plan | 2 | 462 | $0.01 |
| ▶️ Resuming | 1 | 8 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 8 | 2700 | $0.05 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 2 | 0 | 0 | 29 | 23 | 2 | 4 | 2663 | 0 | 40660 | 0.13 |
| diff | 6 | 3 | 0 | 0 | 321 | 123 | 35 | 64 | 10329 | 545756 | 106990 | 0.43 |
| red | 6 | 1 | 0 | 0 | 253 | 188 | 38 | 72 | 16702 | 806172 | 142315 | 0.60 |
| pin | 4 | 3 | 1 | 0 | 116 | 87 | 17 | 34 | 5976 | 259496 | 58644 | 0.23 |
| green | 2 | 1 | 0 | 0 | 119 | 40 | 13 | 24 | 2872 | 208572 | 31942 | 0.13 |
| refactor | 1 | 0 | 0 | 0 | 10 | 7 | 2 | 4 | 365 | 24034 | 14608 | 0.04 |
| prose | 15 | 0 | 0 | 0 | 504 | 476 | 15 | 30 | 74532 | 33078 | 614797 | 2.29 |
| skill-edit | 2 | 0 | 0 | 0 | 25 | 20 | 9 | 16 | 1997 | 308556 | 97344 | 0.29 |
| rebase | 7 | 2 | 1 | 0 | 2104 | 196 | 51 | 94 | 14863 | 870699 | 208509 | 1.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 12 | 2 | 0 | 1772 | 247 | 56 | 102 | 18664 | 705208 | 281784 | 0.96 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 446 | 270 | 66 | 124 | 24718 | 1273481 | 217708 | 0.92 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 734 | 147 | 36 | 70 | 10388 | 736040 | 104176 | 0.73 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 48 | 0.12 |
| pin | 0 | 0.00 | 24 | 0.05 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| rebase | 1707 | 0.69 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The existing case `test_main_with_a_zero_or_non_integer_target_prints_the_usage_on_stderr_and_exits_2_launching_nothing` in skills/tdd/scripts/tests/py/unit/test_dispatch.py no longer passes `--target 0` among its argvs (its other argvs and its assertion of the usage line and exit 2 kept, its name unchanged), a test-only change with no production change ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 6 | 12 | 1711 | 71709 | 29769 | 0.10 | 191 | n/a | n/a | n/a |  |  | full |
| `dispatch.sh --target -1`, `--target abc` and `--target 1.5` each exit 2 with the usage line `usage: dispatch.sh --target <N>` on stderr, launching nothing (a unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py driving dispatch in-process) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 11 | 22 | 4298 | 202554 | 35994 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `dispatch.sh --target 0` is accepted (no usage error, not exit 2) and, with solvable issues queued and no live runs, launches nothing: no `launched` line is appended to `.tdd/dispatch.log` (a unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py driving dispatch in-process, boundaries faked) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 90 | 26 | 48 | 7107 | 438000 | 88926 | 0.34 | 427 | unknown | 0/5 | nothing-left |  |  | full |
| With `--target 0`, an empty solvable queue and no live runs, dispatch does not print `queue-empty` merely because it launches nothing (a unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py driving dispatch in-process) | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 12 | 24 | 4613 | 236735 | 39480 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| With `--target 0` and live runs, dispatch still reports each run's exit (`done`, `bail`, `silent-exit`) as it does for a positive target, launching nothing in the freed slots (a unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py driving dispatch in-process) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 10 | 18 | 5315 | 190235 | 41979 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| A dispatch armed with `--target 0` and later re-armed with a positive target launches into free slots again (a unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py driving dispatch in-process) ⟦criterion 3⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 57 | 11 | 22 | 4582 | 230750 | 41130 | 0.17 | unknown | unknown | unknown | unknown |  |  | full |
| The `dispatch.sh` entry in skills/tdd/SCRIPTS.md states that `--target 0` holds dispatch (watch and report exits, launch nothing) and that re-arming with a positive `--target` resumes launching ⟦skill-edit⟧ ⟦criterion 5⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 72 | 19 | 36 | 5834 | 287254 | 67823 | 0.36 | 121 | 1/2 | unknown | unknown |  |  | full |
| Narrow the assertion of `test_main_with_target_0_and_a_live_run_that_exits_prints_its_done_line_and_exits_0_launching_nothing_issue_3520` in skills/tdd/scripts/tests/py/unit/test_dispatch.py so its launches-nothing half can fail: before the live run exit is reported, dispatch makes at least one pass with an issue queued and fewer live runs than a target of 1 would fill, so a launch under `--target 0` would be recorded before the exit line returns; within the same case, a contrast run of the same fixture under `--target 1` records that launch, showing the fixture observes launches; the edited case goes red when the hold is removed (`--target 0` read as 1) and on the pre-change code; no case added or removed, no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 15 | 30 | 4587 | 283144 | 40964 | 0.18 | 231 | n/a | n/a | n/a |  |  | full |
| The `USAGE` line of skills/tdd/scripts/veri/dispatch.py and the `Usage:` header of skills/tdd/scripts/dispatch.sh keep their `dispatch.sh --target <N>` start and add that `<N>` is a whole number >= 0 and that `--target 0` holds dispatch (keeps watching and reporting exits, launches nothing); the cases in skills/tdd/scripts/tests/py/unit/test_dispatch.py that compare the usage line verbatim are updated to the new line in the same change, no case added or removed, no behaviour changed ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 14 | 22 | 4031 | 190903 | 36257 | 0.15 | 289 | n/a | n/a | n/a |  |  | full |
| `skills/tdd/SCRIPTS.md`: requirement SC89 in its list takes the issue row for SC89 (`<N>` a whole number >= 0, `--target 0` holding dispatch while it keeps reporting exits, and re-arming with a positive `--target` to resume launching); the `dispatch.sh` entry already states all three, so only the list and its `GRADED` signature change ⟦skill-edit⟧ ⟦added⟧ ⟦criterion 5⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 43 | 1 | 2 | 6666 | 649 | 74017 | 0.25 | unknown | unknown | unknown | unknown |  |  | full |
| `skills/vdev/SKILL.md` says that `--target 0` holds dispatch while the watch keeps reporting exits: its *Watching* section beside `$S/dispatch.sh --target <N>`, and *The slot decision* step 1, where an N of 0 restarts `dispatch.sh` with `--target 0` and a later positive N restarts it with that `--target` to resume launching (issue rows D15 and D38) ⟦skill-edit⟧ ⟦added⟧ ⟦criterion 5⟧ | 9 | 1 | 1 | 0 | 0 | 0 | 190 | 41 | 74 | 17718 | 669688 | 209161 | 0.95 | 99 | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `dispatch.sh --target 0` is accepted (no usage error, not exit 2) and, with solvable issues queued and no live runs, launches nothing: no `launched` line is appended to `.tdd/dispatch.log` (a unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py driving dispatch in-process, boundaries faked) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| `dispatch.sh --target 0` is accepted (no usage error, not exit 2) and, with solvable issues queued and no live runs, launches nothing: no `launched` line is appended to `.tdd/dispatch.log` (a unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py driving dispatch in-process, boundaries faked) ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 2 | ? | ? | nothing-left 1, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 23 | 26 | 22 | 22 | 23 | 22 | 22 | 22 | 23 | 22 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 201 | 221 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 2 | 2 | 2 | 2 |
| all | 24 | 28 | 232 | 21 | 21 | 360 | 524 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 182 | 342 | 130299 | 3056363 | 1315809 | 12.01 (estimate) |
