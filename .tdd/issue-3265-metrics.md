### 📊 Metrics — issue 3265

Wall time for the issue: 3183 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 18 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $9.03 over 185 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78709 tokens, largest 207058 tokens
Conductor context: first turn 77701 tokens, largest 173327 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78709 |
| 2 | $0.07 | 84513 |
| 3 | $0.04 | 85625 |
| 4 | $0.04 | 87639 |
| 5 | $0.03 | 87948 |
| 6 | $0.03 | 88332 |
| 7 | $0.03 | 88878 |
| 8 | $0.04 | 89605 |
| 9 | $0.03 | 89954 |
| 10 | $0.04 | 91993 |
| 11 | $0.05 | 94946 |
| 12 | $0.04 | 95574 |
| 13 | $0.09 | 102972 |
| 14 | $0.07 | 108007 |
| 15 | $0.03 | 108426 |
| 16 | $0.04 | 109548 |
| 17 | $0.04 | 110117 |
| 18 | $0.04 | 110613 |
| 19 | $0.03 | 111254 |
| 20 | $0.05 | 112592 |
| 21 | $0.03 | 112861 |
| 22 | $0.04 | 113729 |
| 23 | $0.04 | 114264 |
| 24 | $0.04 | 115030 |
| 25 | $0.04 | 116106 |
| 26 | $0.04 | 117006 |
| 27 | $0.04 | 117907 |
| 28 | $0.10 | 126481 |
| 29 | $0.05 | 127753 |
| 30 | $0.04 | 128037 |
| 31 | $0.04 | 128513 |
| 32 | $0.05 | 130301 |
| 33 | $0.04 | 130958 |
| 34 | $0.04 | 131642 |
| 35 | $0.04 | 132396 |
| 36 | $0.05 | 133326 |
| 37 | $0.04 | 134051 |
| 38 | $0.04 | 134370 |
| 39 | $0.04 | 135055 |
| 40 | $0.04 | 135922 |
| 41 | $0.05 | 137026 |
| 42 | $0.04 | 137535 |
| 43 | $0.04 | 138104 |
| 44 | $0.05 | 138763 |
| 45 | $0.04 | 139479 |
| 46 | $0.04 | 140033 |
| 47 | $0.04 | 140500 |
| 48 | $0.05 | 141570 |
| 49 | $0.05 | 143186 |
| 50 | $0.05 | 143654 |
| 51 | $0.04 | 144645 |
| 52 | $0.07 | 148196 |
| 53 | $0.04 | 148590 |
| 54 | $0.04 | 148747 |
| 55 | $0.05 | 149431 |
| 56 | $0.04 | 150009 |
| 57 | $0.06 | 151613 |
| 58 | $0.04 | 152490 |
| 59 | $0.05 | 153004 |
| 60 | $0.05 | 154830 |
| 61 | $0.05 | 155725 |
| 62 | $0.05 | 156206 |
| 63 | $0.04 | 156825 |
| 64 | $0.05 | 157845 |
| 65 | $0.05 | 159120 |
| 66 | $0.05 | 159531 |
| 67 | $0.05 | 160823 |
| 68 | $0.05 | 161570 |
| 69 | $0.06 | 163235 |
| 70 | $0.04 | 163808 |
| 71 | $0.05 | 164738 |
| 72 | $0.05 | 165512 |
| 73 | $0.05 | 166032 |
| 74 | $0.06 | 167538 |
| 75 | $0.04 | 167966 |
| 76 | $0.05 | 168622 |
| 77 | $0.05 | 169365 |
| 78 | $0.05 | 170076 |
| 79 | $0.05 | 170393 |
| 80 | $0.05 | 171220 |
| 81 | $0.05 | 171738 |
| 82 | $0.05 | 172426 |
| 83 | $0.05 | 172944 |
| 84 | $0.05 | 173589 |
| 85 | $0.04 | 173871 |
| 86 | $0.05 | 174732 |
| 87 | $0.05 | 175029 |
| 88 | $0.05 | 175677 |
| 89 | $0.05 | 176219 |
| 90 | $0.05 | 176932 |
| 91 | $0.06 | 177806 |
| 92 | $0.04 | 178167 |
| 93 | $0.06 | 179028 |
| 94 | $0.05 | 180050 |
| 95 | $0.05 | 180383 |
| 96 | $0.06 | 181732 |
| 97 | $0.05 | 182165 |
| 98 | $0.05 | 182848 |
| 99 | $0.05 | 184000 |
| 100 | $0.06 | 185007 |
| 101 | $0.05 | 185393 |
| 102 | $0.06 | 186579 |
| 103 | $0.05 | 187665 |
| 104 | $0.05 | 188215 |
| 105 | $0.08 | 192209 |
| 106 | $0.07 | 194735 |
| 107 | $0.06 | 196186 |
| 108 | $0.06 | 196935 |
| 109 | $0.06 | 198229 |
| 110 | $0.09 | 203703 |
| 111 | $0.06 | 204156 |
| 112 | $0.06 | 205689 |
| 113 | $0.06 | 207058 |
| 114 | $0.48 | 77701 |
| 115 | $0.06 | 83494 |
| 116 | $0.03 | 84627 |
| 117 | $0.03 | 86155 |
| 118 | $0.04 | 89266 |
| 119 | $0.05 | 92793 |
| 120 | $0.02 | 93399 |
| 121 | $0.02 | 93966 |
| 122 | $0.02 | 94384 |
| 123 | $0.02 | 94889 |
| 124 | $0.02 | 95532 |
| 125 | $0.05 | 99943 |
| 126 | $0.03 | 100702 |
| 127 | $0.02 | 101097 |
| 128 | $0.03 | 101793 |
| 129 | $0.09 | 110396 |
| 130 | $0.03 | 111909 |
| 131 | $0.03 | 112449 |
| 132 | $0.03 | 113132 |
| 133 | $0.03 | 114310 |
| 134 | $0.03 | 114864 |
| 135 | $0.03 | 115779 |
| 136 | $0.03 | 116201 |
| 137 | $0.03 | 117428 |
| 138 | $0.03 | 118180 |
| 139 | $0.03 | 119201 |
| 140 | $0.03 | 120078 |
| 141 | $0.03 | 120780 |
| 142 | $0.03 | 121602 |
| 143 | $0.03 | 122826 |
| 144 | $0.03 | 123556 |
| 145 | $0.03 | 124509 |
| 146 | $0.03 | 125496 |
| 147 | $0.03 | 126325 |
| 148 | $0.03 | 127518 |
| 149 | $0.03 | 127892 |
| 150 | $0.03 | 128965 |
| 151 | $0.04 | 130647 |
| 152 | $0.04 | 132062 |
| 153 | $0.05 | 134493 |
| 154 | $0.03 | 134914 |
| 155 | $0.04 | 136133 |
| 156 | $0.04 | 137160 |
| 157 | $0.03 | 137543 |
| 158 | $0.04 | 138775 |
| 159 | $0.04 | 139892 |
| 160 | $0.03 | 140215 |
| 161 | $0.04 | 141135 |
| 162 | $0.05 | 143968 |
| 163 | $0.03 | 144690 |
| 164 | $0.04 | 145864 |
| 165 | $0.03 | 146158 |
| 166 | $0.08 | 151983 |
| 167 | $0.04 | 152996 |
| 168 | $0.03 | 153318 |
| 169 | $0.04 | 153861 |
| 170 | $0.04 | 155609 |
| 171 | $0.04 | 156846 |
| 172 | $0.03 | 157153 |
| 173 | $0.04 | 158071 |
| 174 | $0.04 | 158620 |
| 175 | $0.04 | 159697 |
| 176 | $0.04 | 160162 |
| 177 | $0.04 | 161480 |
| 178 | $0.04 | 161953 |
| 179 | $0.06 | 165449 |
| 180 | $0.04 | 165836 |
| 181 | $0.04 | 166800 |
| 182 | $0.04 | 167368 |
| 183 | $0.04 | 168736 |
| 184 | $0.07 | 173327 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 12 | 3243 | $0.06 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 11 | 4080 | $0.08 |
| 🟢 Green | 14 | 4105 | $0.08 |
| 🛠️ Refactor | 12 | 3243 | $0.06 |
| 🔎 verify-green | 15 | 4609 | $0.09 |
| 🔎 verify-refactor | 12 | 3243 | $0.06 |
| 🔎 verify-<phase> (revised) | 5 | 2032 | $0.04 |
| 🗺️ Plan | 1 | 504 | $0.01 |
| 🗺️ verify-plan | 2 | 520 | $0.01 |
| ▶️ Resuming | 1 | 7 | $0.00 |
| ⛔ Bailed | 1 | 504 | $0.01 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 46 | 15476 | $0.31 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 2 | 0 | 0 | 28 | 23 | 2 | 4 | 2990 | 8722 | 29933 | 0.11 |
| red | 28 | 13 | 1 | 0 | 925 | 480 | 152 | 290 | 54781 | 2654772 | 542443 | 2.26 |
| green | 45 | 11 | 10 | 0 | 5414 | 848 | 260 | 506 | 83495 | 4451310 | 767504 | 3.94 |
| refactor | 12 | 0 | 0 | 0 | 83 | 53 | 28 | 50 | 4588 | 293459 | 156045 | 0.47 |
| pin | 6 | 6 | 0 | 0 | 228 | 132 | 34 | 66 | 14887 | 565177 | 100890 | 0.46 |
| red-missing | 6 | 0 | 0 | 0 | 228 | 140 | 34 | 66 | 17530 | 621571 | 111615 | 0.52 |
| exhausted | 1 | 0 | 0 | 0 | 61 | 29 | 5 | 10 | 2121 | 76176 | 14295 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 43 | 32 | 11 | 0 | 3065 | 710 | 214 | 412 | 76855 | 3399228 | 615307 | 2.65 |
| developer | claude-sonnet-5-5 | 40 | 0 | 0 | 0 | 1133 | 593 | 199 | 382 | 67617 | 3494531 | 735198 | 2.86 |
| developer | claude-opus-5-5 | 17 | 0 | 0 | 0 | 2769 | 402 | 102 | 198 | 35920 | 1777428 | 372220 | 2.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 137 | 0.39 | 72 | 0.15 |
| green | 6791 | 4.45 | 303 | 0.52 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 36 | 0.08 |
| red-missing | 0 | 0.00 | 34 | 0.11 |
| exhausted | 0 | 0.00 | 61 | 0.13 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `make -C projects/dashboard test` runs pytest over the tests under `projects/dashboard/` and exits with pytest's own exit code (a failing case makes it exit 1, all passing 0); pinned by a case under `projects/dashboard/tests/` that runs that Makefile's `test` target over a one-case tests directory in its `tmp_path`, changing nothing outside `projects/dashboard/` ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 169 | 47 | 90 | 16420 | 845396 | 196341 | 1.00 | 2252 | 1/2 | 0/5 | nothing-left |  |  | full |
| Every case under `projects/dashboard/tests/` runs with `VERI_HOME` pointing at a copy of `fixtures/journal/` inside its own `tmp_path` (the copy holds `3277.jsonl` under `runs/`), never the real `~/.veri`; pinned by a case in a test file other than `projects/dashboard/tests/conftest.py`, which supplies the copy ⟦guard-subject: projects/dashboard/tests/conftest.py⟧ ⟦criterion 5⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 54 | 21 | 42 | 6103 | 330564 | 81079 | 0.30 | 256 | unknown | 0/5 | nothing-left |  |  | full |
| veri's own `make test` collects no case under `projects/dashboard/`; pinned by a case under `projects/dashboard/tests/`, with no file outside `projects/dashboard/` changed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 13 | 24 | 5047 | 232044 | 42934 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| `python3 projects/dashboard/serve.py --repo <path> --port <n>` serves an HTML page answering `GET /` with status 200, using only the Python standard library; pinned by a case that starts it as a real process against the fixture copy ⟦criterion 2⟧ | 15 | 3 | 3 | 0 | 0 | 0 | 241 | 70 | 128 | 25755 | 1057859 | 223349 | 1.27 | 1010 | green 3/2, red 1/2 | 0/5 | nothing-left |  |  | full |
| `serve.py` listens on `127.0.0.1` only: the page is reachable at `127.0.0.1` and the listening socket is bound to no other address ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 66 | 23 | 42 | 7150 | 334670 | 83427 | 0.31 | 218 | unknown | 0/5 | nothing-left |  |  | full |
| `serve.py --repo <path>` with no `--port` still serves the page, on a default port ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 59 | 21 | 40 | 6363 | 317136 | 84475 | 0.31 | 251 | unknown | 0/5 | nothing-left |  |  | full |
| The page's Running section names each run whose journal under `$VERI_HOME/runs/` has no ending event, with its awake wall time (minutes between its first and last journal line's `awake`), as `status.sh --report` prints it for that run ⟦criterion 4⟧ | 17 | 5 | 3 | 0 | 0 | 0 | 288 | 87 | 170 | 32958 | 1541064 | 279330 | 1.18 | 6192 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| The page's Running entry for a run shows its steps done of planned (`step-done` events of the last `plan` event's `steps`), as `status.sh --report` prints them ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 75 | 22 | 44 | 7560 | 370649 | 82411 | 0.32 | 385 | unknown | 0/5 | nothing-left |  |  | full |
| The page's Running entry for a run shows its current phase (the last `launch` event's phase) and that phase's attempt count, as `status.sh --report` prints them ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 70 | 27 | 52 | 7576 | 448382 | 88800 | 0.34 | 318 | unknown | 0/5 | structural-owed |  |  | full |
| The page's Running entry for a run shows its PASS and REJECT verdict counts, as `status.sh --report` prints them ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 81 | 28 | 54 | 8108 | 458441 | 81314 | 0.33 | 318 | unknown | 0/5 | structural-owed |  |  | full |
| The page's Running entry for a run shows its cost in dollars (summed `usage` `total_cost_usd`), as `status.sh --report` prints it ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 81 | 29 | 54 | 8771 | 492087 | 88403 | 0.36 | 321 | unknown | 0/5 | nothing-left |  |  | full |
| The page's Running entry for a run shows its model split (the model per role: developer, verifier, revise), as `status.sh --report` prints it ⟦criterion 4⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 222 | 66 | 130 | 23367 | 1188013 | 173320 | 0.88 | 1156 | 1/2 | 0/5 | structural-owed |  |  | already-satisfied |
| A line appended to a running run's journal shows on the already-open page without a reload (the page fetches fresh Running data from the server and re-renders it) ⟦criterion 4⟧ | 11 | 2 | 2 | 0 | 0 | 0 | 231 | 59 | 118 | 22224 | 1046160 | 187609 | 0.98 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `make -C projects/dashboard test` runs pytest over the tests under `projects/dashboard/` and exits with pytest's own exit code (a failing case makes it exit 1, all passing 0); pinned by a case under `projects/dashboard/tests/` that runs that Makefile's `test` target over a one-case tests directory in its `tmp_path`, changing nothing outside `projects/dashboard/` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |
| Every case under `projects/dashboard/tests/` runs with `VERI_HOME` pointing at a copy of `fixtures/journal/` inside its own `tmp_path` (the copy holds `3277.jsonl` under `runs/`), never the real `~/.veri`; pinned by a case in a test file other than `projects/dashboard/tests/conftest.py`, which supplies the copy ⟦guard-subject: projects/dashboard/tests/conftest.py⟧ ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |
| `python3 projects/dashboard/serve.py --repo <path> --port <n>` serves an HTML page answering `GET /` with status 200, using only the Python standard library; pinned by a case that starts it as a real process against the fixture copy ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| `serve.py` listens on `127.0.0.1` only: the page is reachable at `127.0.0.1` and the listening socket is bound to no other address ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |
| `serve.py --repo <path>` with no `--port` still serves the page, on a default port ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |
| The page's Running section names each run whose journal under `$VERI_HOME/runs/` has no ending event, with its awake wall time (minutes between its first and last journal line's `awake`), as `status.sh --report` prints it for that run ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 14 | 0.08 |
| The page's Running entry for a run shows its steps done of planned (`step-done` events of the last `plan` event's `steps`), as `status.sh --report` prints them ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| The page's Running entry for a run shows its current phase (the last `launch` event's phase) and that phase's attempt count, as `status.sh --report` prints them ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 7 | 0.04 |
| The page's Running entry for a run shows its PASS and REJECT verdict counts, as `status.sh --report` prints them ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 8 | 0.04 |
| The page's Running entry for a run shows its cost in dollars (summed `usage` `total_cost_usd`), as `status.sh --report` prints it ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |
| The page's Running entry for a run shows its model split (the model per role: developer, verifier, revise), as `status.sh --report` prints it ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 7 | 0.04 |

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| `make -C projects/dashboard test` runs pytest over the tests under `projects/dashboard/` and exits with pytest's own exit code (a failing case makes it exit 1, all passing 0); pinned by a case under `projects/dashboard/tests/` that runs that Makefile's `test` target over a one-case tests directory in its `tmp_path`, changing nothing outside `projects/dashboard/` ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| Every case under `projects/dashboard/tests/` runs with `VERI_HOME` pointing at a copy of `fixtures/journal/` inside its own `tmp_path` (the copy holds `3277.jsonl` under `runs/`), never the real `~/.veri`; pinned by a case in a test file other than `projects/dashboard/tests/conftest.py`, which supplies the copy ⟦guard-subject: projects/dashboard/tests/conftest.py⟧ ⟦criterion 5⟧ | 1 | 0 | 1 | nothing-left 1 |
| `python3 projects/dashboard/serve.py --repo <path> --port <n>` serves an HTML page answering `GET /` with status 200, using only the Python standard library; pinned by a case that starts it as a real process against the fixture copy ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| `serve.py` listens on `127.0.0.1` only: the page is reachable at `127.0.0.1` and the listening socket is bound to no other address ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| `serve.py --repo <path>` with no `--port` still serves the page, on a default port ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| The page's Running section names each run whose journal under `$VERI_HOME/runs/` has no ending event, with its awake wall time (minutes between its first and last journal line's `awake`), as `status.sh --report` prints it for that run ⟦criterion 4⟧ | 1 | 0 | 1 | nothing-left 1 |
| The page's Running entry for a run shows its steps done of planned (`step-done` events of the last `plan` event's `steps`), as `status.sh --report` prints them ⟦criterion 4⟧ | 1 | 0 | 1 | nothing-left 1 |
| The page's Running entry for a run shows its current phase (the last `launch` event's phase) and that phase's attempt count, as `status.sh --report` prints them ⟦criterion 4⟧ | 1 | 0 | 1 | structural-owed 1 |
| The page's Running entry for a run shows its PASS and REJECT verdict counts, as `status.sh --report` prints them ⟦criterion 4⟧ | 1 | 0 | 1 | structural-owed 1 |
| The page's Running entry for a run shows its cost in dollars (summed `usage` `total_cost_usd`), as `status.sh --report` prints it ⟦criterion 4⟧ | 1 | 0 | 1 | nothing-left 1 |
| The page's Running entry for a run shows its model split (the model per role: developer, verifier, revise), as `status.sh --report` prints it ⟦criterion 4⟧ | 1 | 0 | 1 | structural-owed 1 |
| issue | 11 | 0 | 11 | nothing-left 8, structural-owed 3 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 1 | 1 | 2 | 870 | 1 | 1 | 0 | 2 | 0 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 198 | 2 | 3 | 3 | 1 | 1 | 0 | 3 | 1 | 1 | 4 | 1 | 4 | 1 | 1 | 19 | 4 | 1 | 4 | 0 | 1 | 1 | 2 | 1 | 0 | 4 | 0 | 2 | 2 | 2 | 2 | 2 | 4 | 1 | 2 | 1 | 1 | 2 | 1 | 2 | 0 | 1 | 1 | 1 | 0 | 2 | 1 | 2 | 1 | 4 | 0 | 1 | 1 | 4 | 4 | 2 | 4 | 1 | 5 | 4 | 1 |  |  |  |  |  |  |  |  |  |
| fast | 19 | 30 | 21 | 20 | 21 | 20 | 19 | 20 | 20 | 21 | 21 | 23 | 24 | 21 | 33 | 19 | 19 | 28 | 20 | 21 | 20 | 22 | 22 | 29 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 24 | 19 | 23 | 23 | 23 | 24 | 24 | 18 | 23 | 18 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 1 | 2 | 2 | 3 | 1 | 1 | 1 | 2 | 3 | 1 | 4 | 1 | 4 | 0 | 0 | 0 | 10 | 10 | 1 | 3 | 3 | 0 | 4 | 1 | 3 | 4 | 0 | 0 | 1 | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 | 1 | 1 | 11 | 2 | 4 | 0 | 0 | 0 | 0 | 1 | 2 | 4 | 1 | 2 | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 515 | 992 | 180392 | 8671187 | 1722725 | 16.89 (estimate) |
