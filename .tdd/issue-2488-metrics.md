### 📊 Metrics — issue 2488

Wall time for the issue: 1446 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 17 of 23 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $23.35 over 457 turns, in 7 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88648 tokens, largest 186423 tokens
Conductor context: first turn 88673 tokens, largest 156281 tokens
Conductor context: first turn 88656 tokens, largest 149079 tokens
Conductor context: first turn 88664 tokens, largest 175421 tokens
Conductor context: first turn 88671 tokens, largest 138889 tokens
Conductor context: first turn 88665 tokens, largest 171771 tokens
Conductor context: first turn 88699 tokens, largest 165486 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 88648 |
| 2 | $0.03 | 89013 |
| 3 | $0.06 | 92773 |
| 4 | $0.04 | 94416 |
| 5 | $0.03 | 95032 |
| 6 | $0.04 | 95731 |
| 7 | $0.03 | 96378 |
| 8 | $0.04 | 96838 |
| 9 | $0.03 | 97399 |
| 10 | $0.04 | 98371 |
| 11 | $0.04 | 99370 |
| 12 | $0.15 | 114870 |
| 13 | $0.05 | 116327 |
| 14 | $0.04 | 117175 |
| 15 | $0.04 | 118833 |
| 16 | $0.07 | 123353 |
| 17 | $0.04 | 123877 |
| 18 | $0.05 | 124715 |
| 19 | $0.04 | 126322 |
| 20 | $0.07 | 130331 |
| 21 | $0.04 | 130818 |
| 22 | $0.05 | 131710 |
| 23 | $0.04 | 132100 |
| 24 | $0.04 | 132400 |
| 25 | $0.04 | 133173 |
| 26 | $0.04 | 133781 |
| 27 | $0.05 | 135131 |
| 28 | $0.04 | 135849 |
| 29 | $0.06 | 137760 |
| 30 | $0.04 | 138090 |
| 31 | $0.04 | 138621 |
| 32 | $0.04 | 139443 |
| 33 | $0.04 | 139719 |
| 34 | $0.05 | 140410 |
| 35 | $0.04 | 141344 |
| 36 | $0.05 | 141965 |
| 37 | $0.05 | 143226 |
| 38 | $0.05 | 144468 |
| 39 | $0.04 | 144840 |
| 40 | $0.10 | 152561 |
| 41 | $0.05 | 154053 |
| 42 | $0.05 | 155329 |
| 43 | $0.05 | 155913 |
| 44 | $0.05 | 156740 |
| 45 | $0.05 | 157458 |
| 46 | $0.04 | 158208 |
| 47 | $0.05 | 159378 |
| 48 | $0.05 | 160194 |
| 49 | $0.05 | 160937 |
| 50 | $0.05 | 161967 |
| 51 | $0.05 | 162655 |
| 52 | $0.05 | 162961 |
| 53 | $0.05 | 164007 |
| 54 | $0.05 | 164731 |
| 55 | $0.05 | 165298 |
| 56 | $0.06 | 167706 |
| 57 | $0.05 | 168349 |
| 58 | $0.04 | 168547 |
| 59 | $0.05 | 169001 |
| 60 | $0.05 | 170164 |
| 61 | $0.06 | 171862 |
| 62 | $0.06 | 173055 |
| 63 | $0.05 | 173783 |
| 64 | $0.06 | 176018 |
| 65 | $0.08 | 180669 |
| 66 | $0.08 | 184884 |
| 67 | $0.06 | 185670 |
| 68 | $0.05 | 186423 |
| 69 | $0.58 | 88673 |
| 70 | $0.03 | 89604 |
| 71 | $0.06 | 93327 |
| 72 | $0.04 | 95171 |
| 73 | $0.05 | 98047 |
| 74 | $0.06 | 101878 |
| 75 | $0.03 | 102372 |
| 76 | $0.03 | 102762 |
| 77 | $0.04 | 103272 |
| 78 | $0.03 | 103556 |
| 79 | $0.03 | 103878 |
| 80 | $0.03 | 104132 |
| 81 | $0.04 | 104883 |
| 82 | $0.03 | 105524 |
| 83 | $0.04 | 107411 |
| 84 | $0.04 | 108579 |
| 85 | $0.04 | 109919 |
| 86 | $0.05 | 112138 |
| 87 | $0.04 | 112945 |
| 88 | $0.03 | 113229 |
| 89 | $0.04 | 114519 |
| 90 | $0.04 | 114995 |
| 91 | $0.04 | 115762 |
| 92 | $0.05 | 118223 |
| 93 | $0.04 | 119218 |
| 94 | $0.03 | 119467 |
| 95 | $0.04 | 119752 |
| 96 | $0.04 | 120643 |
| 97 | $0.04 | 121757 |
| 98 | $0.04 | 122425 |
| 99 | $0.14 | 136948 |
| 100 | $0.06 | 139486 |
| 101 | $0.04 | 140119 |
| 102 | $0.04 | 140415 |
| 103 | $0.04 | 140978 |
| 104 | $0.05 | 142241 |
| 105 | $0.04 | 142924 |
| 106 | $0.04 | 143541 |
| 107 | $0.04 | 144184 |
| 108 | $0.05 | 145419 |
| 109 | $0.04 | 145804 |
| 110 | $0.05 | 146586 |
| 111 | $0.04 | 147001 |
| 112 | $0.04 | 147590 |
| 113 | $0.04 | 148288 |
| 114 | $0.05 | 149614 |
| 115 | $0.04 | 150059 |
| 116 | $0.04 | 150477 |
| 117 | $0.05 | 151639 |
| 118 | $0.05 | 152989 |
| 119 | $0.04 | 153361 |
| 120 | $0.05 | 153776 |
| 121 | $0.04 | 154320 |
| 122 | $0.04 | 154995 |
| 123 | $0.05 | 155919 |
| 124 | $0.04 | 156281 |
| 125 | $0.58 | 88656 |
| 126 | $0.06 | 93324 |
| 127 | $0.04 | 93869 |
| 128 | $0.06 | 97762 |
| 129 | $0.05 | 101442 |
| 130 | $0.04 | 101912 |
| 131 | $0.03 | 102331 |
| 132 | $0.03 | 102730 |
| 133 | $0.04 | 103020 |
| 134 | $0.03 | 103289 |
| 135 | $0.03 | 103751 |
| 136 | $0.04 | 104046 |
| 137 | $0.03 | 104724 |
| 138 | $0.05 | 106483 |
| 139 | $0.04 | 108647 |
| 140 | $0.04 | 109694 |
| 141 | $0.04 | 110338 |
| 142 | $0.04 | 111771 |
| 143 | $0.04 | 112459 |
| 144 | $0.04 | 113010 |
| 145 | $0.03 | 113329 |
| 146 | $0.04 | 114064 |
| 147 | $0.04 | 114756 |
| 148 | $0.03 | 115158 |
| 149 | $0.04 | 115914 |
| 150 | $0.04 | 116488 |
| 151 | $0.04 | 117323 |
| 152 | $0.04 | 118440 |
| 153 | $0.04 | 118736 |
| 154 | $0.09 | 126672 |
| 155 | $0.05 | 127698 |
| 156 | $0.04 | 129032 |
| 157 | $0.04 | 129744 |
| 158 | $0.05 | 130855 |
| 159 | $0.04 | 131941 |
| 160 | $0.04 | 132612 |
| 161 | $0.05 | 133603 |
| 162 | $0.04 | 134824 |
| 163 | $0.04 | 135389 |
| 164 | $0.05 | 136253 |
| 165 | $0.04 | 137113 |
| 166 | $0.04 | 138058 |
| 167 | $0.05 | 139132 |
| 168 | $0.04 | 139590 |
| 169 | $0.05 | 140588 |
| 170 | $0.04 | 141395 |
| 171 | $0.05 | 142242 |
| 172 | $0.04 | 142984 |
| 173 | $0.07 | 147027 |
| 174 | $0.05 | 148157 |
| 175 | $0.04 | 149079 |
| 176 | $0.58 | 88664 |
| 177 | $0.03 | 89068 |
| 178 | $0.07 | 93304 |
| 179 | $0.06 | 98124 |
| 180 | $0.10 | 106291 |
| 181 | $0.04 | 106859 |
| 182 | $0.03 | 107247 |
| 183 | $0.04 | 107563 |
| 184 | $0.03 | 107878 |
| 185 | $0.04 | 108481 |
| 186 | $0.04 | 109317 |
| 187 | $0.04 | 109877 |
| 188 | $0.04 | 110382 |
| 189 | $0.04 | 111014 |
| 190 | $0.03 | 111204 |
| 191 | $0.04 | 112548 |
| 192 | $0.05 | 113391 |
| 193 | $0.04 | 114828 |
| 194 | $0.04 | 115502 |
| 195 | $0.04 | 115919 |
| 196 | $0.04 | 116660 |
| 197 | $0.04 | 116925 |
| 198 | $0.04 | 118322 |
| 199 | $0.04 | 118945 |
| 200 | $0.04 | 119482 |
| 201 | $0.04 | 120336 |
| 202 | $0.11 | 128755 |
| 203 | $0.04 | 129811 |
| 204 | $0.05 | 130910 |
| 205 | $0.04 | 131718 |
| 206 | $0.04 | 132240 |
| 207 | $0.05 | 133162 |
| 208 | $0.04 | 133911 |
| 209 | $0.05 | 134620 |
| 210 | $0.04 | 135022 |
| 211 | $0.04 | 135771 |
| 212 | $0.05 | 136726 |
| 213 | $0.04 | 137478 |
| 214 | $0.05 | 138499 |
| 215 | $0.04 | 138963 |
| 216 | $0.05 | 139662 |
| 217 | $0.04 | 140414 |
| 218 | $0.04 | 140722 |
| 219 | $0.05 | 141576 |
| 220 | $0.05 | 142216 |
| 221 | $0.04 | 143381 |
| 222 | $0.05 | 144265 |
| 223 | $0.05 | 145531 |
| 224 | $0.05 | 146416 |
| 225 | $0.05 | 147309 |
| 226 | $0.04 | 148072 |
| 227 | $0.05 | 149330 |
| 228 | $0.06 | 150531 |
| 229 | $0.05 | 151613 |
| 230 | $0.05 | 152927 |
| 231 | $0.05 | 153977 |
| 232 | $0.05 | 154973 |
| 233 | $0.05 | 155766 |
| 234 | $0.05 | 157044 |
| 235 | $0.05 | 157606 |
| 236 | $0.05 | 158677 |
| 237 | $0.06 | 161204 |
| 238 | $0.05 | 161992 |
| 239 | $0.05 | 162315 |
| 240 | $0.06 | 164268 |
| 241 | $0.07 | 167910 |
| 242 | $0.05 | 168433 |
| 243 | $0.05 | 168878 |
| 244 | $0.08 | 173269 |
| 245 | $0.05 | 174381 |
| 246 | $0.06 | 175421 |
| 247 | $0.58 | 88671 |
| 248 | $0.06 | 93116 |
| 249 | $0.04 | 95040 |
| 250 | $0.07 | 100432 |
| 251 | $0.03 | 100993 |
| 252 | $0.04 | 101418 |
| 253 | $0.03 | 101782 |
| 254 | $0.03 | 102038 |
| 255 | $0.03 | 102638 |
| 256 | $0.06 | 106318 |
| 257 | $0.04 | 107708 |
| 258 | $0.04 | 109041 |
| 259 | $0.04 | 110526 |
| 260 | $0.04 | 111175 |
| 261 | $0.03 | 111398 |
| 262 | $0.05 | 113003 |
| 263 | $0.03 | 113703 |
| 264 | $0.04 | 114442 |
| 265 | $0.03 | 114879 |
| 266 | $0.04 | 116164 |
| 267 | $0.04 | 116362 |
| 268 | $0.04 | 117086 |
| 269 | $0.03 | 117952 |
| 270 | $0.04 | 118710 |
| 271 | $0.04 | 119617 |
| 272 | $0.04 | 119857 |
| 273 | $0.04 | 121308 |
| 274 | $0.03 | 121553 |
| 275 | $0.05 | 123105 |
| 276 | $0.03 | 123477 |
| 277 | $0.04 | 124023 |
| 278 | $0.04 | 124440 |
| 279 | $0.04 | 124953 |
| 280 | $0.03 | 125373 |
| 281 | $0.04 | 126091 |
| 282 | $0.04 | 126745 |
| 283 | $0.04 | 127662 |
| 284 | $0.04 | 128403 |
| 285 | $0.04 | 128976 |
| 286 | $0.04 | 129817 |
| 287 | $0.04 | 130500 |
| 288 | $0.04 | 130881 |
| 289 | $0.04 | 132124 |
| 290 | $0.04 | 132547 |
| 291 | $0.04 | 132841 |
| 292 | $0.03 | 133109 |
| 293 | $0.04 | 133554 |
| 294 | $0.04 | 133905 |
| 295 | $0.04 | 134914 |
| 296 | $0.04 | 135364 |
| 297 | $0.04 | 135536 |
| 298 | $0.04 | 135930 |
| 299 | $0.04 | 136466 |
| 300 | $0.04 | 137556 |
| 301 | $0.04 | 138533 |
| 302 | $0.04 | 138889 |
| 303 | $0.58 | 88665 |
| 304 | $0.06 | 93108 |
| 305 | $0.04 | 93608 |
| 306 | $0.08 | 100408 |
| 307 | $0.06 | 104147 |
| 308 | $0.03 | 104689 |
| 309 | $0.04 | 105191 |
| 310 | $0.03 | 105459 |
| 311 | $0.04 | 105796 |
| 312 | $0.03 | 106554 |
| 313 | $0.04 | 107195 |
| 314 | $0.04 | 107805 |
| 315 | $0.03 | 108464 |
| 316 | $0.05 | 109846 |
| 317 | $0.04 | 110744 |
| 318 | $0.04 | 111590 |
| 319 | $0.03 | 111967 |
| 320 | $0.04 | 112511 |
| 321 | $0.04 | 113701 |
| 322 | $0.04 | 114369 |
| 323 | $0.04 | 114932 |
| 324 | $0.03 | 115651 |
| 325 | $0.05 | 116598 |
| 326 | $0.03 | 117304 |
| 327 | $0.04 | 117976 |
| 328 | $0.04 | 118454 |
| 329 | $0.10 | 126127 |
| 330 | $0.04 | 127138 |
| 331 | $0.04 | 128325 |
| 332 | $0.04 | 128898 |
| 333 | $0.05 | 130516 |
| 334 | $0.05 | 131402 |
| 335 | $0.04 | 131903 |
| 336 | $0.04 | 132954 |
| 337 | $0.05 | 134193 |
| 338 | $0.05 | 135495 |
| 339 | $0.04 | 136215 |
| 340 | $0.04 | 136684 |
| 341 | $0.04 | 137525 |
| 342 | $0.05 | 138155 |
| 343 | $0.05 | 139803 |
| 344 | $0.04 | 140761 |
| 345 | $0.05 | 141746 |
| 346 | $0.05 | 142569 |
| 347 | $0.04 | 143389 |
| 348 | $0.05 | 144675 |
| 349 | $0.04 | 145121 |
| 350 | $0.05 | 146445 |
| 351 | $0.05 | 147433 |
| 352 | $0.05 | 148199 |
| 353 | $0.05 | 150622 |
| 354 | $0.05 | 151401 |
| 355 | $0.04 | 151709 |
| 356 | $0.05 | 152781 |
| 357 | $0.05 | 153538 |
| 358 | $0.06 | 155666 |
| 359 | $0.05 | 157221 |
| 360 | $0.05 | 157779 |
| 361 | $0.04 | 158517 |
| 362 | $0.06 | 159615 |
| 363 | $0.04 | 160131 |
| 364 | $0.05 | 160438 |
| 365 | $0.04 | 161154 |
| 366 | $0.05 | 161915 |
| 367 | $0.05 | 162284 |
| 368 | $0.04 | 162633 |
| 369 | $0.05 | 163103 |
| 370 | $0.05 | 163640 |
| 371 | $0.05 | 164440 |
| 372 | $0.05 | 165373 |
| 373 | $0.04 | 165880 |
| 374 | $0.05 | 166698 |
| 375 | $0.05 | 167320 |
| 376 | $0.05 | 167707 |
| 377 | $0.05 | 168134 |
| 378 | $0.04 | 168822 |
| 379 | $0.06 | 170253 |
| 380 | $0.05 | 171303 |
| 381 | $0.05 | 171771 |
| 382 | $0.57 | 88699 |
| 383 | $0.02 | 89078 |
| 384 | $0.05 | 93336 |
| 385 | $0.03 | 95265 |
| 386 | $0.09 | 103794 |
| 387 | $0.04 | 105654 |
| 388 | $0.02 | 106134 |
| 389 | $0.05 | 109998 |
| 390 | $0.02 | 110358 |
| 391 | $0.02 | 110652 |
| 392 | $0.03 | 111126 |
| 393 | $0.03 | 111668 |
| 394 | $0.02 | 111982 |
| 395 | $0.02 | 112240 |
| 396 | $0.03 | 112892 |
| 397 | $0.03 | 114081 |
| 398 | $0.03 | 114797 |
| 399 | $0.03 | 115460 |
| 400 | $0.03 | 116813 |
| 401 | $0.03 | 117676 |
| 402 | $0.03 | 118324 |
| 403 | $0.03 | 118687 |
| 404 | $0.03 | 119255 |
| 405 | $0.03 | 119728 |
| 406 | $0.03 | 120356 |
| 407 | $0.03 | 120633 |
| 408 | $0.03 | 121876 |
| 409 | $0.03 | 122492 |
| 410 | $0.03 | 123221 |
| 411 | $0.03 | 123750 |
| 412 | $0.09 | 131674 |
| 413 | $0.04 | 133566 |
| 414 | $0.03 | 133990 |
| 415 | $0.03 | 134621 |
| 416 | $0.03 | 134987 |
| 417 | $0.04 | 136077 |
| 418 | $0.04 | 137407 |
| 419 | $0.03 | 138262 |
| 420 | $0.05 | 140773 |
| 421 | $0.04 | 141843 |
| 422 | $0.04 | 143175 |
| 423 | $0.04 | 144973 |
| 424 | $0.03 | 145527 |
| 425 | $0.04 | 146553 |
| 426 | $0.04 | 147477 |
| 427 | $0.04 | 148331 |
| 428 | $0.03 | 148889 |
| 429 | $0.03 | 149198 |
| 430 | $0.04 | 149876 |
| 431 | $0.04 | 150605 |
| 432 | $0.04 | 151372 |
| 433 | $0.03 | 151927 |
| 434 | $0.04 | 153280 |
| 435 | $0.04 | 154123 |
| 436 | $0.04 | 154811 |
| 437 | $0.04 | 155746 |
| 438 | $0.04 | 156536 |
| 439 | $0.04 | 157613 |
| 440 | $0.04 | 158310 |
| 441 | $0.04 | 158740 |
| 442 | $0.04 | 159663 |
| 443 | $0.04 | 160649 |
| 444 | $0.04 | 161429 |
| 445 | $0.06 | 165486 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 22 | 2 | 4 | 2033 | 36668 | 39437 | 0.12 |
| red | 27 | 10 | 1 | 0 | 820 | 700 | 134 | 268 | 61991 | 4722425 | 886700 | 3.68 |
| green | 42 | 7 | 12 | 0 | 2430 | 1295 | 238 | 466 | 114204 | 8336365 | 898246 | 5.85 |
| red-missing | 2 | 0 | 0 | 0 | 89 | 65 | 14 | 26 | 7905 | 600834 | 69907 | 0.31 |
| pin | 7 | 7 | 0 | 0 | 170 | 125 | 32 | 64 | 11581 | 1008733 | 169046 | 0.64 |
| refactor | 7 | 0 | 0 | 0 | 89 | 71 | 20 | 40 | 2576 | 562144 | 179788 | 0.53 |
| prose | 36 | 0 | 0 | 0 | 1522 | 1443 | 36 | 72 | 221026 | 250940 | 1607859 | 6.26 |
| skill-edit | 8 | 0 | 0 | 0 | 610 | 144 | 39 | 76 | 11536 | 2333112 | 606295 | 1.86 |
| reconcile | 1 | 0 | 0 | 0 | 13 | 6 | 3 | 6 | 509 | 69451 | 35929 | 0.10 |
| exhausted | 2 | 0 | 0 | 0 | 92 | 67 | 7 | 14 | 5066 | 209392 | 39430 | 0.34 |
| rebase | 2 | 1 | 0 | 0 | 814 | 57 | 12 | 22 | 4298 | 258697 | 163319 | 0.48 |
| red-contradicted | 1 | 0 | 0 | 0 | 32 | 29 | 7 | 12 | 2832 | 227669 | 29472 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 39 | 26 | 13 | 0 | 1803 | 783 | 167 | 328 | 66245 | 5257087 | 854774 | 3.33 |
| developer | claude-sonnet-5-5 | 35 | 0 | 0 | 0 | 1557 | 793 | 180 | 352 | 70855 | 6137227 | 1096276 | 4.33 |
| developer | claude-opus-5-5 | 18 | 0 | 0 | 0 | 1213 | 861 | 122 | 242 | 75895 | 4638064 | 560224 | 4.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 302 | 1.50 |
| green | 1819 | 4.16 | 1029 | 2.52 |
| red-missing | 0 | 0.00 | 29 | 0.11 |
| pin | 0 | 0.00 | 25 | 0.09 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 105 | 0.42 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| reconcile | 0 | 0.00 | 13 | 0.10 |
| exhausted | 0 | 0.00 | 92 | 0.34 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 32 | 0.12 |
| verify-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `wait-ci.sh` exits 4 — a code of its own, distinct from 0, 1, 2 and 3 — on its first poll when the PR's head reports no check runs and no commit statuses and none of the head's `.github/workflows/*` files carries a `pull_request` or `pull_request_target` trigger: no `.tdd/ci-deadline-<sha>` is recorded and no poll sleep is served; the conflict refusal (exit 2) and the draft refusal (exit 2) keep precedence, and a PR still reporting a head other than `<head-sha>` stays pending (3); the header's status line names exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, and older cases there that pin exit 3 for a rollup with no check are superseded by this step ⟦criterion 1⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 222 | 49 | 98 | 21596 | 1798487 | 264928 | 1.17 | 667 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| A late CI is unaffected: `wait-ci.sh` still exits 3 when the rollup reports no check yet but a head workflow carries a `pull_request` trigger, exits 3 while a check is pending, and 0 or 1 when the checks land green or red; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, no production change ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 12 | 24 | 4506 | 439734 | 48665 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/SCRIPTS.md`'s `wait-ci.sh` entry (SC38) documents exit 4, a PR whose rollup reports no checks on the first poll with no head workflow triggered by pull requests, distinct from pending (3) and from past-the-deadline (2) ⟦skill-edit⟧ ⟦criterion 1⟧ | 9 | 0 | 0 | 0 | 0 | 0 | 166 | 25 | 50 | 20347 | 1066799 | 293355 | 1.04 | -816894 | unknown | unknown | unknown |  |  | full |
| `skills/tdd/SKILL.md`'s Draft PR step routes a `wait-ci.sh` exit 4 at both CI waits (the first wait and the wait after the `metrics:` push) as no CI gate for this pull request: no bail mark, no `ci-timeout` cause, no `⟦ci-repair⟧` step appended; the run goes on to the `done` mark, the `metrics:` commit and a `### ✅ Done` comment that says the repository reports no checks on this pull request; pins outside the unit in `skills/tdd/scripts/tests/py/test_skill_ci_conflict.py` updated in the same commit ⟦skill-edit⟧ ⟦criterion 2⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 245 | 9 | 18 | 34784 | 662139 | 459575 | 1.56 | 734 | unknown | unknown | unknown |  |  | full |
| Running the Draft PR step's CI command blocks from `skills/tdd/SKILL.md` under `bash -c` with a `wait-ci.sh` stub that exits 4 writes no `bail` event and no `ci-timeout` cause, appends no step to the ledger, and writes the `done` mark; a medium case with a real process (`@pytest.mark.process`), against stub scripts as `test_skill_ci_conflict.py` does, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 11 | 22 | 5008 | 370759 | 73608 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |
| `queued-merge.sh` still refuses to merge when `wait-ci.sh` exits 4: no `gh pr merge` is called and it exits non-zero, so an empty rollup is still not a pass at merge time; a small in-process case in `tests/py/unit/test_queued_merge.py`, no production change ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 20 | 3026 | 328821 | 42801 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_supervise_process.py::test_2380_a_leaf_queued_on_the_full_suite_lock_past_the_hard_timeout_is_not_killed_stuck — AssertionError: harvest-usage.sh: no closing result record in .tdd/verify-rebase.log — no usage event appended for verify-rebase ⟦suite-repair⟧ ⟦criterion 4⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 6 | 3 | 6 | 509 | 69451 | 35929 | 0.10 | unknown | unknown | unknown | unknown |  |  | full |
| `wait_ci.py`'s `runs_on_pull_requests` reads each head workflow's `on:` trigger block instead of matching raw text: `pull_request` or `pull_request_target` counts as running on pull requests when bare, with no `types:`, or with `types:` naming any of opened, synchronize, reopened or ready_for_review, and does not count when its `types:` name none of those; the list form (`on: [push, pull_request]`) and the mapping form are both read; a mention only in a comment or an `if:` does not count; stdlib only, no YAML library and no new requirements-dev.txt entry; cases each red first: ps-mutuus/gs-marketplace's exact trigger `on: pull_request: types: [closed]` reaches exit 4, `types: [opened, synchronize]` stays on exit 3, a workflow whose only mention of pull_request is a comment or an `if:` reaches exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 12 | 2 | 3 | 0 | 0 | 0 | 247 | 55 | 108 | 26133 | 1770573 | 287729 | 1.50 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |
| `wait_ci.py`'s `runs_on_pull_requests` reads each head workflow's `on:` trigger block instead of matching raw text: `pull_request` or `pull_request_target` counts as running on pull requests when bare, with no `types:`, or with `types:` naming any of opened, synchronize, reopened or ready_for_review, and does not count when its `types:` name none of those; the list form (`on: [push, pull_request]`) and the mapping form are both read; a mention only in a comment or an `if:` does not count; stdlib only, no YAML library and no new requirements-dev.txt entry; cases each red first: ps-mutuus/gs-marketplace's exact trigger `on: pull_request: types: [closed]` reaches exit 4, `types: [opened, synchronize]` stays on exit 3, a `types: [reopened]` workflow and a `types: [ready_for_review]` workflow each stay on exit 3, and every entry of the opening types (opened, synchronize, reopened, ready_for_review) is pinned by a case that goes red when that entry alone is removed, a workflow whose only mention of pull_request is a comment or an `if:` reaches exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 11 | 2 | 3 | 0 | 0 | 0 | 281 | 54 | 108 | 26717 | 1812380 | 268527 | 1.55 | 669 | 3/4 | 0/5 | nothing-left |  |  | full |
| `wait-ci.sh` still fails closed: an unreadable workflows listing (other than a 404), an unreadable workflow body, or an `on:` block the reader cannot make sense of counts as running on pull requests, so exit 3 and the deadline runs; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 104 | 21 | 40 | 6065 | 645101 | 112345 | 0.41 | 226 | unknown | 0/5 | nothing-left |  |  | full |
| A 404 on `repos/<owner>/<repo>/contents/.github/workflows` counts as no workflow running on pull requests, so the empty rollup exits 4, distinguished from every other non-zero listing failure, which stays fail-closed (exit 3); the commit body records why: by then the same token has read the PR and its check rollup, so a 404 on the workflows directory is absence, not a permission wall; a small in-process case in `tests/py/unit/test_wait_ci.py`, red first ⟦added⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 105 | 23 | 44 | 6867 | 736967 | 110775 | 0.42 | 235 | unknown | 0/5 | nothing-left |  |  | full |
| `test_skill_ci_conflict.py`'s done-mark assertion (`:136`) can fail: the case no longer writes the `done` line whatever the stubbed `wait-ci.sh` exit code, so breaking the exit-4 routing in the command block turns that assertion red; watched red, then restored ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 13 | 26 | 6718 | 528611 | 63478 | 0.28 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/REQUIREMENTS.md` gains the issue's `## Requirements` rows for `skills/tdd/SKILL.md`'s exit-4 routing at both CI waits (`SKILL.md:1704`, `:1741`), graded PASS ⟦skill-edit⟧ ⟦added⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 103 | 1 | 2 | 14871 | 649 | 107675 | 0.42 | unknown | unknown | unknown | unknown |  |  | full |
| A change to `skills/tdd/SKILL.md`'s prose: in the Draft PR step's exit-4 paragraph (`SKILL.md:1704`), reword the clause "— the repository reports no checks on this pull request —" to say that the PR's head reports no checks and no head workflow runs on pull requests (a `pull_request` trigger whose `types:` name none of opened, synchronize, reopened, ready_for_review does not count, and a missing workflows directory counts as none), so the prose matches the trigger-aware exit 4 of steps 8–10; graded against its list with the issue's `## Requirements` rows DP85 and DP86 added to `skills/tdd/REQUIREMENTS.md` ⟦skill-edit⟧ ⟦criterion 2⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 226 | 5 | 10 | 35092 | 253165 | 340606 | 1.23 | 256 | unknown | unknown | unknown |  |  | full |
| `skills/tdd/SCRIPTS.md`'s `wait-ci.sh` entry (SC38) states the trigger rule (a `pull_request` trigger whose `types:` name none of opened, synchronize, reopened, ready_for_review does not count), that a 404 on the workflows directory exits 4, and that `queued-merge.sh` passes a `wait-ci.sh` exit 4 through as its own exit code and merges nothing ⟦skill-edit⟧ ⟦added⟧ ⟦criterion 4⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 93 | 9 | 16 | 11583 | 224501 | 146636 | 0.50 | 130 | unknown | unknown | unknown |  |  | full |
| `CLAUDE.md`'s "Exit codes are the API" section states `wait-ci.sh`'s exit 4 (the repository reports no checks on this pull request) as the one script code beyond the four, and that `queued-merge.sh` passes it through (`queued_merge.py:160`) ⟦added⟧ ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 106 | 22 | 44 | 5891 | 716996 | 122382 | 0.44 | 275 | unknown | 0/5 | nothing-left |  |  | full |
| `wait_ci.py`'s runs-on-pull-requests predicate defaults to TRUE and reaches exit 4 only where it positively establishes, for every workflow file at the head, either that the file's `on:` region holds no `pull_request` and no `pull_request_target` trigger key at all, or that every such key carries a `types:` list, found inside that trigger's own block, naming none of opened, synchronize, reopened, ready_for_review; the spelling-by-spelling parser is replaced by this rule, and the four opening types stay pinned as they are; cases, each red first on today's code: scalar `on: pull_request` and `on: pull_request_target` → 3; block list `on:` then `- pull_request` → 3; quoted `'on': [pull_request]` and a quoted `"pull_request":` key → 3; flow `on: {pull_request: {types: [closed]}}` → 4 and flow `on: {pull_request: null}` → 3; a bare `pull_request:` with a later `workflow_run: types: [completed]` → 3 (the `types:` search stays inside the trigger's own block); ps-mutuus/gs-marketplace's pair (`ci.yml` push only, `deploy.yml` `pull_request: types: [closed]`) still → 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 236 | 41 | 80 | 22002 | 1310858 | 247660 | 1.26 | 605 | 2/2 | 0/5 | nothing-left |  |  | full |
| Everything the predicate cannot positively classify counts as running on pull requests (exit 3, the deadline runs): an `on:` value it cannot classify (`on: !!binary |`), a `types:` whose extent or a trigger whose own block it cannot delimit, an unreadable workflow body, a non-404 listing failure; a readable file in `.github/workflows` with no `on:` region (a README) contributes nothing, so a directory holding only such a file reaches exit 4; a 404 on the directory stays exit 4; cases, each red first: `on: !!binary |` → 3, README-only directory → 4, unreadable body → 3, non-404 listing failure → 3; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 106 | 22 | 44 | 7546 | 734701 | 117741 | 0.44 | 241 | unknown | 0/5 | nothing-left |  |  | full |
| `queued-merge.sh` passes a `wait-ci.sh` exit 4 through as exactly exit 4 (not merely non-zero) and calls no `gh pr merge`: `tests/py/unit/test_queued_merge.py`'s case (`:288`) asserts the exact code 4, so rewriting the pass-through to exit 1 turns it red; a pin step for behaviour that already holds (Red reports already passes), never ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 9 | 18 | 3480 | 294836 | 42652 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| A change to `skills/tdd/SCRIPTS.md`'s prose, so its SC38 requirement row (`skills/tdd/REQUIREMENTS.md:710`) is brought in line: reword SC38's `wait-ci.sh` exit-4 sentence to state the default-TRUE rule (exit 4 only where every workflow file at the head is shown to have no `pull_request`/`pull_request_target` trigger or only ones whose own `types:` name none of opened, synchronize, reopened, ready_for_review; anything unclassifiable counts as running on pull requests), that a 404 on the workflows directory exits 4, and that `queued-merge.sh` passes exit 4 through as its own exit code; graded against SCRIPTS.md's list with the SC38 row updated to say the same ⟦skill-edit⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 12 | 22 | 4298 | 258697 | 163319 | 0.48 | unknown | unknown | unknown | unknown |  |  | full |
| `wait_ci.py`'s runs-on-pull-requests predicate is a whitelist of one recognisable shape: a workflow file counts as not running on pull requests only when it has exactly one `on:` line, unindented at column 0, and no `*`, `&` or `{` anywhere in its `on:` region, and each `pull_request`/`pull_request_target` key in that region is either absent or carries `types:` inside its own block as a single-line closed `[...]` list or a `-` block list naming none of opened, synchronize, reopened, ready_for_review; every other file counts as running on pull requests (exit 3); a readable file with no `on:` line contributes nothing; cases, each red first on today's code, for the ten forms the review of d6ca06c90 found reaching exit 4 where 3 is right — every entry of `.tdd/issue-2488-forms.md` whose note starts "FLAGGED:" — each → 3, and ps-mutuus/gs-marketplace's real pair (`gs_marketplace_real` there) still → 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 16 | 2 | 4 | 0 | 0 | 0 | 723 | 110 | 214 | 60600 | 4178738 | 469298 | 3.19 | unknown | green 3/2, red 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `wait-ci.sh` exits 4 — a code of its own, distinct from 0, 1, 2 and 3 — on its first poll when the PR's head reports no check runs and no commit statuses and none of the head's `.github/workflows/*` files carries a `pull_request` or `pull_request_target` trigger: no `.tdd/ci-deadline-<sha>` is recorded and no poll sleep is served; the conflict refusal (exit 2) and the draft refusal (exit 2) keep precedence, and a PR still reporting a head other than `<head-sha>` stays pending (3); the header's status line names exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, and older cases there that pin exit 3 for a rollup with no check are superseded by this step ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.07 |
| `wait_ci.py`'s `runs_on_pull_requests` reads each head workflow's `on:` trigger block instead of matching raw text: `pull_request` or `pull_request_target` counts as running on pull requests when bare, with no `types:`, or with `types:` naming any of opened, synchronize, reopened or ready_for_review, and does not count when its `types:` name none of those; the list form (`on: [push, pull_request]`) and the mapping form are both read; a mention only in a comment or an `if:` does not count; stdlib only, no YAML library and no new requirements-dev.txt entry; cases each red first: ps-mutuus/gs-marketplace's exact trigger `on: pull_request: types: [closed]` reaches exit 4, `types: [opened, synchronize]` stays on exit 3, a `types: [reopened]` workflow and a `types: [ready_for_review]` workflow each stay on exit 3, and every entry of the opening types (opened, synchronize, reopened, ready_for_review) is pinned by a case that goes red when that entry alone is removed, a workflow whose only mention of pull_request is a comment or an `if:` reaches exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.11 |
| `wait-ci.sh` still fails closed: an unreadable workflows listing (other than a 404), an unreadable workflow body, or an `on:` block the reader cannot make sense of counts as running on pull requests, so exit 3 and the deadline runs; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 28 | 0.06 |
| A 404 on `repos/<owner>/<repo>/contents/.github/workflows` counts as no workflow running on pull requests, so the empty rollup exits 4, distinguished from every other non-zero listing failure, which stays fail-closed (exit 3); the commit body records why: by then the same token has read the PR and its check rollup, so a 404 on the workflows directory is absence, not a permission wall; a small in-process case in `tests/py/unit/test_wait_ci.py`, red first ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.05 |
| `CLAUDE.md`'s "Exit codes are the API" section states `wait-ci.sh`'s exit 4 (the repository reports no checks on this pull request) as the one script code beyond the four, and that `queued-merge.sh` passes it through (`queued_merge.py:160`) ⟦added⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.06 |
| `wait_ci.py`'s runs-on-pull-requests predicate defaults to TRUE and reaches exit 4 only where it positively establishes, for every workflow file at the head, either that the file's `on:` region holds no `pull_request` and no `pull_request_target` trigger key at all, or that every such key carries a `types:` list, found inside that trigger's own block, naming none of opened, synchronize, reopened, ready_for_review; the spelling-by-spelling parser is replaced by this rule, and the four opening types stay pinned as they are; cases, each red first on today's code: scalar `on: pull_request` and `on: pull_request_target` → 3; block list `on:` then `- pull_request` → 3; quoted `'on': [pull_request]` and a quoted `"pull_request":` key → 3; flow `on: {pull_request: {types: [closed]}}` → 4 and flow `on: {pull_request: null}` → 3; a bare `pull_request:` with a later `workflow_run: types: [completed]` → 3 (the `types:` search stays inside the trigger's own block); ps-mutuus/gs-marketplace's pair (`ci.yml` push only, `deploy.yml` `pull_request: types: [closed]`) still → 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 13 | 0.11 |
| Everything the predicate cannot positively classify counts as running on pull requests (exit 3, the deadline runs): an `on:` value it cannot classify (`on: !!binary |`), a `types:` whose extent or a trigger whose own block it cannot delimit, an unreadable workflow body, a non-404 listing failure; a readable file in `.github/workflows` with no `on:` region (a README) contributes nothing, so a directory holding only such a file reaches exit 4; a 404 on the directory stays exit 4; cases, each red first: `on: !!binary |` → 3, README-only directory → 4, unreadable body → 3, non-404 listing failure → 3; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 14 | 0.07 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 0 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 0 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 |
| fast | 18 | 18 | 18 | 18 | 17 | 17 | 16 | 19 | 19 | 20 | 20 | 13 | 13 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 13 | 13 | 13 | 13 | 13 | 16 | 15 | 14 | 16 | 15 | 15 | 14 | 15 | 16 | 18 | 12 | 13 | 13 | 17 | 18 | 17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 0 | 1 | 1 | 0 | 2 | 0 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 0 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 379 | 370 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 544 | 1070 | 445557 | 18616430 | 4725428 | 20.30 |
