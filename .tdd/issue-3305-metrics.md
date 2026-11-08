### 📊 Metrics — issue 3305

Wall time for the issue: 58 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 19 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $10.88 over 203 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78620 tokens, largest 150983 tokens
Conductor context: first turn 78619 tokens, largest 167886 tokens
Conductor context: first turn 78619 tokens, largest 156532 tokens
Conductor context: first turn 78620 tokens, largest 136160 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78620 |
| 2 | $0.07 | 84556 |
| 3 | $0.10 | 92606 |
| 4 | $0.04 | 94526 |
| 5 | $0.04 | 94960 |
| 6 | $0.03 | 95300 |
| 7 | $0.03 | 95797 |
| 8 | $0.04 | 96241 |
| 9 | $0.03 | 96729 |
| 10 | $0.06 | 99929 |
| 11 | $0.04 | 100956 |
| 12 | $0.06 | 105532 |
| 13 | $0.07 | 109799 |
| 14 | $0.05 | 111489 |
| 15 | $0.03 | 111915 |
| 16 | $0.04 | 112283 |
| 17 | $0.04 | 112519 |
| 18 | $0.03 | 112956 |
| 19 | $0.04 | 113129 |
| 20 | $0.04 | 113787 |
| 21 | $0.10 | 122247 |
| 22 | $0.04 | 122966 |
| 23 | $0.04 | 123356 |
| 24 | $0.04 | 123899 |
| 25 | $0.04 | 124287 |
| 26 | $0.04 | 124559 |
| 27 | $0.04 | 125008 |
| 28 | $0.06 | 128401 |
| 29 | $0.04 | 129174 |
| 30 | $0.13 | 140900 |
| 31 | $0.05 | 141628 |
| 32 | $0.04 | 142084 |
| 33 | $0.05 | 142729 |
| 34 | $0.04 | 143291 |
| 35 | $0.06 | 145692 |
| 36 | $0.05 | 146383 |
| 37 | $0.04 | 146741 |
| 38 | $0.05 | 147328 |
| 39 | $0.04 | 148038 |
| 40 | $0.06 | 150021 |
| 41 | $0.04 | 150499 |
| 42 | $0.05 | 150983 |
| 43 | $0.50 | 78619 |
| 44 | $0.07 | 84549 |
| 45 | $0.09 | 92592 |
| 46 | $0.04 | 93604 |
| 47 | $0.05 | 96911 |
| 48 | $0.04 | 97417 |
| 49 | $0.03 | 98143 |
| 50 | $0.03 | 98492 |
| 51 | $0.03 | 98752 |
| 52 | $0.04 | 99188 |
| 53 | $0.03 | 99480 |
| 54 | $0.03 | 99770 |
| 55 | $0.04 | 100521 |
| 56 | $0.06 | 104941 |
| 57 | $0.04 | 105889 |
| 58 | $0.03 | 106403 |
| 59 | $0.04 | 106586 |
| 60 | $0.10 | 114962 |
| 61 | $0.04 | 116316 |
| 62 | $0.04 | 116957 |
| 63 | $0.03 | 117415 |
| 64 | $0.04 | 118003 |
| 65 | $0.04 | 118866 |
| 66 | $0.04 | 119163 |
| 67 | $0.04 | 120169 |
| 68 | $0.04 | 121037 |
| 69 | $0.06 | 124290 |
| 70 | $0.04 | 125010 |
| 71 | $0.04 | 125306 |
| 72 | $0.03 | 125563 |
| 73 | $0.05 | 126611 |
| 74 | $0.04 | 127530 |
| 75 | $0.04 | 127979 |
| 76 | $0.04 | 128330 |
| 77 | $0.04 | 129081 |
| 78 | $0.04 | 129577 |
| 79 | $0.03 | 129824 |
| 80 | $0.05 | 130744 |
| 81 | $0.03 | 131027 |
| 82 | $0.04 | 131531 |
| 83 | $0.05 | 132600 |
| 84 | $0.04 | 133400 |
| 85 | $0.05 | 135477 |
| 86 | $0.08 | 140512 |
| 87 | $0.07 | 143938 |
| 88 | $0.04 | 144609 |
| 89 | $0.05 | 145498 |
| 90 | $0.05 | 147061 |
| 91 | $0.04 | 147487 |
| 92 | $0.04 | 148013 |
| 93 | $0.04 | 148327 |
| 94 | $0.05 | 148710 |
| 95 | $0.04 | 149026 |
| 96 | $0.05 | 150640 |
| 97 | $0.05 | 151888 |
| 98 | $0.05 | 153441 |
| 99 | $0.05 | 154345 |
| 100 | $0.06 | 156510 |
| 101 | $0.04 | 157045 |
| 102 | $0.05 | 158225 |
| 103 | $0.05 | 158748 |
| 104 | $0.05 | 159941 |
| 105 | $0.08 | 164541 |
| 106 | $0.05 | 165307 |
| 107 | $0.05 | 166695 |
| 108 | $0.05 | 167886 |
| 109 | $0.51 | 78619 |
| 110 | $0.07 | 84515 |
| 111 | $0.09 | 92547 |
| 112 | $0.04 | 94394 |
| 113 | $0.05 | 97389 |
| 114 | $0.06 | 101699 |
| 115 | $0.04 | 102050 |
| 116 | $0.03 | 102531 |
| 117 | $0.03 | 102865 |
| 118 | $0.03 | 103428 |
| 119 | $0.04 | 103906 |
| 120 | $0.03 | 104273 |
| 121 | $0.04 | 104940 |
| 122 | $0.04 | 106709 |
| 123 | $0.04 | 107718 |
| 124 | $0.03 | 108332 |
| 125 | $0.04 | 108702 |
| 126 | $0.03 | 109079 |
| 127 | $0.03 | 109561 |
| 128 | $0.05 | 110851 |
| 129 | $0.04 | 112169 |
| 130 | $0.04 | 113172 |
| 131 | $0.03 | 113407 |
| 132 | $0.03 | 113922 |
| 133 | $0.04 | 114586 |
| 134 | $0.04 | 115113 |
| 135 | $0.03 | 115706 |
| 136 | $0.04 | 116244 |
| 137 | $0.03 | 116397 |
| 138 | $0.04 | 117367 |
| 139 | $0.05 | 119321 |
| 140 | $0.04 | 119813 |
| 141 | $0.03 | 120366 |
| 142 | $0.04 | 120644 |
| 143 | $0.04 | 121287 |
| 144 | $0.04 | 121946 |
| 145 | $0.04 | 122704 |
| 146 | $0.03 | 123113 |
| 147 | $0.05 | 125425 |
| 148 | $0.04 | 126059 |
| 149 | $0.04 | 126640 |
| 150 | $0.04 | 127660 |
| 151 | $0.04 | 128363 |
| 152 | $0.04 | 128896 |
| 153 | $0.04 | 129281 |
| 154 | $0.04 | 129724 |
| 155 | $0.04 | 130315 |
| 156 | $0.04 | 131108 |
| 157 | $0.04 | 132231 |
| 158 | $0.05 | 133221 |
| 159 | $0.04 | 134241 |
| 160 | $0.04 | 135361 |
| 161 | $0.11 | 143977 |
| 162 | $0.04 | 144733 |
| 163 | $0.05 | 145489 |
| 164 | $0.04 | 146748 |
| 165 | $0.05 | 147475 |
| 166 | $0.04 | 148313 |
| 167 | $0.05 | 149173 |
| 168 | $0.04 | 149834 |
| 169 | $0.04 | 150213 |
| 170 | $0.05 | 151198 |
| 171 | $0.05 | 152164 |
| 172 | $0.04 | 152818 |
| 173 | $0.05 | 153561 |
| 174 | $0.05 | 155448 |
| 175 | $0.05 | 156030 |
| 176 | $0.04 | 156532 |
| 177 | $0.49 | 78620 |
| 178 | $0.06 | 84556 |
| 179 | $0.08 | 92597 |
| 180 | $0.05 | 96702 |
| 181 | $0.05 | 101067 |
| 182 | $0.02 | 101465 |
| 183 | $0.02 | 101922 |
| 184 | $0.02 | 102261 |
| 185 | $0.02 | 102666 |
| 186 | $0.04 | 105153 |
| 187 | $0.04 | 108079 |
| 188 | $0.05 | 111014 |
| 189 | $0.03 | 111923 |
| 190 | $0.03 | 112733 |
| 191 | $0.04 | 114657 |
| 192 | $0.03 | 115363 |
| 193 | $0.03 | 116287 |
| 194 | $0.03 | 116735 |
| 195 | $0.09 | 124907 |
| 196 | $0.03 | 125874 |
| 197 | $0.03 | 126493 |
| 198 | $0.03 | 127081 |
| 199 | $0.03 | 128085 |
| 200 | $0.04 | 130284 |
| 201 | $0.03 | 130948 |
| 202 | $0.07 | 136160 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 7 | 3316 | $0.07 |
| 🟢 Green | 4 | 1916 | $0.04 |
| 🛠️ Refactor | 2 | 919 | $0.02 |
| 🔎 verify-green | 4 | 1916 | $0.04 |
| 🔎 verify-refactor | 2 | 919 | $0.02 |
| 🔎 verify-<phase> (revised) | 3 | 1357 | $0.03 |
| 🗺️ Plan | 1 | 559 | $0.01 |
| 🗺️ verify-plan | 3 | 1478 | $0.03 |
| ▶️ Resuming | 3 | 927 | $0.02 |
| ⛔ Bailed | 1 | 481 | $0.01 |
| ⏹️ Stopped | 2 | 997 | $0.02 |
| Total | 24 | 11031 | $0.22 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 3 | 3 | 0 | 0 | 80 | 69 | 7 | 14 | 8090 | 108773 | 87610 | 0.31 |
| red | 16 | 5 | 1 | 0 | 754 | 286 | 73 | 140 | 31105 | 1530218 | 419938 | 1.74 |
| green | 11 | 3 | 1 | 0 | 2772 | 269 | 75 | 142 | 22961 | 1629299 | 319214 | 1.58 |
| refactor | 3 | 0 | 0 | 0 | 27 | 15 | 7 | 12 | 1363 | 78599 | 74050 | 0.21 |
| pin | 3 | 3 | 0 | 0 | 74 | 35 | 12 | 24 | 3411 | 233794 | 62909 | 0.21 |
| exhausted | 1 | 0 | 0 | 0 | 93 | 18 | 3 | 6 | 1291 | 46295 | 24938 | 0.16 |
| diff | 4 | 2 | 0 | 0 | 361 | 53 | 16 | 32 | 6211 | 333422 | 102243 | 0.35 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 18 | 16 | 2 | 0 | 1253 | 238 | 62 | 124 | 25130 | 1193454 | 416272 | 1.41 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 2442 | 333 | 91 | 172 | 32960 | 1957124 | 459352 | 1.96 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 466 | 174 | 40 | 74 | 16342 | 809822 | 215278 | 1.19 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 267 | 0.63 |
| green | 551 | 0.39 | 1179 | 0.77 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 93 | 0.16 |
| diff | 0 | 0.00 | 0 | 0.00 |
| suite-repair | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tick-ledger.sh --unpinnable <reason-file> --case <id>` with a reason saying `stays green` and a named case that fails exits 1: the line stays unticked and unmarked, no `unpinnable-step` event is written, and stderr names the step and the failing case; the case is run through one wrapper in `veri/tick_ledger.py` that runs `make test TESTS="<id>"`, which cases swap for an in-process spy (small unit case, no real process) ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 70 | 19 | 34 | 6782 | 339318 | 128600 | 0.42 | 1652 | unknown | 0/5 | nothing-left |  |  | full |
| `tick-ledger.sh --already-holds <reason-file> --case <id>` with a non-blank `REASON:` line and a named case that fails exits 1: the line stays unticked and unmarked, no `already-holds-step` event is written, and stderr names the step and the failing case (the case-run wrapper swapped for an in-process spy) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 8 | 16 | 3084 | 166335 | 46282 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| `tick-ledger.sh --unpinnable <reason-file> --case <id>` with a reason saying `stays green` and a named case that passes exits 0: the line is ticked with ` ⟂ retired unpinnable` and one `unpinnable-step` event is written (the case-run wrapper swapped for an in-process spy that passes) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 10 | 20 | 4139 | 229853 | 47720 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| `tick-ledger.sh --already-holds <reason-file> --case <id>` with a non-blank `REASON:` line and a named case that passes exits 0: the line is ticked with ` ⟂ retired already holds` and one `already-holds-step` event is written (the case-run wrapper swapped for an in-process spy that passes) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 10 | 20 | 3926 | 232434 | 48348 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| `tick-ledger.sh`'s usage line, in `veri/tick_ledger.py` and the shim's header, names the case option: `usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher>`; the Red updates the `USAGE` constant `tests/py/unit/test_tick_ledger.py` pins verbatim (its line 11) to that line, and the usage case near its line 622 keeps passing ⟦criterion 1⟧ | 10 | 2 | 1 | 0 | 0 | 0 | 257 | 61 | 118 | 22319 | 1324525 | 290875 | 1.55 | unknown | green 1/2, red 1/2 | unknown | unknown |  |  | full |
| `tick-ledger.sh`'s usage line, in `veri/tick_ledger.py` and the shim's header, names the case option: `usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher>`; the Red updates the `USAGE` constant `tests/py/unit/test_tick_ledger.py` pins verbatim (its line 11) to that line, and the usage case near its line 622 keeps passing; the Red also updates the `tick-ledger.sh` checksum pin at `tests/py/unit/test_emitted_text.py` line 47 from `2087776818 176` to `2448343706 190`, which the new usage line makes stale ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 66 | 25 | 50 | 7181 | 510037 | 153451 | 0.51 | 1158 | unknown | 0/5 | nothing-left |  |  | full |
| The existing cases that call `--unpinnable` or `--already-holds` in `tests/py/unit/test_tick_ledger_unpinnable.py`, `tests/py/unit/test_tick_ledger_already_holds.py` and `tests/py/test_resume_clean_process.py` (the `--unpinnable` call near line 277) name a passing case with `--case <id>`, the case-run wrapper swapped for an in-process spy that passes, and keep passing; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 8 | 16 | 3101 | 164582 | 55844 | 0.19 | 331 | n/a | n/a | n/a |  |  | full |
| The existing cases in `tests/py/unit/test_pin_reject_route.py` pass a target test as a new final argument after the matcher (the case-run wrapper swapped for an in-process spy that passes where the step retires; the two-argument `few` call stays a too-few-arguments call) and keep passing; test-only, no production change ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 8 | 16 | 3110 | 168840 | 46399 | 0.16 | 260 | n/a | n/a | n/a |  |  | full |
| `pin-reject-route.sh <reason-file> <ledger-file> <matcher> <target-test>` passes `<target-test>` to `tick_ledger` as the `--case` of its `--unpinnable` call: with a reason saying `stays green` and a target test that fails (the case-run wrapper swapped for an in-process spy) it prints `revise`, exits 1, and the line stays unticked and unmarked ⟦criterion 4⟧ | 8 | 2 | 1 | 0 | 0 | 0 | 129 | 37 | 66 | 12700 | 715703 | 185773 | 0.89 | 1786 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tick-ledger.sh --unpinnable <reason-file> --case <id>` with a reason saying `stays green` and a named case that fails exits 1: the line stays unticked and unmarked, no `unpinnable-step` event is written, and stderr names the step and the failing case; the case is run through one wrapper in `veri/tick_ledger.py` that runs `make test TESTS="<id>"`, which cases swap for an in-process spy (small unit case, no real process) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.07 |
| `tick-ledger.sh`'s usage line, in `veri/tick_ledger.py` and the shim's header, names the case option: `usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher>`; the Red updates the `USAGE` constant `tests/py/unit/test_tick_ledger.py` pins verbatim (its line 11) to that line, and the usage case near its line 622 keeps passing; the Red also updates the `tick-ledger.sh` checksum pin at `tests/py/unit/test_emitted_text.py` line 47 from `2087776818 176` to `2448343706 190`, which the new usage line makes stale ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.06 |
| `pin-reject-route.sh <reason-file> <ledger-file> <matcher> <target-test>` passes `<target-test>` to `tick_ledger` as the `--case` of its `--unpinnable` call: with a reason saying `stays green` and a target test that fails (the case-run wrapper swapped for an in-process spy) it prints `revise`, exits 1, and the line stays unticked and unmarked ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.07 |

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| `tick-ledger.sh --unpinnable <reason-file> --case <id>` with a reason saying `stays green` and a named case that fails exits 1: the line stays unticked and unmarked, no `unpinnable-step` event is written, and stderr names the step and the failing case; the case is run through one wrapper in `veri/tick_ledger.py` that runs `make test TESTS="<id>"`, which cases swap for an in-process spy (small unit case, no real process) ⟦criterion 3⟧ | 1 | 0 | 1 | nothing-left 1 |
| `tick-ledger.sh`'s usage line, in `veri/tick_ledger.py` and the shim's header, names the case option: `usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher>`; the Red updates the `USAGE` constant `tests/py/unit/test_tick_ledger.py` pins verbatim (its line 11) to that line, and the usage case near its line 622 keeps passing; the Red also updates the `tick-ledger.sh` checksum pin at `tests/py/unit/test_emitted_text.py` line 47 from `2087776818 176` to `2448343706 190`, which the new usage line makes stale ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| `pin-reject-route.sh <reason-file> <ledger-file> <matcher> <target-test>` passes `<target-test>` to `tick_ledger` as the `--case` of its `--unpinnable` call: with a reason saying `stays green` and a target test that fails (the case-run wrapper swapped for an in-process spy) it prints `revise`, exits 1, and the line stays unticked and unmarked ⟦criterion 4⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 3 | 0 | 3 | nothing-left 3 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 6 | 5 | 4 | 5 | 4 | 4 | 3 | 4 | 5 | 73 | 6 | 248 | 2 | 6 | 4 | 3 | 5 | 5 | 4 | 279 | 7 | 11 | 3 | 3 | 4 | 4 | 4 | 6 | 8 | 3 | 8 |
| fast | 97 | 68 | 49 | 48 | 51 | 64 | 60 | 79 | 53 | 48 | 77 | 65 | 63 | 67 | 65 | 77 | 56 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 4 | 3 | 7 | 3 | 3 | 2 | 7 | 4 | 5 | 4 | 2 | 4 | 4 | 2 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 193 | 370 | 74432 | 3960400 | 1090902 | 15.44 (estimate) |
