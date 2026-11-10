### 📊 Metrics — issue 3288

Wall time for the issue: 1837 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 8309 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3514.
Lane: ready-for-agent:mu
Suite flakes: skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, skills/tdd/scripts/tests/py/test_verdict_chain.py.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $13.73 over 304 turns, in 5 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78439 tokens, largest 159632 tokens
Conductor context: first turn 78391 tokens, largest 158530 tokens
Conductor context: first turn 78375 tokens, largest 129178 tokens
Conductor context: first turn 78408 tokens, largest 128418 tokens
Conductor context: first turn 78436 tokens, largest 159813 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78439 |
| 2 | $0.07 | 84451 |
| 3 | $0.04 | 85575 |
| 4 | $0.05 | 88228 |
| 5 | $0.05 | 90243 |
| 6 | $0.03 | 90539 |
| 7 | $0.04 | 91241 |
| 8 | $0.03 | 91792 |
| 9 | $0.04 | 92461 |
| 10 | $0.03 | 93114 |
| 11 | $0.04 | 94149 |
| 12 | $0.04 | 94789 |
| 13 | $0.03 | 95456 |
| 14 | $0.04 | 95787 |
| 15 | $0.03 | 96398 |
| 16 | $0.04 | 97217 |
| 17 | $0.04 | 97504 |
| 18 | $0.04 | 98449 |
| 19 | $0.04 | 99774 |
| 20 | $0.04 | 100575 |
| 21 | $0.04 | 101477 |
| 22 | $0.04 | 102579 |
| 23 | $0.03 | 103151 |
| 24 | $0.04 | 103985 |
| 25 | $0.04 | 105002 |
| 26 | $0.05 | 106307 |
| 27 | $0.04 | 106967 |
| 28 | $0.04 | 108636 |
| 29 | $0.07 | 112128 |
| 30 | $0.04 | 113172 |
| 31 | $0.04 | 113685 |
| 32 | $0.04 | 115008 |
| 33 | $0.05 | 116025 |
| 34 | $0.04 | 116896 |
| 35 | $0.04 | 118102 |
| 36 | $0.05 | 118891 |
| 37 | $0.04 | 119448 |
| 38 | $0.04 | 120223 |
| 39 | $0.05 | 122421 |
| 40 | $0.05 | 123739 |
| 41 | $0.05 | 125566 |
| 42 | $0.04 | 125943 |
| 43 | $0.04 | 126814 |
| 44 | $0.05 | 127516 |
| 45 | $0.05 | 128953 |
| 46 | $0.05 | 131028 |
| 47 | $0.05 | 131787 |
| 48 | $0.04 | 132113 |
| 49 | $0.04 | 133106 |
| 50 | $0.05 | 133514 |
| 51 | $0.11 | 142391 |
| 52 | $0.06 | 144914 |
| 53 | $0.04 | 145668 |
| 54 | $0.05 | 146488 |
| 55 | $0.05 | 147913 |
| 56 | $0.06 | 149203 |
| 57 | $0.04 | 149862 |
| 58 | $0.06 | 151566 |
| 59 | $0.05 | 152621 |
| 60 | $0.04 | 152894 |
| 61 | $0.09 | 157660 |
| 62 | $0.05 | 158567 |
| 63 | $0.05 | 159632 |
| 64 | $0.50 | 78391 |
| 65 | $0.07 | 84396 |
| 66 | $0.04 | 85470 |
| 67 | $0.05 | 88986 |
| 68 | $0.07 | 93444 |
| 69 | $0.03 | 93905 |
| 70 | $0.03 | 94492 |
| 71 | $0.04 | 94847 |
| 72 | $0.03 | 95298 |
| 73 | $0.04 | 96199 |
| 74 | $0.03 | 96974 |
| 75 | $0.05 | 99171 |
| 76 | $0.04 | 99980 |
| 77 | $0.03 | 100398 |
| 78 | $0.03 | 100738 |
| 79 | $0.04 | 101504 |
| 80 | $0.04 | 103192 |
| 81 | $0.04 | 104334 |
| 82 | $0.04 | 105055 |
| 83 | $0.04 | 105924 |
| 84 | $0.04 | 106615 |
| 85 | $0.05 | 108673 |
| 86 | $0.04 | 109581 |
| 87 | $0.03 | 110214 |
| 88 | $0.04 | 110954 |
| 89 | $0.04 | 111522 |
| 90 | $0.05 | 114076 |
| 91 | $0.04 | 114988 |
| 92 | $0.05 | 116983 |
| 93 | $0.04 | 117752 |
| 94 | $0.04 | 118098 |
| 95 | $0.04 | 118696 |
| 96 | $0.09 | 125690 |
| 97 | $0.04 | 126366 |
| 98 | $0.04 | 127344 |
| 99 | $0.05 | 128515 |
| 100 | $0.04 | 129748 |
| 101 | $0.05 | 130352 |
| 102 | $0.04 | 131100 |
| 103 | $0.05 | 132695 |
| 104 | $0.04 | 133499 |
| 105 | $0.04 | 134094 |
| 106 | $0.05 | 135287 |
| 107 | $0.05 | 136654 |
| 108 | $0.04 | 137492 |
| 109 | $0.05 | 138255 |
| 110 | $0.05 | 139682 |
| 111 | $0.04 | 140723 |
| 112 | $0.06 | 142306 |
| 113 | $0.04 | 143125 |
| 114 | $0.04 | 143475 |
| 115 | $0.06 | 146148 |
| 116 | $0.06 | 147554 |
| 117 | $0.04 | 148474 |
| 118 | $0.05 | 149580 |
| 119 | $0.05 | 150737 |
| 120 | $0.05 | 151642 |
| 121 | $0.05 | 152418 |
| 122 | $0.04 | 152978 |
| 123 | $0.05 | 153805 |
| 124 | $0.05 | 154440 |
| 125 | $0.06 | 156716 |
| 126 | $0.05 | 157977 |
| 127 | $0.04 | 158530 |
| 128 | $0.49 | 78375 |
| 129 | $0.08 | 84388 |
| 130 | $0.03 | 85494 |
| 131 | $0.04 | 87336 |
| 132 | $0.04 | 89560 |
| 133 | $0.03 | 90107 |
| 134 | $0.04 | 90698 |
| 135 | $0.02 | 91040 |
| 136 | $0.03 | 91415 |
| 137 | $0.03 | 91824 |
| 138 | $0.04 | 92484 |
| 139 | $0.03 | 93285 |
| 140 | $0.06 | 97636 |
| 141 | $0.06 | 101298 |
| 142 | $0.03 | 101966 |
| 143 | $0.03 | 102195 |
| 144 | $0.04 | 102714 |
| 145 | $0.03 | 103482 |
| 146 | $0.03 | 104073 |
| 147 | $0.04 | 104370 |
| 148 | $0.03 | 105060 |
| 149 | $0.03 | 105520 |
| 150 | $0.04 | 106490 |
| 151 | $0.04 | 107531 |
| 152 | $0.15 | 123355 |
| 153 | $0.04 | 123829 |
| 154 | $0.04 | 124167 |
| 155 | $0.04 | 124950 |
| 156 | $0.03 | 125269 |
| 157 | $0.04 | 125545 |
| 158 | $0.03 | 125970 |
| 159 | $0.04 | 126406 |
| 160 | $0.04 | 126714 |
| 161 | $0.04 | 128107 |
| 162 | $0.04 | 128826 |
| 163 | $0.04 | 129178 |
| 164 | $0.50 | 78408 |
| 165 | $0.07 | 84389 |
| 166 | $0.03 | 85441 |
| 167 | $0.04 | 87272 |
| 168 | $0.05 | 89625 |
| 169 | $0.03 | 90246 |
| 170 | $0.05 | 92803 |
| 171 | $0.04 | 94264 |
| 172 | $0.03 | 94709 |
| 173 | $0.03 | 95256 |
| 174 | $0.04 | 95665 |
| 175 | $0.03 | 95986 |
| 176 | $0.03 | 96422 |
| 177 | $0.03 | 97030 |
| 178 | $0.07 | 101403 |
| 179 | $0.03 | 102281 |
| 180 | $0.04 | 102889 |
| 181 | $0.03 | 103487 |
| 182 | $0.04 | 104416 |
| 183 | $0.03 | 104933 |
| 184 | $0.04 | 105750 |
| 185 | $0.04 | 106512 |
| 186 | $0.04 | 107636 |
| 187 | $0.04 | 108832 |
| 188 | $0.03 | 109224 |
| 189 | $0.04 | 109926 |
| 190 | $0.04 | 110592 |
| 191 | $0.03 | 111247 |
| 192 | $0.04 | 112312 |
| 193 | $0.04 | 113218 |
| 194 | $0.04 | 113900 |
| 195 | $0.04 | 114772 |
| 196 | $0.04 | 115676 |
| 197 | $0.04 | 116480 |
| 198 | $0.03 | 116998 |
| 199 | $0.05 | 118300 |
| 200 | $0.04 | 119901 |
| 201 | $0.09 | 125956 |
| 202 | $0.04 | 127568 |
| 203 | $0.04 | 128418 |
| 204 | $0.49 | 78436 |
| 205 | $0.06 | 84495 |
| 206 | $0.03 | 85559 |
| 207 | $0.03 | 87469 |
| 208 | $0.04 | 89789 |
| 209 | $0.02 | 90273 |
| 210 | $0.02 | 90843 |
| 211 | $0.02 | 91129 |
| 212 | $0.02 | 91419 |
| 213 | $0.02 | 91705 |
| 214 | $0.02 | 92312 |
| 215 | $0.05 | 96573 |
| 216 | $0.03 | 98161 |
| 217 | $0.02 | 98688 |
| 218 | $0.02 | 99209 |
| 219 | $0.02 | 99392 |
| 220 | $0.03 | 100083 |
| 221 | $0.03 | 101476 |
| 222 | $0.02 | 102038 |
| 223 | $0.02 | 102320 |
| 224 | $0.03 | 102992 |
| 225 | $0.03 | 103717 |
| 226 | $0.03 | 104412 |
| 227 | $0.03 | 106100 |
| 228 | $0.02 | 106520 |
| 229 | $0.03 | 107175 |
| 230 | $0.03 | 108163 |
| 231 | $0.04 | 110185 |
| 232 | $0.03 | 110605 |
| 233 | $0.03 | 111276 |
| 234 | $0.03 | 111726 |
| 235 | $0.03 | 112443 |
| 236 | $0.03 | 112835 |
| 237 | $0.03 | 113540 |
| 238 | $0.03 | 113839 |
| 239 | $0.03 | 114364 |
| 240 | $0.03 | 115564 |
| 241 | $0.15 | 131383 |
| 242 | $0.03 | 131951 |
| 243 | $0.03 | 132260 |
| 244 | $0.03 | 132769 |
| 245 | $0.04 | 134408 |
| 246 | $0.05 | 136739 |
| 247 | $0.04 | 137896 |
| 248 | $0.04 | 139769 |
| 249 | $0.03 | 140240 |
| 250 | $0.03 | 140537 |
| 251 | $0.03 | 141252 |
| 252 | $0.03 | 141304 |
| 253 | $0.03 | 142080 |
| 254 | $0.04 | 143127 |
| 255 | $0.03 | 143707 |
| 256 | $0.03 | 144059 |
| 257 | $0.03 | 144501 |
| 258 | $0.05 | 147426 |
| 259 | $0.03 | 147873 |
| 260 | $0.03 | 148404 |
| 261 | $0.04 | 149543 |
| 262 | $0.03 | 149707 |
| 263 | $0.03 | 150198 |
| 264 | $0.03 | 150698 |
| 265 | $0.04 | 151959 |
| 266 | $0.04 | 152621 |
| 267 | $0.03 | 153175 |
| 268 | $0.04 | 153819 |
| 269 | $0.04 | 154419 |
| 270 | $0.04 | 155106 |
| 271 | $0.04 | 155727 |
| 272 | $0.04 | 156474 |
| 273 | $0.03 | 156810 |
| 274 | $0.03 | 157096 |
| 275 | $0.04 | 157741 |
| 276 | $0.04 | 158387 |
| 277 | $0.03 | 158439 |
| 278 | $0.04 | 159057 |
| 279 | $0.03 | 159408 |
| 280 | $0.04 | 159813 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 10 | 4925 | $0.10 |
| 🟢 Green | 8 | 3941 | $0.08 |
| 🛠️ Refactor | 3 | 1067 | $0.02 |
| 🔎 verify-green | 7 | 3337 | $0.07 |
| 🔎 verify-refactor | 3 | 1067 | $0.02 |
| 🔎 verify-<phase> (revised) | 4 | 2185 | $0.04 |
| 🗺️ Plan | 2 | 1073 | $0.02 |
| 🗺️ verify-plan | 6 | 2499 | $0.05 |
| ▶️ Resuming | 4 | 1418 | $0.03 |
| ⛔ Bailed | 2 | 1073 | $0.02 |
| ⏹️ Stopped | 1 | 527 | $0.01 |
| Total | 36 | 16446 | $0.33 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 6 | 5 | 1 | 0 | 55 | 42 | 6 | 12 | 5032 | 5350 | 107048 | 0.32 |
| red | 19 | 9 | 2 | 0 | 644 | 362 | 89 | 172 | 33736 | 1592202 | 356030 | 1.77 |
| green | 18 | 3 | 5 | 0 | 1552 | 413 | 113 | 206 | 40833 | 1828265 | 287224 | 1.41 |
| red-missing | 4 | 0 | 0 | 0 | 102 | 82 | 21 | 40 | 9163 | 362198 | 78606 | 0.32 |
| pin | 3 | 1 | 2 | 0 | 53 | 38 | 9 | 18 | 3589 | 123263 | 43739 | 0.16 |
| refactor | 4 | 1 | 0 | 0 | 60 | 25 | 14 | 28 | 2334 | 202224 | 61792 | 0.20 |
| red-contradicted | 2 | 0 | 0 | 0 | 66 | 57 | 13 | 20 | 6018 | 183477 | 38780 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 29 | 19 | 10 | 0 | 1553 | 392 | 102 | 202 | 36576 | 1505322 | 414518 | 1.55 |
| developer | claude-sonnet-5-5 | 22 | 0 | 0 | 0 | 773 | 450 | 132 | 232 | 47716 | 2123877 | 426888 | 1.86 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 206 | 177 | 31 | 62 | 16413 | 667780 | 131813 | 0.94 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 462 | 1.11 | 252 | 0.70 |
| green | 1507 | 1.47 | 471 | 0.39 |
| red-missing | 0 | 0.00 | 57 | 0.17 |
| pin | 0 | 0.00 | 35 | 0.10 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 24 | 0.08 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A conductor log stream of assistant record id m1 with no comment tool_use, a result record, then assistant record id m1 carrying a comment tool_use: the metrics comment-family counts include that later record's comment family (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 115 | 40 | 76 | 12755 | 619519 | 151643 | 0.57 | 641 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| A conductor log stream of assistant id m1, a result record, assistant id m1 in the next session with its own comment tool_use, then a result record: the metrics count the second m1 as a new turn of its own session, counted and priced like any turn (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦criterion 2⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 243 | 62 | 122 | 25589 | 1186275 | 187327 | 1.01 | unknown | 1/2 | unknown | unknown |  |  | full |
| A conductor log stream of assistant id m1, a result record, assistant id m1 in the next session with its own comment tool_use, then a result record: the metrics count the second m1 as a new turn of its own session, counted and priced like any turn; in the same case, a duplicate record of an id still in the open turn (before any result) carrying a comment tool_use merges its names into that one turn, not a new row and not double counted (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦added⟧ ⟦criterion 2⟧ | 18 | 4 | 4 | 0 | 0 | 0 | 427 | 91 | 166 | 36998 | 1407627 | 307069 | 1.59 | 2118 | red 2/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| A conductor log stream of assistant id m1 carrying a Green comment tool_use, a result record, assistant id m1 in the next session carrying a Red comment tool_use, then a result record: the metrics give 2 turn rows, both counted and priced, Green and Red each counted once (today the seen_ids filter applied at each result in metrics.py keeps an id whose turn carried comment names, so the second m1 is dropped as a duplicate and only 1 row is given) (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦added⟧ ⟦criterion 2⟧ | 6 | 1 | 2 | 0 | 0 | 0 | 102 | 31 | 56 | 10774 | 493245 | 109406 | 0.43 | unknown | unknown | unknown | unknown |  |  | full |
| A conductor log stream of assistant id m1 carrying a Green comment tool_use, a result record, assistant id m1 in the next session carrying a Red comment tool_use, a result record, then assistant id m1 in a third session carrying no comment tool_use and a result record: the metrics give 2 turn rows, both counted and priced, Green and Red each counted once — the reused m1 carrying comment names opens a new turn, while the later name-less m1 of the already-flushed id is a duplicate, not a third row (today the seen_ids filter applied at each result in metrics.py keeps an id whose turn carried comment names, so the Red m1 is dropped as a duplicate and only 1 row is given) (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 35 | 64 | 9557 | 584963 | 110726 | 0.43 | 466 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A conductor log stream of assistant record id m1 with no comment tool_use, a result record, then assistant record id m1 carrying a comment tool_use: the metrics comment-family counts include that later record's comment family (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |
| A conductor log stream of assistant id m1, a result record, assistant id m1 in the next session with its own comment tool_use, then a result record: the metrics count the second m1 as a new turn of its own session, counted and priced like any turn; in the same case, a duplicate record of an id still in the open turn (before any result) carrying a comment tool_use merges its names into that one turn, not a new row and not double counted (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.06 |
| A conductor log stream of assistant id m1 carrying a Green comment tool_use, a result record, assistant id m1 in the next session carrying a Red comment tool_use, a result record, then assistant id m1 in a third session carrying no comment tool_use and a result record: the metrics give 2 turn rows, both counted and priced, Green and Red each counted once — the reused m1 carrying comment names opens a new turn, while the later name-less m1 of the already-flushed id is a duplicate, not a third row (today the seen_ids filter applied at each result in metrics.py keeps an id whose turn carried comment names, so the Red m1 is dropped as a duplicate and only 1 row is given) (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦added⟧ ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 48 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| A conductor log stream of assistant record id m1 with no comment tool_use, a result record, then assistant record id m1 carrying a comment tool_use: the metrics comment-family counts include that later record's comment family (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| A conductor log stream of assistant id m1, a result record, assistant id m1 in the next session with its own comment tool_use, then a result record: the metrics count the second m1 as a new turn of its own session, counted and priced like any turn; in the same case, a duplicate record of an id still in the open turn (before any result) carrying a comment tool_use merges its names into that one turn, not a new row and not double counted (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦added⟧ ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| A conductor log stream of assistant id m1 carrying a Green comment tool_use, a result record, assistant id m1 in the next session carrying a Red comment tool_use, a result record, then assistant id m1 in a third session carrying no comment tool_use and a result record: the metrics give 2 turn rows, both counted and priced, Green and Red each counted once — the reused m1 carrying comment names opens a new turn, while the later name-less m1 of the already-flushed id is a duplicate, not a third row (today the seen_ids filter applied at each result in metrics.py keeps an id whose turn carried comment names, so the Red m1 is dropped as a duplicate and only 1 row is given) (a reproduction case in skills/tdd/scripts/tests/py/test_metrics.py, no git, no network) ⟦added⟧ ⟦criterion 2⟧ | 1 | 1 | 0 | nothing-structural 1 |
| issue | 4 | ? | ? | nothing-left 2, nothing-structural 2 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 1 | 3 | 1 | 2 | 5 | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 0 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 4 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 1 | 1 | 1 | 2 |
| fast | 20 | 38 | 22 | 46 | 21 | 20 | 22 | 23 | 22 | 21 | 21 | 18 | 23 | 19 | 25 | 26 | 22 | 21 | 22 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 2 | 1 | 1 | 1 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 265 | 496 | 100705 | 4296979 | 973219 | 18.08 (estimate) |
