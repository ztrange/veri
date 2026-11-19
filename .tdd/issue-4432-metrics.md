### 📊 Metrics — issue 4432

Wall time for the issue: 1958 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 21 planned.
Outcome: the run bailed — revise-impossible, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $17.45 over 316 turns, in 7 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86835 tokens, largest 156842 tokens
Conductor context: first turn 86793 tokens, largest 159754 tokens
Conductor context: first turn 87423 tokens, largest 152556 tokens
Conductor context: first turn 87424 tokens, largest 160278 tokens
Conductor context: first turn 87422 tokens, largest 153334 tokens
Conductor context: first turn 87423 tokens, largest 129135 tokens
Conductor context: first turn 87469 tokens, largest 163533 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 86835 |
| 2 | $0.05 | 89136 |
| 3 | $0.04 | 90383 |
| 4 | $0.05 | 92149 |
| 5 | $0.05 | 94552 |
| 6 | $0.04 | 95203 |
| 7 | $0.15 | 110214 |
| 8 | $0.07 | 114709 |
| 9 | $0.05 | 115631 |
| 10 | $0.08 | 121559 |
| 11 | $0.05 | 122795 |
| 12 | $0.05 | 124805 |
| 13 | $0.06 | 126820 |
| 14 | $0.04 | 127607 |
| 15 | $0.06 | 129901 |
| 16 | $0.06 | 132032 |
| 17 | $0.07 | 136448 |
| 18 | $0.05 | 137437 |
| 19 | $0.06 | 139614 |
| 20 | $0.06 | 141312 |
| 21 | $0.05 | 143264 |
| 22 | $0.05 | 143594 |
| 23 | $0.06 | 146343 |
| 24 | $0.06 | 147645 |
| 25 | $0.06 | 150853 |
| 26 | $0.07 | 153730 |
| 27 | $0.05 | 154688 |
| 28 | $0.06 | 155802 |
| 29 | $0.04 | 156265 |
| 30 | $0.05 | 156842 |
| 31 | $0.57 | 86793 |
| 32 | $0.04 | 88898 |
| 33 | $0.03 | 89220 |
| 34 | $0.03 | 89888 |
| 35 | $0.06 | 93180 |
| 36 | $0.07 | 98764 |
| 37 | $0.04 | 100119 |
| 38 | $0.04 | 101258 |
| 39 | $0.05 | 103453 |
| 40 | $0.03 | 104177 |
| 41 | $0.03 | 104549 |
| 42 | $0.04 | 104780 |
| 43 | $0.03 | 105151 |
| 44 | $0.04 | 105811 |
| 45 | $0.03 | 106358 |
| 46 | $0.04 | 106974 |
| 47 | $0.04 | 108740 |
| 48 | $0.04 | 109246 |
| 49 | $0.03 | 109631 |
| 50 | $0.13 | 122308 |
| 51 | $0.13 | 133849 |
| 52 | $0.04 | 134446 |
| 53 | $0.04 | 135095 |
| 54 | $0.05 | 136314 |
| 55 | $0.04 | 136502 |
| 56 | $0.04 | 136953 |
| 57 | $0.04 | 137540 |
| 58 | $0.04 | 138405 |
| 59 | $0.05 | 139295 |
| 60 | $0.04 | 139758 |
| 61 | $0.04 | 140594 |
| 62 | $0.04 | 141215 |
| 63 | $0.05 | 142098 |
| 64 | $0.04 | 142629 |
| 65 | $0.05 | 143747 |
| 66 | $0.05 | 145024 |
| 67 | $0.04 | 145543 |
| 68 | $0.04 | 146439 |
| 69 | $0.06 | 148182 |
| 70 | $0.05 | 149552 |
| 71 | $0.04 | 150084 |
| 72 | $0.04 | 150757 |
| 73 | $0.06 | 152318 |
| 74 | $0.04 | 153353 |
| 75 | $0.09 | 158620 |
| 76 | $0.05 | 159754 |
| 77 | $0.56 | 87423 |
| 78 | $0.05 | 89720 |
| 79 | $0.03 | 90350 |
| 80 | $0.05 | 94062 |
| 81 | $0.13 | 106396 |
| 82 | $0.03 | 106942 |
| 83 | $0.04 | 108304 |
| 84 | $0.04 | 109426 |
| 85 | $0.04 | 110187 |
| 86 | $0.04 | 111339 |
| 87 | $0.04 | 112266 |
| 88 | $0.03 | 112593 |
| 89 | $0.05 | 115523 |
| 90 | $0.04 | 116200 |
| 91 | $0.04 | 116748 |
| 92 | $0.03 | 117448 |
| 93 | $0.04 | 117884 |
| 94 | $0.03 | 118372 |
| 95 | $0.06 | 121422 |
| 96 | $0.04 | 122403 |
| 97 | $0.06 | 125694 |
| 98 | $0.04 | 126149 |
| 99 | $0.08 | 132855 |
| 100 | $0.08 | 137733 |
| 101 | $0.04 | 138240 |
| 102 | $0.04 | 139495 |
| 103 | $0.04 | 139719 |
| 104 | $0.04 | 140063 |
| 105 | $0.04 | 141016 |
| 106 | $0.05 | 142010 |
| 107 | $0.04 | 142671 |
| 108 | $0.04 | 143402 |
| 109 | $0.05 | 144339 |
| 110 | $0.04 | 145119 |
| 111 | $0.04 | 145880 |
| 112 | $0.05 | 146894 |
| 113 | $0.05 | 148198 |
| 114 | $0.04 | 149219 |
| 115 | $0.06 | 151841 |
| 116 | $0.05 | 152556 |
| 117 | $0.56 | 87424 |
| 118 | $0.05 | 89723 |
| 119 | $0.03 | 90151 |
| 120 | $0.06 | 94920 |
| 121 | $0.08 | 100987 |
| 122 | $0.03 | 101343 |
| 123 | $0.07 | 105733 |
| 124 | $0.05 | 108402 |
| 125 | $0.04 | 109330 |
| 126 | $0.03 | 110097 |
| 127 | $0.04 | 110388 |
| 128 | $0.05 | 112618 |
| 129 | $0.03 | 113128 |
| 130 | $0.04 | 114006 |
| 131 | $0.04 | 114863 |
| 132 | $0.05 | 117074 |
| 133 | $0.04 | 118465 |
| 134 | $0.04 | 119528 |
| 135 | $0.04 | 120271 |
| 136 | $0.04 | 121178 |
| 137 | $0.04 | 122217 |
| 138 | $0.04 | 122843 |
| 139 | $0.04 | 123233 |
| 140 | $0.04 | 123691 |
| 141 | $0.03 | 124052 |
| 142 | $0.04 | 124561 |
| 143 | $0.04 | 125275 |
| 144 | $0.04 | 125943 |
| 145 | $0.04 | 127044 |
| 146 | $0.04 | 127689 |
| 147 | $0.04 | 128139 |
| 148 | $0.04 | 128847 |
| 149 | $0.04 | 129207 |
| 150 | $0.04 | 129651 |
| 151 | $0.05 | 132365 |
| 152 | $0.05 | 133602 |
| 153 | $0.04 | 134069 |
| 154 | $0.05 | 136218 |
| 155 | $0.05 | 137815 |
| 156 | $0.04 | 138718 |
| 157 | $0.05 | 139991 |
| 158 | $0.04 | 140943 |
| 159 | $0.05 | 141977 |
| 160 | $0.10 | 149501 |
| 161 | $0.04 | 150259 |
| 162 | $0.04 | 150483 |
| 163 | $0.05 | 151331 |
| 164 | $0.05 | 152558 |
| 165 | $0.05 | 153794 |
| 166 | $0.05 | 154839 |
| 167 | $0.04 | 155586 |
| 168 | $0.05 | 157012 |
| 169 | $0.06 | 159591 |
| 170 | $0.05 | 160278 |
| 171 | $0.56 | 87422 |
| 172 | $0.03 | 87611 |
| 173 | $0.03 | 88245 |
| 174 | $0.09 | 96363 |
| 175 | $0.03 | 97220 |
| 176 | $0.04 | 98262 |
| 177 | $0.06 | 102965 |
| 178 | $0.05 | 106244 |
| 179 | $0.04 | 107090 |
| 180 | $0.04 | 108680 |
| 181 | $0.03 | 109235 |
| 182 | $0.04 | 110068 |
| 183 | $0.03 | 110644 |
| 184 | $0.03 | 110806 |
| 185 | $0.04 | 111427 |
| 186 | $0.03 | 112297 |
| 187 | $0.04 | 112459 |
| 188 | $0.03 | 113048 |
| 189 | $0.03 | 113700 |
| 190 | $0.04 | 113931 |
| 191 | $0.08 | 120469 |
| 192 | $0.03 | 121084 |
| 193 | $0.04 | 121326 |
| 194 | $0.03 | 121481 |
| 195 | $0.03 | 121683 |
| 196 | $0.04 | 121865 |
| 197 | $0.03 | 122009 |
| 198 | $0.04 | 122733 |
| 199 | $0.03 | 123229 |
| 200 | $0.04 | 124184 |
| 201 | $0.04 | 124521 |
| 202 | $0.04 | 125311 |
| 203 | $0.03 | 125780 |
| 204 | $0.04 | 126506 |
| 205 | $0.04 | 127805 |
| 206 | $0.04 | 128658 |
| 207 | $0.04 | 128988 |
| 208 | $0.03 | 129433 |
| 209 | $0.04 | 130291 |
| 210 | $0.04 | 130796 |
| 211 | $0.04 | 131617 |
| 212 | $0.04 | 132046 |
| 213 | $0.04 | 132711 |
| 214 | $0.03 | 133252 |
| 215 | $0.04 | 133993 |
| 216 | $0.04 | 134739 |
| 217 | $0.05 | 136107 |
| 218 | $0.04 | 136647 |
| 219 | $0.04 | 137971 |
| 220 | $0.05 | 139490 |
| 221 | $0.04 | 140505 |
| 222 | $0.04 | 141199 |
| 223 | $0.05 | 142149 |
| 224 | $0.04 | 142584 |
| 225 | $0.04 | 143896 |
| 226 | $0.07 | 148488 |
| 227 | $0.05 | 149372 |
| 228 | $0.04 | 149823 |
| 229 | $0.04 | 150135 |
| 230 | $0.06 | 152688 |
| 231 | $0.04 | 153334 |
| 232 | $0.56 | 87423 |
| 233 | $0.05 | 89744 |
| 234 | $0.03 | 90356 |
| 235 | $0.09 | 99262 |
| 236 | $0.04 | 100224 |
| 237 | $0.04 | 101857 |
| 238 | $0.04 | 102824 |
| 239 | $0.03 | 103347 |
| 240 | $0.03 | 104182 |
| 241 | $0.04 | 105200 |
| 242 | $0.04 | 106082 |
| 243 | $0.04 | 107471 |
| 244 | $0.05 | 110155 |
| 245 | $0.03 | 110761 |
| 246 | $0.07 | 115149 |
| 247 | $0.03 | 115840 |
| 248 | $0.04 | 116140 |
| 249 | $0.03 | 116791 |
| 250 | $0.05 | 118113 |
| 251 | $0.03 | 118350 |
| 252 | $0.03 | 118585 |
| 253 | $0.04 | 119002 |
| 254 | $0.03 | 119485 |
| 255 | $0.04 | 120221 |
| 256 | $0.09 | 127343 |
| 257 | $0.04 | 128219 |
| 258 | $0.04 | 129135 |
| 259 | $0.55 | 87469 |
| 260 | $0.02 | 87742 |
| 261 | $0.06 | 92727 |
| 262 | $0.04 | 95766 |
| 263 | $0.06 | 101218 |
| 264 | $0.03 | 102546 |
| 265 | $0.05 | 106352 |
| 266 | $0.03 | 107469 |
| 267 | $0.03 | 108586 |
| 268 | $0.07 | 114234 |
| 269 | $0.03 | 114553 |
| 270 | $0.03 | 116030 |
| 271 | $0.03 | 117347 |
| 272 | $0.05 | 120457 |
| 273 | $0.03 | 121231 |
| 274 | $0.03 | 121531 |
| 275 | $0.03 | 122374 |
| 276 | $0.03 | 123301 |
| 277 | $0.03 | 124468 |
| 278 | $0.03 | 125102 |
| 279 | $0.03 | 125470 |
| 280 | $0.03 | 125930 |
| 281 | $0.03 | 126190 |
| 282 | $0.03 | 126648 |
| 283 | $0.03 | 127118 |
| 284 | $0.06 | 130939 |
| 285 | $0.03 | 131692 |
| 286 | $0.03 | 132257 |
| 287 | $0.03 | 132528 |
| 288 | $0.03 | 132810 |
| 289 | $0.03 | 133058 |
| 290 | $0.03 | 133856 |
| 291 | $0.03 | 134476 |
| 292 | $0.03 | 134929 |
| 293 | $0.03 | 135664 |
| 294 | $0.03 | 136493 |
| 295 | $0.03 | 137060 |
| 296 | $0.03 | 137639 |
| 297 | $0.03 | 138274 |
| 298 | $0.04 | 139236 |
| 299 | $0.03 | 139933 |
| 300 | $0.03 | 140416 |
| 301 | $0.07 | 145612 |
| 302 | $0.03 | 146314 |
| 303 | $0.04 | 147711 |
| 304 | $0.03 | 148241 |
| 305 | $0.04 | 149304 |
| 306 | $0.03 | 149673 |
| 307 | $0.04 | 151186 |
| 308 | $0.04 | 152512 |
| 309 | $0.06 | 156493 |
| 310 | $0.09 | 163533 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 1 | 468 | $0.01 |
| 🟢 Green | 0 | 0 | $0.00 |
| 🛠️ Refactor | 0 | 0 | $0.00 |
| 🔎 verify-green | 0 | 0 | $0.00 |
| 🔎 verify-refactor | 0 | 0 | $0.00 |
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 0 | 0 | $0.00 |
| 🗺️ verify-plan | 0 | 0 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 1 | 468 | $0.01 |

