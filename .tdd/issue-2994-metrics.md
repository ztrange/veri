### 📊 Metrics — issue 2994

Wall time for the issue: 1598 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3014.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $9.52 over 121 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89713 tokens, largest 164397 tokens
Conductor context: first turn 164896 tokens, largest 193418 tokens
Conductor context: first turn 90283 tokens, largest 143918 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 89713 |
| 2 | $0.08 | 96869 |
| 3 | $0.04 | 98669 |
| 4 | $0.05 | 100274 |
| 5 | $0.03 | 100887 |
| 6 | $0.04 | 101359 |
| 7 | $0.03 | 101702 |
| 8 | $0.03 | 102038 |
| 9 | $0.04 | 102636 |
| 10 | $0.04 | 104921 |
| 11 | $0.06 | 107551 |
| 12 | $0.03 | 107772 |
| 13 | $0.04 | 109070 |
| 14 | $0.04 | 109357 |
| 15 | $0.03 | 110144 |
| 16 | $0.04 | 110680 |
| 17 | $0.04 | 111357 |
| 18 | $0.03 | 111823 |
| 19 | $0.13 | 124043 |
| 20 | $0.04 | 124854 |
| 21 | $0.05 | 125634 |
| 22 | $0.03 | 126044 |
| 23 | $0.06 | 129109 |
| 24 | $0.04 | 129897 |
| 25 | $0.06 | 131947 |
| 26 | $0.04 | 132391 |
| 27 | $0.04 | 132941 |
| 28 | $0.04 | 133688 |
| 29 | $0.06 | 136082 |
| 30 | $0.04 | 136988 |
| 31 | $0.04 | 137930 |
| 32 | $0.09 | 143573 |
| 33 | $0.04 | 144646 |
| 34 | $0.05 | 145256 |
| 35 | $0.05 | 146454 |
| 36 | $0.05 | 147637 |
| 37 | $0.04 | 148515 |
| 38 | $0.05 | 149507 |
| 39 | $0.05 | 150312 |
| 40 | $0.04 | 151147 |
| 41 | $0.05 | 151805 |
| 42 | $0.05 | 152853 |
| 43 | $0.05 | 154965 |
| 44 | $0.05 | 155798 |
| 45 | $0.05 | 156807 |
| 46 | $0.05 | 158098 |
| 47 | $0.05 | 158808 |
| 48 | $0.05 | 159530 |
| 49 | $0.04 | 159916 |
| 50 | $0.05 | 160841 |
| 51 | $0.07 | 164040 |
| 52 | $0.04 | 164397 |
| 53 | $0.17 | 164896 |
| 54 | $0.22 | 170312 |
| 55 | $0.18 | 172064 |
| 56 | $0.18 | 172645 |
| 57 | $0.17 | 173083 |
| 58 | $0.18 | 173881 |
| 59 | $0.18 | 174543 |
| 60 | $0.17 | 174785 |
| 61 | $0.18 | 175619 |
| 62 | $0.18 | 176868 |
| 63 | $0.19 | 178380 |
| 64 | $0.18 | 179591 |
| 65 | $0.18 | 180662 |
| 66 | $0.18 | 181232 |
| 67 | $0.18 | 182549 |
| 68 | $0.18 | 183845 |
| 69 | $0.19 | 185376 |
| 70 | $0.18 | 185607 |
| 71 | $0.17 | 185838 |
| 72 | $0.18 | 186069 |
| 73 | $0.18 | 186589 |
| 74 | $0.21 | 191248 |
| 75 | $0.18 | 192450 |
| 76 | $0.18 | 193418 |
| 77 | $0.58 | 90283 |
| 78 | $0.08 | 97530 |
| 79 | $0.03 | 99386 |
| 80 | $0.03 | 101264 |
| 81 | $0.02 | 101672 |
| 82 | $0.06 | 106371 |
| 83 | $0.02 | 106477 |
| 84 | $0.04 | 108677 |
| 85 | $0.05 | 112638 |
| 86 | $0.03 | 113053 |
| 87 | $0.03 | 113524 |
| 88 | $0.03 | 113934 |
| 89 | $0.03 | 114395 |
| 90 | $0.03 | 115155 |
| 91 | $0.03 | 116442 |
| 92 | $0.03 | 117194 |
| 93 | $0.05 | 120564 |
| 94 | $0.03 | 121540 |
| 95 | $0.04 | 122929 |
| 96 | $0.03 | 123709 |
| 97 | $0.04 | 125804 |
| 98 | $0.04 | 127318 |
| 99 | $0.03 | 128124 |
| 100 | $0.03 | 128646 |
| 101 | $0.03 | 129249 |
| 102 | $0.03 | 129754 |
| 103 | $0.03 | 130457 |
| 104 | $0.03 | 131183 |
| 105 | $0.03 | 131834 |
| 106 | $0.03 | 132872 |
| 107 | $0.05 | 135809 |
| 108 | $0.03 | 136529 |
| 109 | $0.03 | 136824 |
| 110 | $0.03 | 137474 |
| 111 | $0.03 | 138248 |
| 112 | $0.04 | 139454 |
| 113 | $0.03 | 140162 |
| 114 | $0.04 | 141338 |
| 115 | $0.03 | 141885 |
| 116 | $0.03 | 142185 |
| 117 | $0.03 | 142628 |
| 118 | $0.03 | 143008 |
| 119 | $0.03 | 143291 |
| 120 | $0.03 | 143602 |
| 121 | $0.03 | 143918 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 8 | 1 | 2 | 807 | 0 | 32449 | 0.09 |
| red | 9 | 2 | 1 | 0 | 746 | 321 | 54 | 108 | 27466 | 1791823 | 302087 | 1.40 |
| green | 5 | 1 | 1 | 0 | 1496 | 165 | 42 | 84 | 11867 | 1362876 | 135815 | 0.59 |
| pin | 3 | 3 | 0 | 0 | 120 | 66 | 12 | 24 | 4445 | 324559 | 66863 | 0.24 |
| refactor | 3 | 0 | 0 | 1 | 1843 | 20 | 4 | 8 | 328 | 80913 | 48850 | 0.13 |
| reconcile | 1 | 0 | 0 | 0 | 26 | 16 | 4 | 8 | 759 | 113488 | 42098 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 7 | 2 | 0 | 1137 | 184 | 35 | 70 | 13059 | 923863 | 220657 | 0.77 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 1 | 3107 | 412 | 82 | 164 | 32613 | 2749796 | 407505 | 1.82 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 565 | 1.04 | 0 | 0.00 |
| green | 1496 | 0.59 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| reconcile | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| rerecord-rebased over an earlier step's record naming a case absent both at HEAD and at the pre-rebase sha (never committed on the branch) exits 0 or 3, not 2, and afterwards the record names neither that case's body line nor its helpers line (a process case with real git, in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 1⟧ | 17 | 4 | 2 | 1 | 1 | 0 | 438 | 89 | 178 | 31529 | 2745438 | 464655 | 1.95 | 71753 | red 1/2, refactor 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| rerecord-rebased over a record naming one never-committed case beside other recorded cases keeps every other case's lines and still re-records an upstream-only-changed one as before, while dropping only the never-committed case (a process case with real git) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 11 | 22 | 5056 | 350591 | 81892 | 0.29 | unknown | unknown | unknown | unknown |  |  | pin |
| rerecord-rebased over a record naming a case present at the pre-rebase sha but absent at HEAD (committed, then removed) still exits 2 with the existing "record <path> names case <case>, which <file> does not hold at HEAD" message (a process case with real git) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 16 | 32 | 8280 | 577630 | 49166 | 0.26 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| rerecord-rebased over an earlier step's record naming a case absent both at HEAD and at the pre-rebase sha (never committed on the branch) exits 0 or 3, not 2, and afterwards the record names neither that case's body line nor its helpers line (a process case with real git, in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 1 | 1843 | 0.13 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s | run 147 s | run 148 s | run 149 s | run 150 s | run 151 s | run 152 s | run 153 s | run 154 s | run 155 s | run 156 s | run 157 s | run 158 s | run 159 s | run 160 s | run 161 s | run 162 s | run 163 s | run 164 s | run 165 s | run 166 s | run 167 s | run 168 s | run 169 s | run 170 s | run 171 s | run 172 s | run 173 s | run 174 s | run 175 s | run 176 s | run 177 s | run 178 s | run 179 s | run 180 s | run 181 s | run 182 s | run 183 s | run 184 s | run 185 s | run 186 s | run 187 s | run 188 s | run 189 s | run 190 s | run 191 s | run 192 s | run 193 s | run 194 s | run 195 s | run 196 s | run 197 s | run 198 s | run 199 s | run 200 s | run 201 s | run 202 s | run 203 s | run 204 s | run 205 s | run 206 s | run 207 s | run 208 s | run 209 s | run 210 s | run 211 s | run 212 s | run 213 s | run 214 s | run 215 s | run 216 s | run 217 s | run 218 s | run 219 s | run 220 s | run 221 s | run 222 s | run 223 s | run 224 s | run 225 s | run 226 s | run 227 s | run 228 s | run 229 s | run 230 s | run 231 s | run 232 s | run 233 s | run 234 s | run 235 s | run 236 s | run 237 s | run 238 s | run 239 s | run 240 s | run 241 s | run 242 s | run 243 s | run 244 s | run 245 s | run 246 s | run 247 s | run 248 s | run 249 s | run 250 s | run 251 s | run 252 s | run 253 s | run 254 s | run 255 s | run 256 s | run 257 s | run 258 s | run 259 s | run 260 s | run 261 s | run 262 s | run 263 s | run 264 s | run 265 s | run 266 s | run 267 s | run 268 s | run 269 s | run 270 s | run 271 s | run 272 s | run 273 s | run 274 s | run 275 s | run 276 s | run 277 s | run 278 s | run 279 s | run 280 s | run 281 s | run 282 s | run 283 s | run 284 s | run 285 s | run 286 s | run 287 s | run 288 s | run 289 s | run 290 s | run 291 s | run 292 s | run 293 s | run 294 s | run 295 s | run 296 s | run 297 s | run 298 s | run 299 s | run 300 s | run 301 s | run 302 s | run 303 s | run 304 s | run 305 s | run 306 s | run 307 s | run 308 s | run 309 s | run 310 s | run 311 s | run 312 s | run 313 s | run 314 s | run 315 s | run 316 s | run 317 s | run 318 s | run 319 s | run 320 s | run 321 s | run 322 s | run 323 s | run 324 s | run 325 s | run 326 s | run 327 s | run 328 s | run 329 s | run 330 s | run 331 s | run 332 s | run 333 s | run 334 s | run 335 s | run 336 s | run 337 s | run 338 s | run 339 s | run 340 s | run 341 s | run 342 s | run 343 s | run 344 s | run 345 s | run 346 s | run 347 s | run 348 s | run 349 s | run 350 s | run 351 s | run 352 s | run 353 s | run 354 s | run 355 s | run 356 s | run 357 s | run 358 s | run 359 s | run 360 s | run 361 s | run 362 s | run 363 s | run 364 s | run 365 s | run 366 s | run 367 s | run 368 s | run 369 s | run 370 s | run 371 s | run 372 s | run 373 s | run 374 s | run 375 s | run 376 s | run 377 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 63 | 11 | 9 | 9 | 59 | 61 | 68 | 64 | 65 | 6 | 26 | 29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 66 | 66 | 74 | 90 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 11 | 9 | 9 | 10 | 8 | 11 | 7 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 11 | 8 | 8 | 6 | 7 | 7 | 6 | 9 | 9 | 8 | 8 | 10 | 9 | 9 | 10 | 9 | 10 | 8 | 8 | 8 | 8 | 8 | 7 | 6 | 8 | 8 | 9 | 7 | 7 | 7 | 7 | 7 | 8 | 10 | 9 | 8 | 8 | 9 | 8 | 9 | 7 | 9 | 9 | 10 | 9 | 10 | 7 | 7 | 6 | 7 | 6 | 7 | 7 | 10 | 12 | 8 | 9 | 8 | 11 | 9 | 8 | 8 | 8 | 10 | 9 | 7 | 7 | 7 | 7 | 8 | 8 | 11 | 11 | 9 | 11 | 11 | 9 | 7 | 8 | 7 | 8 | 8 | 8 | 9 | 8 | 8 | 8 | 8 | 8 | 9 | 10 | 9 | 7 | 8 | 8 | 8 | 8 | 11 | 10 | 12 | 11 | 12 | 11 | 11 | 10 | 10 | 10 | 12 | 12 | 12 | 9 | 8 | 9 | 7 | 8 | 7 | 8 | 8 | 9 | 8 | 9 | 8 | 8 | 10 | 11 | 8 | 8 | 10 | 7 | 7 | 8 | 11 | 8 | 9 | 6 | 7 | 6 | 8 | 7 | 8 | 8 | 8 | 11 | 9 | 7 | 11 | 8 | 8 | 7 | 10 | 10 | 12 | 11 | 11 | 10 | 13 | 9 | 12 | 10 | 14 | 16 | 12 | 11 | 11 | 10 | 10 | 11 | 14 | 14 | 12 | 8 | 7 | 7 | 8 | 9 | 9 | 14 | 13 | 12 | 11 | 11 | 11 | 10 | 9 | 10 | 10 | 12 | 12 | 13 | 12 | 16 | 20 | 27 | 31 | 22 | 20 | 15 | 15 | 14 | 12 | 12 | 11 | 14 | 15 | 16 | 13 | 13 | 14 | 14 | 14 | 17 | 17 | 17 | 15 | 17 | 20 | 19 | 28 | 23 | 18 | 24 | 24 | 27 | 20 | 21 | 23 | 35 | 54 | 23 | 27 | 18 | 27 | 22 | 17 | 23 | 20 | 48 | 20 | 21 | 41 | 53 | 26 | 33 | 57 | 26 | 68 | 47 | 14 | 25 | 16 | 15 | 25 | 12 | 23 | 15 | 14 | 23 | 14 | 16 | 27 | 14 | 24 | 13 | 13 | 15 | 24 | 14 | 12 | 20 | 10 | 23 | 13 | 13 | 24 | 14 | 12 | 24 | 19 | 19 | 19 | 19 | 18 | 18 | 17 | 20 | 19 | 19 | 16 | 17 | 19 | 18 | 18 | 16 | 17 | 16 | 16 | 18 | 16 | 16 | 16 | 17 | 16 | 4 | 5 | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 5 | 4 | 3 | 4 | 3 | 4 | 3 | 4 | 4 | 4 | 4 | 4 | 5 | 6 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 6 | 6 | 5 | 6 | 5 | 7 | 6 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 6 | 7 | 7 | 7 | 5 | 6 | 3 | 3 | 4 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 117 | 234 | 45672 | 3673659 | 628162 | 12.11 (estimate) |
