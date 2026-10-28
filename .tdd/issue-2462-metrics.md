### 📊 Metrics — issue 2462

Wall time for the issue: 3562 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 10 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $16.86 over 316 turns, in 5 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88653 tokens, largest 129553 tokens
Conductor context: first turn 88705 tokens, largest 149776 tokens
Conductor context: first turn 88963 tokens, largest 160624 tokens
Conductor context: first turn 89061 tokens, largest 208846 tokens
Conductor context: first turn 89068 tokens, largest 203140 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 88653 |
| 2 | $0.05 | 90489 |
| 3 | $0.04 | 92500 |
| 4 | $0.04 | 92794 |
| 5 | $0.03 | 93261 |
| 6 | $0.04 | 94315 |
| 7 | $0.03 | 94563 |
| 8 | $0.05 | 96320 |
| 9 | $0.07 | 100506 |
| 10 | $0.04 | 101943 |
| 11 | $0.04 | 103143 |
| 12 | $0.11 | 112475 |
| 13 | $0.05 | 114092 |
| 14 | $0.07 | 118385 |
| 15 | $0.05 | 120673 |
| 16 | $0.08 | 125177 |
| 17 | $0.04 | 126192 |
| 18 | $0.05 | 127997 |
| 19 | $0.05 | 129553 |
| 20 | $0.58 | 88705 |
| 21 | $0.03 | 89142 |
| 22 | $0.04 | 90680 |
| 23 | $0.03 | 91306 |
| 24 | $0.05 | 93464 |
| 25 | $0.03 | 94180 |
| 26 | $0.03 | 94662 |
| 27 | $0.04 | 95226 |
| 28 | $0.03 | 96418 |
| 29 | $0.05 | 98577 |
| 30 | $0.04 | 99799 |
| 31 | $0.05 | 102006 |
| 32 | $0.03 | 102894 |
| 33 | $0.04 | 103299 |
| 34 | $0.03 | 104227 |
| 35 | $0.05 | 106176 |
| 36 | $0.03 | 106537 |
| 37 | $0.04 | 107455 |
| 38 | $0.04 | 107970 |
| 39 | $0.03 | 108153 |
| 40 | $0.03 | 108785 |
| 41 | $0.05 | 110037 |
| 42 | $0.03 | 110668 |
| 43 | $0.04 | 111415 |
| 44 | $0.04 | 112075 |
| 45 | $0.03 | 112649 |
| 46 | $0.04 | 112893 |
| 47 | $0.03 | 113542 |
| 48 | $0.04 | 114124 |
| 49 | $0.04 | 114898 |
| 50 | $0.04 | 116306 |
| 51 | $0.10 | 124086 |
| 52 | $0.10 | 132115 |
| 53 | $0.03 | 132448 |
| 54 | $0.05 | 133230 |
| 55 | $0.04 | 134003 |
| 56 | $0.04 | 134454 |
| 57 | $0.04 | 135069 |
| 58 | $0.04 | 135674 |
| 59 | $0.04 | 136352 |
| 60 | $0.05 | 137302 |
| 61 | $0.04 | 138206 |
| 62 | $0.04 | 138897 |
| 63 | $0.05 | 139548 |
| 64 | $0.04 | 140301 |
| 65 | $0.04 | 141077 |
| 66 | $0.05 | 141763 |
| 67 | $0.04 | 142529 |
| 68 | $0.04 | 143180 |
| 69 | $0.07 | 147322 |
| 70 | $0.06 | 148986 |
| 71 | $0.04 | 149776 |
| 72 | $0.59 | 88963 |
| 73 | $0.03 | 89298 |
| 74 | $0.05 | 91625 |
| 75 | $0.04 | 93215 |
| 76 | $0.04 | 93956 |
| 77 | $0.03 | 94657 |
| 78 | $0.03 | 95275 |
| 79 | $0.05 | 97196 |
| 80 | $0.03 | 97428 |
| 81 | $0.03 | 97813 |
| 82 | $0.04 | 98347 |
| 83 | $0.03 | 98869 |
| 84 | $0.04 | 99395 |
| 85 | $0.03 | 99674 |
| 86 | $0.04 | 101191 |
| 87 | $0.04 | 101919 |
| 88 | $0.07 | 106287 |
| 89 | $0.04 | 107533 |
| 90 | $0.04 | 108589 |
| 91 | $0.04 | 109832 |
| 92 | $0.04 | 111005 |
| 93 | $0.05 | 113222 |
| 94 | $0.04 | 114031 |
| 95 | $0.04 | 114634 |
| 96 | $0.04 | 115480 |
| 97 | $0.04 | 116029 |
| 98 | $0.04 | 116722 |
| 99 | $0.10 | 125165 |
| 100 | $0.04 | 126020 |
| 101 | $0.04 | 126609 |
| 102 | $0.04 | 127319 |
| 103 | $0.05 | 128545 |
| 104 | $0.04 | 129425 |
| 105 | $0.04 | 129936 |
| 106 | $0.10 | 137575 |
| 107 | $0.05 | 138968 |
| 108 | $0.04 | 139599 |
| 109 | $0.05 | 140841 |
| 110 | $0.05 | 141530 |
| 111 | $0.05 | 142744 |
| 112 | $0.04 | 143245 |
| 113 | $0.04 | 143841 |
| 114 | $0.05 | 144743 |
| 115 | $0.04 | 145392 |
| 116 | $0.05 | 145735 |
| 117 | $0.05 | 146949 |
| 118 | $0.04 | 147843 |
| 119 | $0.05 | 148578 |
| 120 | $0.05 | 149387 |
| 121 | $0.04 | 150514 |
| 122 | $0.08 | 154566 |
| 123 | $0.08 | 159812 |
| 124 | $0.05 | 160624 |
| 125 | $0.58 | 89061 |
| 126 | $0.03 | 89350 |
| 127 | $0.05 | 91819 |
| 128 | $0.03 | 92082 |
| 129 | $0.04 | 92595 |
| 130 | $0.03 | 93140 |
| 131 | $0.04 | 95009 |
| 132 | $0.04 | 95342 |
| 133 | $0.03 | 95715 |
| 134 | $0.03 | 96167 |
| 135 | $0.03 | 96470 |
| 136 | $0.04 | 97099 |
| 137 | $0.03 | 97460 |
| 138 | $0.06 | 100560 |
| 139 | $0.05 | 103075 |
| 140 | $0.05 | 105762 |
| 141 | $0.06 | 108732 |
| 142 | $0.03 | 109462 |
| 143 | $0.04 | 110239 |
| 144 | $0.04 | 111046 |
| 145 | $0.05 | 113570 |
| 146 | $0.05 | 115267 |
| 147 | $0.05 | 116663 |
| 148 | $0.09 | 124541 |
| 149 | $0.07 | 128030 |
| 150 | $0.05 | 129997 |
| 151 | $0.06 | 133539 |
| 152 | $0.04 | 134014 |
| 153 | $0.05 | 134994 |
| 154 | $0.04 | 135537 |
| 155 | $0.04 | 136056 |
| 156 | $0.04 | 136494 |
| 157 | $0.04 | 136713 |
| 158 | $0.04 | 136932 |
| 159 | $0.05 | 138202 |
| 160 | $0.05 | 139634 |
| 161 | $0.05 | 140510 |
| 162 | $0.04 | 141020 |
| 163 | $0.04 | 141549 |
| 164 | $0.13 | 153146 |
| 165 | $0.05 | 153643 |
| 166 | $0.04 | 154167 |
| 167 | $0.05 | 154586 |
| 168 | $0.05 | 155567 |
| 169 | $0.05 | 157027 |
| 170 | $0.05 | 158302 |
| 171 | $0.05 | 159050 |
| 172 | $0.05 | 159431 |
| 173 | $0.10 | 167099 |
| 174 | $0.05 | 168317 |
| 175 | $0.06 | 169810 |
| 176 | $0.05 | 170671 |
| 177 | $0.05 | 171573 |
| 178 | $0.05 | 172365 |
| 179 | $0.05 | 172958 |
| 180 | $0.06 | 174268 |
| 181 | $0.05 | 174890 |
| 182 | $0.05 | 175751 |
| 183 | $0.06 | 176632 |
| 184 | $0.05 | 177349 |
| 185 | $0.05 | 178316 |
| 186 | $0.06 | 179303 |
| 187 | $0.05 | 180395 |
| 188 | $0.05 | 180860 |
| 189 | $0.07 | 183347 |
| 190 | $0.05 | 183707 |
| 191 | $0.05 | 184699 |
| 192 | $0.06 | 185789 |
| 193 | $0.05 | 186095 |
| 194 | $0.05 | 187003 |
| 195 | $0.06 | 187883 |
| 196 | $0.05 | 188815 |
| 197 | $0.06 | 189188 |
| 198 | $0.05 | 189742 |
| 199 | $0.05 | 190423 |
| 200 | $0.06 | 191220 |
| 201 | $0.05 | 191628 |
| 202 | $0.05 | 192451 |
| 203 | $0.06 | 192678 |
| 204 | $0.05 | 193566 |
| 205 | $0.06 | 194339 |
| 206 | $0.05 | 195246 |
| 207 | $0.06 | 195793 |
| 208 | $0.06 | 197266 |
| 209 | $0.05 | 197724 |
| 210 | $0.07 | 199212 |
| 211 | $0.05 | 199775 |
| 212 | $0.06 | 201221 |
| 213 | $0.06 | 201833 |
| 214 | $0.05 | 202343 |
| 215 | $0.09 | 207002 |
| 216 | $0.06 | 207697 |
| 217 | $0.05 | 207989 |
| 218 | $0.06 | 208846 |
| 219 | $0.57 | 89068 |
| 220 | $0.02 | 89391 |
| 221 | $0.04 | 91865 |
| 222 | $0.02 | 92221 |
| 223 | $0.03 | 93443 |
| 224 | $0.04 | 95552 |
| 225 | $0.05 | 99648 |
| 226 | $0.02 | 99948 |
| 227 | $0.02 | 100288 |
| 228 | $0.02 | 100474 |
| 229 | $0.02 | 100711 |
| 230 | $0.02 | 101015 |
| 231 | $0.03 | 101640 |
| 232 | $0.03 | 103347 |
| 233 | $0.03 | 104293 |
| 234 | $0.18 | 124297 |
| 235 | $0.03 | 125217 |
| 236 | $0.03 | 125963 |
| 237 | $0.03 | 126604 |
| 238 | $0.03 | 126786 |
| 239 | $0.03 | 127473 |
| 240 | $0.04 | 128748 |
| 241 | $0.03 | 129175 |
| 242 | $0.03 | 129702 |
| 243 | $0.03 | 130081 |
| 244 | $0.03 | 130772 |
| 245 | $0.03 | 131038 |
| 246 | $0.03 | 131728 |
| 247 | $0.03 | 132325 |
| 248 | $0.03 | 132897 |
| 249 | $0.03 | 133413 |
| 250 | $0.03 | 134219 |
| 251 | $0.03 | 134724 |
| 252 | $0.03 | 135245 |
| 253 | $0.03 | 135769 |
| 254 | $0.03 | 136474 |
| 255 | $0.03 | 136844 |
| 256 | $0.03 | 137591 |
| 257 | $0.03 | 138230 |
| 258 | $0.03 | 138551 |
| 259 | $0.04 | 139645 |
| 260 | $0.03 | 140450 |
| 261 | $0.04 | 141348 |
| 262 | $0.03 | 141960 |
| 263 | $0.04 | 142940 |
| 264 | $0.04 | 144137 |
| 265 | $0.04 | 145188 |
| 266 | $0.04 | 146542 |
| 267 | $0.05 | 149571 |
| 268 | $0.03 | 149880 |
| 269 | $0.04 | 150598 |
| 270 | $0.03 | 151170 |
| 271 | $0.04 | 151957 |
| 272 | $0.04 | 152622 |
| 273 | $0.04 | 153498 |
| 274 | $0.03 | 153956 |
| 275 | $0.04 | 154721 |
| 276 | $0.04 | 156381 |
| 277 | $0.05 | 159151 |
| 278 | $0.05 | 160927 |
| 279 | $0.04 | 162215 |
| 280 | $0.04 | 163046 |
| 281 | $0.09 | 170736 |
| 282 | $0.05 | 172846 |
| 283 | $0.04 | 173362 |
| 284 | $0.04 | 174002 |
| 285 | $0.04 | 175081 |
| 286 | $0.04 | 176166 |
| 287 | $0.05 | 177534 |
| 288 | $0.05 | 178838 |
| 289 | $0.04 | 179518 |
| 290 | $0.04 | 179899 |
| 291 | $0.05 | 181646 |
| 292 | $0.04 | 182026 |
| 293 | $0.04 | 182602 |
| 294 | $0.05 | 183833 |
| 295 | $0.04 | 184183 |
| 296 | $0.04 | 184982 |
| 297 | $0.04 | 185866 |
| 298 | $0.05 | 187756 |
| 299 | $0.05 | 189223 |
| 300 | $0.05 | 191135 |
| 301 | $0.05 | 192460 |
| 302 | $0.04 | 192803 |
| 303 | $0.05 | 194206 |
| 304 | $0.04 | 194676 |
| 305 | $0.04 | 195176 |
| 306 | $0.05 | 196618 |
| 307 | $0.04 | 196986 |
| 308 | $0.05 | 197877 |
| 309 | $0.04 | 198072 |
| 310 | $0.05 | 199085 |
| 311 | $0.07 | 203140 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 39 | 36 | 5 | 10 | 1987 | 142217 | 37596 | 0.13 |
| red | 22 | 10 | 1 | 0 | 3415 | 444 | 100 | 196 | 44459 | 2994240 | 613627 | 2.59 |
| green | 32 | 7 | 8 | 0 | 2161 | 614 | 169 | 330 | 59203 | 5349410 | 622385 | 3.38 |
| refactor | 7 | 0 | 0 | 0 | 67 | 44 | 20 | 30 | 3240 | 369911 | 140679 | 0.42 |
| exhausted | 2 | 0 | 0 | 0 | 913 | 41 | 8 | 16 | 2852 | 162082 | 100914 | 0.59 |
| red-contradicted | 1 | 0 | 0 | 0 | 41 | 34 | 7 | 14 | 4520 | 249010 | 25182 | 0.13 |
| red-supersede | 1 | 0 | 0 | 0 | 39 | 28 | 7 | 14 | 3518 | 247233 | 24465 | 0.12 |
| pin | 3 | 3 | 0 | 0 | 75 | 45 | 11 | 22 | 4702 | 320398 | 56015 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 30 | 21 | 9 | 0 | 1453 | 470 | 113 | 220 | 41685 | 3196640 | 525218 | 2.05 |
| developer | claude-sonnet-5-5 | 25 | 0 | 0 | 0 | 3771 | 477 | 127 | 238 | 49329 | 3827208 | 671848 | 2.84 |
| developer | claude-opus-5-5 | 14 | 0 | 0 | 0 | 1526 | 339 | 87 | 174 | 33467 | 2810653 | 423797 | 2.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 160 | 0.66 | 40 | 0.16 |
| green | 2366 | 3.57 | 348 | 0.75 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 862 | 0.47 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 39 | 0.12 |
| pin | 0 | 0.00 | 75 | 0.22 |
| verify-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `stale-rows.sh <issue>` (a new `/bin/sh` shim over a new `veri/stale_rows.py`, with a no-argument usage line naming it on stderr and exit 2) grades the rows of each unit whose `### <unit>` heading in the issue's `## Requirements` is directly followed by the line `As is: these rows describe the unit's current text.`, and only those: one parametrized small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py`, driven in-process with `run_cli`, the issue read and the grader faked in-process, over an issue carrying a marked unit and an unmarked unit whose row the fake would fail — when the fake fails the marked row it exits 1 and prints the issue number, the row ID, the unit and the grader's failing line; when the fake passes the marked row it exits 0 and prints no row; in both, the unmarked unit's rows never reach the grader ⟦criterion 1⟧ | 12 | 4 | 1 | 0 | 0 | 0 | 243 | 52 | 98 | 20162 | 1446305 | 312749 | 1.28 | 3631 | 1/2 | 0/5 | nothing-left |  |  | full |
| `stale-rows.sh <issue>` with no argument prints a usage line naming `stale-rows.sh` on stderr and exits 2, which the repo-wide no-argument audit in `skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py` also requires; pinned by a small `run_cli` case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py` ⟦added⟧ ⟦criterion 1⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 97 | 27 | 54 | 7605 | 808227 | 126067 | 0.60 | 382 | 1/2 | 0/5 | nothing-left |  |  | full |
| `stale-rows.sh <issue>` grades through the grader `grade-prose.sh` uses, not a stub: its grading builds that grader's prompt (`grade_prose.prompt`) from the marked unit, the unit's text and its rows, and turns the reply's `BEGIN GRADES` block into the exit (1 on a `FAIL` line, 0 when all `PASS`) and the printed failing lines; a small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py` with only the model call faked in-process at the one wrapper that makes it ⟦added⟧ ⟦criterion 1⟧ | 14 | 3 | 3 | 0 | 0 | 0 | 298 | 74 | 140 | 30284 | 2291396 | 332043 | 1.64 | 335 | 2/2 | 0/5 | nothing-left |  |  | full |
| `stale-rows.sh <issue>` exits 3, prints no row and makes no grader call when the issue has no marked unit: one parametrized small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py`, the issue read and the grader faked in-process, over an issue whose `## Requirements` units all lack the marker line (one with a row the fake would fail) and an issue with no `## Requirements` section ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 19 | 36 | 5199 | 529078 | 93222 | 0.34 | 299 | unknown | 0/5 | nothing-structural |  |  | full |
| `stale-rows.sh <issue>` exits 2 and names the marked unit on stderr when no verdict could be obtained for it (the faked grader answers with no verdict), the issue also carrying an unmarked unit; a small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py`, the issue read and the grader faked in-process ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 54 | 18 | 32 | 5926 | 455914 | 91388 | 0.33 | 302 | unknown | 0/5 | nothing-structural |  |  | full |
| `stale-rows.sh <issue>` grades a marked unit's rows against that unit's text on the repository's default branch, not the working-tree copy: a small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py` whose faked default-branch read and working-tree file hold different text, asserting the text the faked grader receives and the exit it gives are the default branch's | 12 | 3 | 2 | 0 | 0 | 0 | 260 | 66 | 130 | 27628 | 2137823 | 294967 | 1.54 | 960 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| a second `stale-rows.sh` call on an unchanged issue and an unchanged unit makes no grader call and gives the same exit and output as the first, while a change to the marked rows' text, or to the unit's default-branch text, makes one: one small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py` counting grader calls through an in-process spy on the one grading wrapper, the cache kept under the case's `tmp_path` ⟦criterion 3⟧ | 14 | 4 | 3 | 0 | 0 | 0 | 247 | 66 | 132 | 25690 | 2023541 | 332831 | 1.72 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `stale-rows.sh <issue>` (a new `/bin/sh` shim over a new `veri/stale_rows.py`, with a no-argument usage line naming it on stderr and exit 2) grades the rows of each unit whose `### <unit>` heading in the issue's `## Requirements` is directly followed by the line `As is: these rows describe the unit's current text.`, and only those: one parametrized small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py`, driven in-process with `run_cli`, the issue read and the grader faked in-process, over an issue carrying a marked unit and an unmarked unit whose row the fake would fail — when the fake fails the marked row it exits 1 and prints the issue number, the row ID, the unit and the grader's failing line; when the fake passes the marked row it exits 0 and prints no row; in both, the unmarked unit's rows never reach the grader ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 15 | 0.10 |
| `stale-rows.sh <issue>` (a new `/bin/sh` shim over a new `veri/stale_rows.py`, with a no-argument usage line naming it on stderr and exit 2) grades the rows of each unit whose `### <unit>` heading in the issue's `## Requirements` is directly followed by the line `As is: these rows describe the unit's current text.`, and only those: one parametrized small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py`, driven in-process with `run_cli`, the issue read and the grader faked in-process, over an issue carrying a marked unit and an unmarked unit whose row the fake would fail — when the fake fails the marked row it exits 1 and prints the issue number, the row ID, the unit and the grader's failing line; when the fake passes the marked row it exits 0 and prints no row; in both, the unmarked unit's rows never reach the grader ⟦criterion 1⟧ | 2 | 0/5 | nothing-left | skipped | 0 | 15 | 0.10 |
| `stale-rows.sh <issue>` with no argument prints a usage line naming `stale-rows.sh` on stderr and exits 2, which the repo-wide no-argument audit in `skills/tdd/scripts/tests/py/unit/test_missing_argument_cli.py` also requires; pinned by a small `run_cli` case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 13 | 0.05 |
| `stale-rows.sh <issue>` grades through the grader `grade-prose.sh` uses, not a stub: its grading builds that grader's prompt (`grade_prose.prompt`) from the marked unit, the unit's text and its rows, and turns the reply's `BEGIN GRADES` block into the exit (1 on a `FAIL` line, 0 when all `PASS`) and the printed failing lines; a small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py` with only the model call faked in-process at the one wrapper that makes it ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.06 |
| `stale-rows.sh <issue>` exits 3, prints no row and makes no grader call when the issue has no marked unit: one parametrized small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py`, the issue read and the grader faked in-process, over an issue whose `## Requirements` units all lack the marker line (one with a row the fake would fail) and an issue with no `## Requirements` section ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 13 | 0.06 |
| `stale-rows.sh <issue>` exits 2 and names the marked unit on stderr when no verdict could be obtained for it (the faked grader answers with no verdict), the issue also carrying an unmarked unit; a small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py`, the issue read and the grader faked in-process ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 11 | 0.06 |
| `stale-rows.sh <issue>` grades a marked unit's rows against that unit's text on the repository's default branch, not the working-tree copy: a small case in `skills/tdd/scripts/tests/py/unit/test_stale_rows.py` whose faked default-branch read and working-tree file hold different text, asserting the text the faked grader receives and the exit it gives are the default branch's | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.09 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 4 | 5 | 3 | 2 | 3 | 3 | 4 | 3 | 2 | 3 | 4 | 5 | 6 | 3 | 3 | 3 | 3 | 3 | 3 | 66 | 2 | 3 | 2 | 2 | 3 | 3 | 2 | 2 | 4 | 4 | 7 | 5 | 14 | 5 | 4 | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 102 | 3 | 2 | 3 | 3 | 2 | 2 | 3 | 3 | 2 |
| fast | 29 | 29 | 25 | 27 | 33 | 33 | 31 | 37 | 28 | 27 | 28 | 30 | 29 | 27 | 27 | 25 | 27 | 38 | 42 | 36 | 34 | 35 | 41 | 50 | 25 | 25 | 25 | 27 | 24 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 5 | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 327 | 632 | 124481 | 9834501 | 1620863 | 24.44 (estimate) |