#### Conductor by phase (estimated: each turn placed by its timestamp)

| phase | turns | $ |
| --- | ---: | ---: |
| between | 228 | 14.21 |
| plan | 2 | 0.11 |
| untimed | 6 | 0.00 |
| grade-prose | 1 | 0.03 |
| refactor-loop | 59 | 2.46 |
| verify-green | 1 | 0.04 |
| develop-cover | 1 | 0.03 |
| develop-structural | 1 | 0.04 |
| preflight | 1 | 0.02 |
| develop-rebase | 1 | 0.03 |
| verify-rebase | 1 | 0.03 |
| structural | 14 | 0.45 |

Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset, VERI_MODEL_REVISE_GREEN unset, VERI_EFFORT_VERIFIER unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 9 | 7 | 2 | 0 | 158 | 133 | 15 | 30 | 15301 | 295785 | 390392 | 1.16 |
| prose | 13 | 0 | 0 | 0 | 565 | 531 | 13 | 26 | 85213 | 209165 | 999592 | 3.37 |
| skill-edit | 3 | 0 | 0 | 0 | 64 | 55 | 13 | 26 | 5062 | 1304010 | 345871 | 1.05 |
| red | 34 | 14 | 1 | 0 | 2156 | 607 | 149 | 294 | 57198 | 3319366 | 834950 | 3.10 |
| green | 44 | 14 | 8 | 0 | 6642 | 747 | 218 | 416 | 69233 | 4894762 | 980951 | 4.00 |
| red-missing | 5 | 0 | 0 | 0 | 164 | 89 | 21 | 40 | 10662 | 433638 | 119725 | 0.45 |
| pin | 7 | 7 | 0 | 0 | 281 | 143 | 38 | 76 | 11940 | 854472 | 155808 | 0.59 |
| refactor | 24 | 3 | 3 | 0 | 1050 | 235 | 81 | 150 | 19595 | 1464998 | 541237 | 2.00 |
| red-tri | 1 | 0 | 0 | 0 | 25 | 17 | 4 | 8 | 1985 | 84645 | 22477 | 0.08 |
| cover | 3 | 0 | 0 | 0 | 61 | 30 | 9 | 18 | 3030 | 158304 | 57259 | 0.19 |
| transform | 2 | 1 | 0 | 0 | 49 | 29 | 11 | 20 | 2768 | 202761 | 38673 | 0.14 |
| structural | 2 | 0 | 0 | 0 | 49 | 29 | 10 | 18 | 3189 | 188095 | 41821 | 0.16 |
| diff | 7 | 1 | 2 | 0 | 557 | 137 | 36 | 68 | 11322 | 708471 | 148026 | 0.77 |
| rebase | 2 | 1 | 0 | 0 | 553 | 40 | 15 | 28 | 3623 | 299010 | 67077 | 0.23 |
| predicate | 1 | 0 | 0 | 0 | 10 | 8 | 3 | 6 | 598 | 50668 | 16736 | 0.05 |
| test-quality | 1 | 0 | 0 | 0 | 15 | 12 | 2 | 4 | 1409 | 29064 | 30025 | 0.09 |

