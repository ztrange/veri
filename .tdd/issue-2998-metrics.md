### 📊 Metrics — issue 2998

Wall time for the issue: 401 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3001.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.73 over 106 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89824 tokens, largest 180570 tokens
Conductor context: first turn 89848 tokens, largest 124202 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89824 |
| 2 | $0.08 | 96978 |
| 3 | $0.05 | 98872 |
| 4 | $0.04 | 100837 |
| 5 | $0.04 | 102366 |
| 6 | $0.04 | 102805 |
| 7 | $0.03 | 103173 |
| 8 | $0.03 | 103500 |
| 9 | $0.04 | 104015 |
| 10 | $0.04 | 106198 |
| 11 | $0.04 | 107506 |
| 12 | $0.04 | 107857 |
| 13 | $0.04 | 108608 |
| 14 | $0.03 | 109089 |
| 15 | $0.04 | 109747 |
| 16 | $0.03 | 110175 |
| 17 | $0.04 | 111488 |
| 18 | $0.04 | 112379 |
| 19 | $0.05 | 114212 |
| 20 | $0.03 | 114515 |
| 21 | $0.04 | 115224 |
| 22 | $0.04 | 115868 |
| 23 | $0.03 | 116128 |
| 24 | $0.04 | 116850 |
| 25 | $0.04 | 117481 |
| 26 | $0.04 | 118244 |
| 27 | $0.04 | 119118 |
| 28 | $0.03 | 119497 |
| 29 | $0.05 | 120493 |
| 30 | $0.04 | 121212 |
| 31 | $0.03 | 121940 |
| 32 | $0.04 | 122706 |
| 33 | $0.04 | 123068 |
| 34 | $0.05 | 124252 |
| 35 | $0.04 | 125036 |
| 36 | $0.04 | 125769 |
| 37 | $0.04 | 126496 |
| 38 | $0.03 | 126863 |
| 39 | $0.05 | 127825 |
| 40 | $0.06 | 131020 |
| 41 | $0.04 | 131931 |
| 42 | $0.07 | 136369 |
| 43 | $0.05 | 137536 |
| 44 | $0.04 | 138235 |
| 45 | $0.04 | 138883 |
| 46 | $0.04 | 139135 |
| 47 | $0.05 | 140034 |
| 48 | $0.10 | 148728 |
| 49 | $0.05 | 149889 |
| 50 | $0.05 | 150563 |
| 51 | $0.04 | 151345 |
| 52 | $0.05 | 152516 |
| 53 | $0.05 | 153339 |
| 54 | $0.05 | 155046 |
| 55 | $0.05 | 156759 |
| 56 | $0.05 | 156957 |
| 57 | $0.04 | 157381 |
| 58 | $0.05 | 158749 |
| 59 | $0.05 | 159190 |
| 60 | $0.04 | 159965 |
| 61 | $0.05 | 160507 |
| 62 | $0.04 | 160768 |
| 63 | $0.05 | 161591 |
| 64 | $0.05 | 162067 |
| 65 | $0.05 | 163315 |
| 66 | $0.05 | 163967 |
| 67 | $0.04 | 164562 |
| 68 | $0.05 | 165060 |
| 69 | $0.05 | 165808 |
| 70 | $0.04 | 166096 |
| 71 | $0.05 | 166749 |
| 72 | $0.05 | 167265 |
| 73 | $0.04 | 167641 |
| 74 | $0.05 | 168180 |
| 75 | $0.05 | 168403 |
| 76 | $0.04 | 168929 |
| 77 | $0.05 | 169518 |
| 78 | $0.05 | 170119 |
| 79 | $0.06 | 172807 |
| 80 | $0.05 | 173155 |
| 81 | $0.05 | 173849 |
| 82 | $0.05 | 174402 |
| 83 | $0.08 | 179066 |
| 84 | $0.05 | 179762 |
| 85 | $0.05 | 180570 |
| 86 | $0.58 | 89848 |
| 87 | $0.08 | 96998 |
| 88 | $0.03 | 98920 |
| 89 | $0.04 | 101094 |
| 90 | $0.10 | 110506 |
| 91 | $0.05 | 114105 |
| 92 | $0.03 | 115038 |
| 93 | $0.03 | 115294 |
| 94 | $0.05 | 118745 |
| 95 | $0.03 | 119032 |
| 96 | $0.03 | 119533 |
| 97 | $0.03 | 119891 |
| 98 | $0.03 | 120257 |
| 99 | $0.03 | 120931 |
| 100 | $0.03 | 121550 |
| 101 | $0.03 | 122130 |
| 102 | $0.03 | 122595 |
| 103 | $0.03 | 122851 |
| 104 | $0.03 | 123412 |
| 105 | $0.03 | 123876 |
| 106 | $0.03 | 124202 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 6 | 1 | 2 | 715 | 0 | 32612 | 0.09 |
| red | 6 | 2 | 0 | 0 | 726 | 196 | 44 | 88 | 19194 | 1568135 | 235103 | 1.08 |
| green | 6 | 2 | 1 | 0 | 1279 | 82 | 29 | 58 | 7716 | 872038 | 103707 | 0.42 |
| red-missing | 1 | 0 | 0 | 0 | 101 | 27 | 5 | 10 | 3744 | 158923 | 20899 | 0.11 |
| pin | 2 | 1 | 1 | 0 | 164 | 39 | 8 | 16 | 3998 | 208540 | 51538 | 0.19 |
| refactor | 4 | 1 | 0 | 0 | 1251 | 66 | 19 | 38 | 6065 | 613001 | 119052 | 0.63 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 7 | 2 | 0 | 1370 | 151 | 38 | 76 | 13418 | 1056691 | 227333 | 0.81 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 957 | 155 | 43 | 86 | 16631 | 1520644 | 184027 | 0.78 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 1205 | 110 | 25 | 50 | 11383 | 843302 | 151551 | 0.93 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 136 | 0.46 |
| green | 901 | 0.26 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 61 | 0.12 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With the issue's step 1-2 fixture (a format-2 record holding one body: line equal to HEAD's and two stale helpers: lines for TestX, the helper extracted at HEAD), `tests-frozen.sh rerecord-refactored` leaves the record with exactly one helpers: line for TestX, equal to HEAD's helper digest, and `check-earlier` then exits 0 (a process case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 1⟧ | 11 | 4 | 1 | 0 | 1 | 0 | 207 | 55 | 110 | 19832 | 1765467 | 252608 | 1.22 | 5392 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| With the same record shape (one body: line and two stale helpers: lines for one case) and a case that `tests-frozen.sh rerecord-earlier` re-records, the record ends with exactly one helpers: line for that case, equal to HEAD's helper digest (a process case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 119 | 33 | 66 | 12022 | 1152293 | 159684 | 0.63 | 1575 | unknown | 0/5 | nothing-left |  |  | full |
| A record holding two helpers: lines for a case whose body `tests-frozen.sh rerecord-refactored` skips (it writes a `skipped:` line on stderr) is left byte-identical by that rerecord-refactored run (a process case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 3⟧ | 3 | 0 | 1 | 0 | 0 | 0 | 84 | 17 | 34 | 8863 | 502877 | 118007 | 0.58 | unknown | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With the issue's step 1-2 fixture (a format-2 record holding one body: line equal to HEAD's and two stale helpers: lines for TestX, the helper extracted at HEAD), `tests-frozen.sh rerecord-refactored` leaves the record with exactly one helpers: line for TestX, equal to HEAD's helper digest, and `check-earlier` then exits 0 (a process case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 1 | 1238 | 0.56 |
| With the same record shape (one body: line and two stale helpers: lines for one case) and a case that `tests-frozen.sh rerecord-earlier` re-records, the record ends with exactly one helpers: line for that case, equal to HEAD's helper digest (a process case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 13 | 0.06 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s | run 147 s | run 148 s | run 149 s | run 150 s | run 151 s | run 152 s | run 153 s | run 154 s | run 155 s | run 156 s | run 157 s | run 158 s | run 159 s | run 160 s | run 161 s | run 162 s | run 163 s | run 164 s | run 165 s | run 166 s | run 167 s | run 168 s | run 169 s | run 170 s | run 171 s | run 172 s | run 173 s | run 174 s | run 175 s | run 176 s | run 177 s | run 178 s | run 179 s | run 180 s | run 181 s | run 182 s | run 183 s | run 184 s | run 185 s | run 186 s | run 187 s | run 188 s | run 189 s | run 190 s | run 191 s | run 192 s | run 193 s | run 194 s | run 195 s | run 196 s | run 197 s | run 198 s | run 199 s | run 200 s | run 201 s | run 202 s | run 203 s | run 204 s | run 205 s | run 206 s | run 207 s | run 208 s | run 209 s | run 210 s | run 211 s | run 212 s | run 213 s | run 214 s | run 215 s | run 216 s | run 217 s | run 218 s | run 219 s | run 220 s | run 221 s | run 222 s | run 223 s | run 224 s | run 225 s | run 226 s | run 227 s | run 228 s | run 229 s | run 230 s | run 231 s | run 232 s | run 233 s | run 234 s | run 235 s | run 236 s | run 237 s | run 238 s | run 239 s | run 240 s | run 241 s | run 242 s | run 243 s | run 244 s | run 245 s | run 246 s | run 247 s | run 248 s | run 249 s | run 250 s | run 251 s | run 252 s | run 253 s | run 254 s | run 255 s | run 256 s | run 257 s | run 258 s | run 259 s | run 260 s | run 261 s | run 262 s | run 263 s | run 264 s | run 265 s | run 266 s | run 267 s | run 268 s | run 269 s | run 270 s | run 271 s | run 272 s | run 273 s | run 274 s | run 275 s | run 276 s | run 277 s | run 278 s | run 279 s | run 280 s | run 281 s | run 282 s | run 283 s | run 284 s | run 285 s | run 286 s | run 287 s | run 288 s | run 289 s | run 290 s | run 291 s | run 292 s | run 293 s | run 294 s | run 295 s | run 296 s | run 297 s | run 298 s | run 299 s | run 300 s | run 301 s | run 302 s | run 303 s | run 304 s | run 305 s | run 306 s | run 307 s | run 308 s | run 309 s | run 310 s | run 311 s | run 312 s | run 313 s | run 314 s | run 315 s | run 316 s | run 317 s | run 318 s | run 319 s | run 320 s | run 321 s | run 322 s | run 323 s | run 324 s | run 325 s | run 326 s | run 327 s | run 328 s | run 329 s | run 330 s | run 331 s | run 332 s | run 333 s | run 334 s | run 335 s | run 336 s | run 337 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 63 | 12 | 67 | 74 | 69 | 61 | 71 | 63 | 55 | 63 | 67 | 61 | 55 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 98 | 77 | 79 | 80 | 93 | 67 | 67 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 12 | 59 | 9 | 9 | 11 | 12 | 16 | 11 | 12 | 11 | 10 | 10 | 8 | 8 | 8 | 11 | 10 | 10 | 8 | 9 | 9 | 10 | 9 | 12 | 14 | 13 | 14 | 13 | 14 | 13 | 12 | 12 | 15 | 14 | 14 | 15 | 16 | 14 | 10 | 9 | 10 | 10 | 9 | 7 | 6 | 6 | 6 | 7 | 9 | 9 | 9 | 8 | 8 | 7 | 8 | 8 | 7 | 7 | 7 | 8 | 8 | 7 | 7 | 8 | 9 | 8 | 6 | 7 | 8 | 8 | 7 | 7 | 7 | 9 | 9 | 8 | 9 | 10 | 10 | 8 | 8 | 8 | 9 | 8 | 9 | 8 | 10 | 11 | 15 | 13 | 13 | 11 | 10 | 8 | 12 | 9 | 10 | 8 | 8 | 9 | 7 | 5 | 7 | 7 | 7 | 11 | 12 | 10 | 9 | 7 | 7 | 6 | 7 | 7 | 7 | 6 | 8 | 7 | 7 | 5 | 5 | 6 | 6 | 6 | 7 | 7 | 7 | 6 | 6 | 7 | 6 | 7 | 9 | 16 | 7 | 7 | 7 | 6 | 6 | 6 | 6 | 8 | 11 | 12 | 9 | 11 | 10 | 9 | 11 | 10 | 10 | 11 | 9 | 17 | 17 | 15 | 10 | 10 | 10 | 10 | 10 | 11 | 12 | 13 | 10 | 11 | 17 | 19 | 16 | 11 | 9 | 10 | 11 | 10 | 11 | 15 | 15 | 14 | 11 | 11 | 12 | 11 | 11 | 12 | 10 | 13 | 11 | 14 | 11 | 9 | 7 | 8 | 11 | 10 | 8 | 9 | 7 | 7 | 8 | 7 | 6 | 6 | 6 | 6 | 7 | 9 | 8 | 7 | 8 | 8 | 9 | 8 | 11 | 13 | 11 | 12 | 11 | 11 | 9 | 9 | 10 | 9 | 8 | 10 | 10 | 9 | 9 | 9 | 9 | 10 | 10 | 11 | 7 | 6 | 7 | 7 | 8 | 10 | 10 | 11 | 9 | 10 | 10 | 9 | 9 | 10 | 8 | 10 | 10 | 9 | 7 | 8 | 8 | 9 | 8 | 9 | 8 | 8 | 7 | 8 | 11 | 9 | 10 | 9 | 8 | 8 | 5 | 5 | 5 | 6 | 5 | 6 | 6 | 7 | 8 | 8 | 6 | 5 | 6 | 6 | 6 | 6 | 9 | 11 | 10 | 10 | 9 | 9 | 9 | 9 | 9 | 8 | 8 | 9 | 9 | 10 | 8 | 9 | 8 | 10 | 10 | 8 | 7 | 7 | 7 | 8 | 7 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 11 | 10 | 11 | 12 | 12 | 12 | 9 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 8 | 9 | 8 | 8 | 8 | 6 | 7 | 9 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 106 | 212 | 41432 | 3420637 | 562911 | 8.25 (estimate) |
