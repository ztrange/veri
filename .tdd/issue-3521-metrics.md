### 📊 Metrics — issue 3521

Wall time for the issue: 647 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 6 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $13.15 over 247 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78378 tokens, largest 222831 tokens
Conductor context: first turn 78379 tokens, largest 145303 tokens
Conductor context: first turn 78381 tokens, largest 108353 tokens
Conductor context: first turn 78379 tokens, largest 157698 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78378 |
| 2 | $0.07 | 84390 |
| 3 | $0.04 | 86088 |
| 4 | $0.04 | 87683 |
| 5 | $0.03 | 87883 |
| 6 | $0.03 | 88572 |
| 7 | $0.03 | 88975 |
| 8 | $0.03 | 89306 |
| 9 | $0.03 | 89754 |
| 10 | $0.03 | 90093 |
| 11 | $0.03 | 90458 |
| 12 | $0.03 | 91076 |
| 13 | $0.03 | 91380 |
| 14 | $0.10 | 99816 |
| 15 | $0.05 | 102715 |
| 16 | $0.04 | 103838 |
| 17 | $0.04 | 104953 |
| 18 | $0.03 | 105385 |
| 19 | $0.04 | 106073 |
| 20 | $0.04 | 106647 |
| 21 | $0.03 | 107047 |
| 22 | $0.03 | 107565 |
| 23 | $0.14 | 120935 |
| 24 | $0.05 | 122126 |
| 25 | $0.04 | 122952 |
| 26 | $0.11 | 132819 |
| 27 | $0.05 | 134493 |
| 28 | $0.04 | 135295 |
| 29 | $0.04 | 136073 |
| 30 | $0.05 | 137568 |
| 31 | $0.05 | 138716 |
| 32 | $0.04 | 139128 |
| 33 | $0.05 | 140612 |
| 34 | $0.04 | 141545 |
| 35 | $0.05 | 143060 |
| 36 | $0.06 | 145428 |
| 37 | $0.04 | 147116 |
| 38 | $0.04 | 147540 |
| 39 | $0.06 | 150022 |
| 40 | $0.05 | 150648 |
| 41 | $0.04 | 151492 |
| 42 | $0.05 | 152248 |
| 43 | $0.04 | 152888 |
| 44 | $0.04 | 153654 |
| 45 | $0.05 | 154096 |
| 46 | $0.05 | 155055 |
| 47 | $0.05 | 156489 |
| 48 | $0.04 | 156811 |
| 49 | $0.05 | 157427 |
| 50 | $0.04 | 158202 |
| 51 | $0.05 | 158643 |
| 52 | $0.05 | 159239 |
| 53 | $0.04 | 159578 |
| 54 | $0.04 | 160072 |
| 55 | $0.05 | 160874 |
| 56 | $0.05 | 161065 |
| 57 | $0.04 | 161709 |
| 58 | $0.07 | 164556 |
| 59 | $0.05 | 165359 |
| 60 | $0.04 | 165960 |
| 61 | $0.05 | 166410 |
| 62 | $0.06 | 168166 |
| 63 | $0.04 | 168218 |
| 64 | $0.05 | 168656 |
| 65 | $0.04 | 169095 |
| 66 | $0.05 | 169777 |
| 67 | $0.05 | 170062 |
| 68 | $0.05 | 170822 |
| 69 | $0.05 | 171626 |
| 70 | $0.04 | 171815 |
| 71 | $0.05 | 172004 |
| 72 | $0.05 | 172493 |
| 73 | $0.05 | 173151 |
| 74 | $0.04 | 173336 |
| 75 | $0.05 | 174156 |
| 76 | $0.05 | 174869 |
| 77 | $0.05 | 175058 |
| 78 | $0.04 | 175247 |
| 79 | $0.05 | 175557 |
| 80 | $0.05 | 176320 |
| 81 | $0.05 | 177136 |
| 82 | $0.05 | 177325 |
| 83 | $0.05 | 177618 |
| 84 | $0.05 | 178335 |
| 85 | $0.05 | 179086 |
| 86 | $0.05 | 179763 |
| 87 | $0.06 | 182022 |
| 88 | $0.06 | 182708 |
| 89 | $0.05 | 183917 |
| 90 | $0.05 | 184369 |
| 91 | $0.05 | 184799 |
| 92 | $0.05 | 185018 |
| 93 | $0.05 | 185233 |
| 94 | $0.05 | 185507 |
| 95 | $0.05 | 186575 |
| 96 | $0.07 | 189653 |
| 97 | $0.06 | 190997 |
| 98 | $0.06 | 192128 |
| 99 | $0.05 | 192315 |
| 100 | $0.05 | 192648 |
| 101 | $0.05 | 193107 |
| 102 | $0.05 | 193295 |
| 103 | $0.05 | 193483 |
| 104 | $0.05 | 193671 |
| 105 | $0.05 | 193968 |
| 106 | $0.05 | 194431 |
| 107 | $0.06 | 195367 |
| 108 | $0.05 | 196067 |
| 109 | $0.05 | 196254 |
| 110 | $0.06 | 196904 |
| 111 | $0.05 | 197491 |
| 112 | $0.05 | 197679 |
| 113 | $0.05 | 198017 |
| 114 | $0.05 | 198505 |
| 115 | $0.06 | 199234 |
| 116 | $0.06 | 200168 |
| 117 | $0.17 | 215959 |
| 118 | $0.06 | 216162 |
| 119 | $0.05 | 216381 |
| 120 | $0.06 | 216751 |
| 121 | $0.05 | 216986 |
| 122 | $0.06 | 217248 |
| 123 | $0.05 | 217772 |
| 124 | $0.06 | 217988 |
| 125 | $0.05 | 218346 |
| 126 | $0.06 | 218636 |
| 127 | $0.06 | 218951 |
| 128 | $0.05 | 219350 |
| 129 | $0.06 | 219768 |
| 130 | $0.05 | 220045 |
| 131 | $0.06 | 221056 |
| 132 | $0.06 | 222443 |
| 133 | $0.06 | 222831 |
| 134 | $0.49 | 78379 |
| 135 | $0.08 | 84390 |
| 136 | $0.04 | 86120 |
| 137 | $0.04 | 88097 |
| 138 | $0.06 | 92486 |
| 139 | $0.03 | 93105 |
| 140 | $0.03 | 93599 |
| 141 | $0.03 | 93922 |
| 142 | $0.03 | 94438 |
| 143 | $0.05 | 97005 |
| 144 | $0.08 | 103488 |
| 145 | $0.05 | 105550 |
| 146 | $0.03 | 106046 |
| 147 | $0.04 | 107083 |
| 148 | $0.04 | 107894 |
| 149 | $0.03 | 108687 |
| 150 | $0.04 | 109346 |
| 151 | $0.03 | 109795 |
| 152 | $0.04 | 110520 |
| 153 | $0.04 | 111140 |
| 154 | $0.04 | 112850 |
| 155 | $0.04 | 113256 |
| 156 | $0.03 | 113686 |
| 157 | $0.04 | 114208 |
| 158 | $0.03 | 114611 |
| 159 | $0.04 | 115244 |
| 160 | $0.04 | 116623 |
| 161 | $0.04 | 117446 |
| 162 | $0.05 | 120290 |
| 163 | $0.04 | 121150 |
| 164 | $0.11 | 130216 |
| 165 | $0.04 | 130994 |
| 166 | $0.04 | 131752 |
| 167 | $0.05 | 133596 |
| 168 | $0.04 | 134445 |
| 169 | $0.05 | 135946 |
| 170 | $0.04 | 136604 |
| 171 | $0.05 | 137660 |
| 172 | $0.04 | 138663 |
| 173 | $0.04 | 139421 |
| 174 | $0.04 | 139899 |
| 175 | $0.04 | 140415 |
| 176 | $0.05 | 140980 |
| 177 | $0.03 | 141340 |
| 178 | $0.04 | 141676 |
| 179 | $0.06 | 144129 |
| 180 | $0.04 | 144682 |
| 181 | $0.05 | 145303 |
| 182 | $0.49 | 78381 |
| 183 | $0.08 | 84396 |
| 184 | $0.04 | 86062 |
| 185 | $0.04 | 87905 |
| 186 | $0.04 | 90466 |
| 187 | $0.06 | 94810 |
| 188 | $0.04 | 95408 |
| 189 | $0.03 | 96236 |
| 190 | $0.04 | 98289 |
| 191 | $0.04 | 99148 |
| 192 | $0.03 | 99621 |
| 193 | $0.07 | 104393 |
| 194 | $0.03 | 105111 |
| 195 | $0.03 | 105460 |
| 196 | $0.05 | 106912 |
| 197 | $0.04 | 108353 |
| 198 | $0.49 | 78379 |
| 199 | $0.06 | 84393 |
| 200 | $0.03 | 86085 |
| 201 | $0.03 | 87635 |
| 202 | $0.04 | 90748 |
| 203 | $0.03 | 91708 |
| 204 | $0.05 | 95262 |
| 205 | $0.04 | 97620 |
| 206 | $0.02 | 98190 |
| 207 | $0.02 | 98609 |
| 208 | $0.04 | 100912 |
| 209 | $0.03 | 101541 |
| 210 | $0.02 | 101873 |
| 211 | $0.03 | 102581 |
| 212 | $0.02 | 102939 |
| 213 | $0.03 | 103697 |
| 214 | $0.06 | 108120 |
| 215 | $0.03 | 109077 |
| 216 | $0.03 | 109675 |
| 217 | $0.03 | 110300 |
| 218 | $0.03 | 111495 |
| 219 | $0.03 | 112137 |
| 220 | $0.02 | 112449 |
| 221 | $0.03 | 113001 |
| 222 | $0.03 | 113867 |
| 223 | $0.08 | 120770 |
| 224 | $0.03 | 121776 |
| 225 | $0.03 | 122636 |
| 226 | $0.03 | 122998 |
| 227 | $0.03 | 123991 |
| 228 | $0.03 | 124452 |
| 229 | $0.03 | 125292 |
| 230 | $0.03 | 126182 |
| 231 | $0.03 | 126888 |
| 232 | $0.10 | 136384 |
| 233 | $0.04 | 137360 |
| 234 | $0.04 | 138695 |
| 235 | $0.03 | 139514 |
| 236 | $0.04 | 140604 |
| 237 | $0.04 | 141740 |
| 238 | $0.03 | 142436 |
| 239 | $0.03 | 143013 |
| 240 | $0.03 | 143327 |
| 241 | $0.03 | 143861 |
| 242 | $0.04 | 144992 |
| 243 | $0.04 | 146383 |
| 244 | $0.04 | 147914 |
| 245 | $0.05 | 150271 |
| 246 | $0.04 | 151503 |
| 247 | $0.08 | 157698 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 8 | 3068 | $0.06 |
| 🟢 Green | 6 | 2210 | $0.04 |
| 🛠️ Refactor | 2 | 459 | $0.01 |
| 🔎 verify-green | 3 | 1312 | $0.03 |
| 🔎 verify-refactor | 2 | 459 | $0.01 |
| 🔎 verify-<phase> (revised) | 5 | 1756 | $0.04 |
| 🗺️ Plan | 1 | 439 | $0.01 |
| 🗺️ verify-plan | 3 | 889 | $0.02 |
| ▶️ Resuming | 2 | 442 | $0.01 |
| ⛔ Bailed | 1 | 421 | $0.01 |
| ⏹️ Stopped | 1 | 434 | $0.01 |
| Total | 24 | 8362 | $0.17 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 3 | 3 | 0 | 0 | 37 | 30 | 3 | 6 | 3579 | 0 | 59627 | 0.18 |
| red | 14 | 5 | 2 | 0 | 849 | 474 | 78 | 148 | 38267 | 1348321 | 339209 | 1.96 |
| green | 12 | 2 | 2 | 0 | 1995 | 353 | 78 | 148 | 30430 | 1292975 | 405892 | 1.95 |
| red-missing | 2 | 0 | 0 | 0 | 126 | 77 | 17 | 32 | 9346 | 350969 | 49533 | 0.25 |
| pin | 2 | 0 | 2 | 0 | 55 | 41 | 7 | 14 | 2550 | 102080 | 38066 | 0.13 |
| refactor | 2 | 0 | 0 | 0 | 13 | 8 | 4 | 8 | 555 | 42979 | 33663 | 0.09 |
| diff | 6 | 3 | 0 | 0 | 317 | 115 | 23 | 46 | 7456 | 330906 | 79068 | 0.31 |
| red-contradicted | 1 | 0 | 0 | 0 | 53 | 45 | 7 | 14 | 4905 | 159620 | 24293 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 19 | 13 | 6 | 0 | 2072 | 426 | 77 | 150 | 29069 | 1122579 | 381838 | 1.36 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 575 | 356 | 57 | 112 | 34103 | 1124371 | 305727 | 2.16 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 798 | 361 | 83 | 154 | 33916 | 1380900 | 341786 | 1.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 379 | 1.02 | 470 | 0.94 |
| green | 1152 | 2.01 | 1231 | 0.26 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 29 | 0.07 | 26 | 0.06 |
| refactor | 0 | 0.00 | 6 | 0.05 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 53 | 0.13 |
| preflight | 0 | 0.00 | 0 | 0.00 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 20 | 4 | 4 | 0 | 0 | 0 | 577 | 123 | 232 | 54316 | 2106133 | 603583 | 3.07 | 1824 | red 2/2, green 2/2 | 0/5 | nothing-left |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, test_2750 reads its EOF from the report closing its captured stdout within a bound of its own rather than a fixed 10 s wait, so a stand-in delay before status.py --report closes stdout, shorter than that bound, still passes; test-only, no production change, the case stays a process case ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 6 | 12 | 2232 | 79417 | 25607 | 0.09 | 155 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, test_2750 asserts its two conditions separately, so with status.py changed to hold stdout open until the refresh ends it goes red with a message naming no EOF, and a stub that never started fails with a message naming the stub not started; test-only, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 2676 | 136004 | 27023 | 0.11 | 217 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, every wait inside test_2750 (the stdout wait, the stub-started wait and the cleanup wait together) is bounded below VERI_PYTEST_TIMEOUT (30 s default), so its failure paths are reachable before pytest-timeout fires; test-only, no production change ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 8 | 16 | 2548 | 115485 | 26438 | 0.10 | 6576 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py — test_3521_report_with_a_stale_snapshot_launches_its_own_refresh_while_an_unrelated_refresh_is_alive: AssertionError: the stale report did not launch its own refresh while an unrelated refresh was alive; skills/tdd/scripts/tests/py/unit/test_file_location_resolves_symlinks.py — test_no_veri_module_locates_itself_through_abspath_of_file_3501: assert {'status.py': [471]} == {} ⟦suite-repair⟧ ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 223 | 32 | 64 | 14267 | 526072 | 162972 | 0.75 | unknown | 1/2 | 0/5 | nothing-left |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py, the scoping case's unrelated refresh lives at <tmp>/other/scripts/report-cache.sh (a directory also named scripts, not the old elsewhere), and the same case contrasts it with this script's own sibling report-cache.sh refresh being detected as already running (no second refresh launched): status.py --report with a stale snapshot still launches its own refresh while the unrelated <tmp>/other/scripts/report-cache.sh refresh is alive; production (skills/tdd/scripts/veri/status.py refresh_running, lines 468-476) compares the full resolved path of the matched script against this script's own scripts/report-cache.sh, not the basename of its directory, and the case must go red when that comparison is loosened back to the directory basename (a process case, no network) ⟦added⟧ ⟦criterion 1⟧ | 6 | 1 | 1 | 0 | 0 | 0 | 198 | 36 | 68 | 17470 | 664739 | 124101 | 0.69 | unknown | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py — test_3521_report_with_a_stale_snapshot_launches_its_own_refresh_while_an_unrelated_refresh_is_alive: AssertionError: the stale report did not launch its own refresh while an unrelated refresh was alive; skills/tdd/scripts/tests/py/unit/test_file_location_resolves_symlinks.py — test_no_veri_module_locates_itself_through_abspath_of_file_3501: assert {'status.py': [471]} == {} ⟦suite-repair⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py — test_3521_report_with_a_stale_snapshot_launches_its_own_refresh_while_an_unrelated_refresh_is_alive: AssertionError: the stale report did not launch its own refresh while an unrelated refresh was alive; skills/tdd/scripts/tests/py/unit/test_file_location_resolves_symlinks.py — test_no_veri_module_locates_itself_through_abspath_of_file_3501: assert {'status.py': [471]} == {} ⟦suite-repair⟧ ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 3 | ? | ? | nothing-left 2, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 9 | 2 | 10 | 10 | 1 | 10 | 17 | 18 | 9 | 2 | 2 | 4 | 3 | 9 | 573 | 1 | 2 | 1 | 2 | 2 | 3 | 1 | 1 | 9 | 10 | 2 | 3 | 2 | 2 | 3 | 3 | 9 | 10 | 10 | 4 | 4 |
| fast | 21 | 21 | 22 | 31 | 456 | 32 | 23 | 22 | 22 | 22 | 21 | 22 | 47 | 23 | 21 | 26 | 32 | 32 | 30 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 3 | 1 | 2 | 1 | 1 | 2 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 217 | 416 | 97088 | 3627850 | 1029351 | 18.15 (estimate) |