#### REJECT outcomes

| phase | REJECT | caught | flipped | overturned | unresolved | pending | untracked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| red | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| green | 8 | 8 | 0 | 0 | 0 | 0 | 0 |
| refactor | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| diff | 2 | 0 | 0 | 0 | 2 | 0 | 0 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 64 | 48 | 16 | 0 | 6923 | 940 | 249 | 476 | 85274 | 5032677 | 1549615 | 5.23 |
| developer | claude-sonnet-5-5 | 74 | 0 | 0 | 0 | 4438 | 1209 | 337 | 652 | 116985 | 7414388 | 1800465 | 7.10 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 409 | 107 | 26 | 48 | 9594 | 536974 | 95077 | 0.70 |

#### Revise-green, by model

| model | leaves | PASS | REJECT |
| --- | ---: | ---: | ---: |
| claude-sonnet-5-5 | 3 | 0 | 3 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| red | 1197 | 1.72 | 0 | 0.00 |
| green | 26568 | 15.99 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 1527 | 2.90 | 0 | 0.00 |
| red-tri | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 401 | 0.65 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| test-quality | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| with the option --hand <stage>, repeatable, it stops before that stage with seam=<stage> code=1 reason=hand next=DRAFT-PR.md#4. Draft PR without calling it, exit 1 ⟦criterion 5⟧ | 72 | 21 | 7 | 0 | 0 | 0 | 1157 | 280 | 544 | 121794 | 6631469 | 2257640 | 7.92 | 11605 | green 1/2, red 1/2, refactor 2/2 | 0/5 | nothing-left |  |  | already-satisfied |
| with the option --from <stage> it starts at that stage, for each of the five stage names ⟦criterion 5⟧ | 70 | 20 | 5 | 0 | 0 | 0 | 1287 | 313 | 598 | 130351 | 7009711 | 1775107 | 6.83 | 13442 | green 2/2, refactor 1/2 | 0/5 | nothing-left |  |  | pin |
| fix the implementation-coupled case skills/tdd/scripts/tests/py/unit/test_run_pr.py::test_4432_the_title_seam_record_holds_the_sha_of_the_ledgers_last_commit: it finds the record's path with the code's own fused.settled_file and asserts only that the sha appears somewhere in the file, not the record's file name .tdd/issue-<n>-run-pr or its format; edit only that case, no production code ⟦test-quality⟧ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 8⟧ | 5 | 0 | 2 | 0 | 0 | 0 | 111 | 28 | 52 | 9107 | 557965 | 111448 | 0.65 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER, VERI_MODEL_REVISE and VERI_MODEL_REVISE_GREEN.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| with the option --hand <stage>, repeatable, it stops before that stage with seam=<stage> code=1 reason=hand next=DRAFT-PR.md#4. Draft PR without calling it, exit 1 ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 29 | 0.19 |
| with the option --from <stage> it starts at that stage, for each of the five stage names ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 19 | 0.12 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| with the option --hand <stage>, repeatable, it stops before that stage with seam=<stage> code=1 reason=hand next=DRAFT-PR.md#4. Draft PR without calling it, exit 1 ⟦criterion 5⟧ | 1 | 0 | 1 | nothing-left 1 |
| with the option --from <stage> it starts at that stage, for each of the five stage names ⟦criterion 5⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 3 | 1 | 2 | candidates-done 1, nothing-left 2 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| changed | 6 | 4 | 5 | 5 | 6 | 4 | 4 | 6 | 5 | 5 | 0 | 4 | 6 | 4 | 6 | 7 | 6 | 6 | 8 | 36 | 7 | 8 | 7 | 6 | 6 | 5 | 5 | 4 | 5 | 21 | 5 | 5 | 5 | 7 | 8 | 5 | 7 | 9 | 5 | 4 | 5 | 6 | 5 | 5 | 9 | 5 | 6 | 7 | 7 | 5 | 5 | 5 | 4 | 4 | 6 | 5 | 8 | 7 | 6 | 5 | 7 | 7 | 7 | 7 | 10 | 5 | 6 | 5 | 8 | 6 | 6 | 12 | 5 | 5 | 7 | 9 | 0 | 6 | 4 | 6 | 5 | 5 | 5 | 10 | 7 | 6 | 5 | 8 | 7 | 5 | 5 | 6 | 4 | 4 | 5 | 5 | 5 | 4 | 5 | 4 | 6 |
| fast | 60 | 64 | 65 | 65 | 60 | 64 | 64 | 61 | 69 | 66 | 60 | 83 | 87 | 100 | 88 | 68 | 72 | 92 | 96 | 70 | 68 | 94 | 97 | 100 | 94 | 98 | 99 | 85 | 78 | 81 | 65 | 72 | 79 | 94 | 92 | 95 | 79 | 94 | 98 | 80 | 68 | 98 | 81 | 97 | 74 | 128 | 59 | 65 | 63 | 103 | 102 | 94 | 93 | 60 | 67 | 58 | 60 | 60 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 5 | 4 | 5 | 4 | 4 | 5 | 6 | 5 | 5 | 5 | 7 | 5 | 4 | 7 | 4 | 4 | 7 | 5 | 5 | 5 | 5 | 7 | 4 | 11 | 6 | 5 | 4 | 5 | 4 | 5 | 5 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 91 | 399 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Stages

| stage | runs | ok | failed | no answer | nothing | unended | wall s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| preflight | 7 | 7 | 0 | 0 | 0 | 0 | 1194 |
| baseline | 7 | 7 | 0 | 0 | 0 | 0 | 670 |
| plan | 1 | 1 | 0 | 0 | 0 | 0 | 10 |
| push | 47 | 47 | 0 | 0 | 0 | 0 | 98 |
| draft-pr | 1 | 1 | 0 | 0 | 0 | 0 | 2 |
| rebase | 7 | 0 | 4 | 0 | 3 | 0 | 15 |
| refactor-loop | 15 | 14 | 0 | 0 | 0 | 1 | 2273 |
| structural | 1 | 1 | 0 | 0 | 0 | 0 | 172 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 638 | 1228 | 302128 | 14497214 | 4790620 | 34.90 (estimate) |

Not counted: the CI wait after readying and `pr-finish.sh`, which run after this report is committed.

#### Green rejects

| step | attempt | route | check | reason |
| --- | ---: | --- | ---: | --- |
| with the option --hand <stage>, repeatable, it stops before that stage with seam=<stage> code=1 reason=hand next=DRAFT-PR.md#4. Draft PR without calling it, exit 1 ⟦criterion 5⟧ | 1 | revise | 4 | Target, `make unit` (9415 passed) and the changed-file run are green, but the usage guard's `or not argv[0].isdigit()` and `len(argv) != 1` can each be removed or neutralised with every probed suite staying green, so no test requires them. Remove them or add a case for a non-numeric or extra argument. |
| with the option --hand <stage>, repeatable, it stops before that stage with seam=<stage> code=1 reason=hand next=DRAFT-PR.md#4. Draft PR without calling it, exit 1 ⟦criterion 5⟧ | 1 | missing | 4 | MISSING_TEST: run-pr.sh with no argument prints its usage line "usage: run-pr.sh <n>" on stderr, not only exit 2 |
| with the option --from <stage> it starts at that stage, for each of the five stage names ⟦criterion 5⟧ | 1 | revise | 4 | The target test, `make unit` and `test_run_pr.py` are green, but three pieces of `run_pr.py` are untested: the `code == 0` guard in `ledger_sha`, the `else "."` fallback for `wt`, and the sha-equality resume check (criterion 4's behaviour, not this step's). Each can be removed with every test still green. |
| with the option --from <stage> it starts at that stage, for each of the five stage names ⟦criterion 5⟧ | 1 | missing | 4 | MISSING_TEST: the `.tdd/issue-<n>-run-pr` record written at the title seam contains the sha of the ledger's last commit |
| with the option --hand <stage>, repeatable, it stops before that stage with seam=<stage> code=1 reason=hand next=DRAFT-PR.md#4. Draft PR without calling it, exit 1 ⟦criterion 5⟧ | 1 | missing | 4 | MISSING_TEST: a stage exiting 2 stops the run, prints its output then `seam=<stage> code=2 next=DRAFT-PR.md#4. Draft PR`, calls no later stage and exits 2 |
| with the option --from <stage> it starts at that stage, for each of the five stage names ⟦criterion 5⟧ | 1 | revise | 4 | The target test, `make unit` (9427 passed) and `test_run_pr.py` (13 passed) are all green, and the validation does implement exit 2 for an unknown option or a non-stage value. Check 4 fails: the guard `or len(rest) < 2` in `skills/tdd/scripts/veri/run_pr.py` is not required by any test. `mutation-probe.sh` removed it and the suites stayed green (exit 1). Either remove the guard, or add a case for a trailing `--from` with no value, since without the guard that input raises IndexError instead of exiting 2. The probe left `git diff` unchanged. |
| with the option --from <stage> it starts at that stage, for each of the five stage names ⟦criterion 5⟧ | 1 | missing | 4 | MISSING_TEST: an unknown option followed by a valid stage name (`--bogus pr-prepare`) is exit 2 with no stage called, and a valid `--from` or `--hand` pair followed by an invalid one is exit 2. |
| with the option --hand <stage>, repeatable, it stops before that stage with seam=<stage> code=1 reason=hand next=DRAFT-PR.md#4. Draft PR without calling it, exit 1 ⟦criterion 5⟧ | 1 | missing | 4 | MISSING_TEST: run-pr.sh prints a `<stage> <n> exit <code>` call line for pr-ready-wait.sh and pr-finish.sh in the late (title-seam-resumed) run |

Green rejects by route: missing 5, revise 3
Green rejects by check: 4 8, unnamed 0

#### Launch cost, by role

| role | model | leaves | first-turn cache creation | first-turn cache read | first-turn input |
| --- | --- | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 64 | 1345736 | 412163 | 128 |
| grader | claude-sonnet-5-5 | 13 | 999592 | 209165 | 26 |
| author | claude-sonnet-5-5 | 3 | 334482 | 17976 | 6 |
| developer | claude-sonnet-5-5 | 69 | 1306331 | 406470 | 138 |
| developer | claude-opus-5-5 | 9 | 207592 | 10824 | 18 |

Gradings: 7, PASS 4, REJECT 3, cost $2.85, efforts default
