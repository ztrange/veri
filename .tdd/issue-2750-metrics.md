### 📊 Metrics — issue 2750

Wall time for the issue: 190 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 20 of 31 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $29.08 over 493 turns, in 8 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87212 tokens, largest 257328 tokens
Conductor context: first turn 87214 tokens, largest 118124 tokens
Conductor context: first turn 88033 tokens, largest 221161 tokens
Conductor context: first turn 88361 tokens, largest 168958 tokens
Conductor context: first turn 88993 tokens, largest 131663 tokens
Conductor context: first turn 89184 tokens, largest 156896 tokens
Conductor context: first turn 92622 tokens, largest 157017 tokens
Conductor context: first turn 92855 tokens, largest 162571 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87212 |
| 2 | $0.09 | 94293 |
| 3 | $0.04 | 95983 |
| 4 | $0.04 | 97944 |
| 5 | $0.03 | 98295 |
| 6 | $0.03 | 98585 |
| 7 | $0.03 | 98897 |
| 8 | $0.03 | 99129 |
| 9 | $0.03 | 99324 |
| 10 | $0.02 | 99563 |
| 11 | $0.03 | 99870 |
| 12 | $0.03 | 100176 |
| 13 | $0.03 | 100343 |
| 14 | $0.04 | 100943 |
| 15 | $0.03 | 101284 |
| 16 | $0.04 | 103392 |
| 17 | $0.14 | 116749 |
| 18 | $0.05 | 119093 |
| 19 | $0.06 | 123726 |
| 20 | $0.05 | 125515 |
| 21 | $0.05 | 127967 |
| 22 | $0.04 | 128581 |
| 23 | $0.04 | 129108 |
| 24 | $0.04 | 129678 |
| 25 | $0.04 | 131091 |
| 26 | $0.04 | 131557 |
| 27 | $0.05 | 133067 |
| 28 | $0.13 | 145545 |
| 29 | $0.04 | 145968 |
| 30 | $0.04 | 146669 |
| 31 | $0.04 | 147092 |
| 32 | $0.04 | 147723 |
| 33 | $0.04 | 147902 |
| 34 | $0.05 | 148699 |
| 35 | $0.04 | 149109 |
| 36 | $0.04 | 149606 |
| 37 | $0.05 | 150935 |
| 38 | $0.05 | 153080 |
| 39 | $0.04 | 153312 |
| 40 | $0.04 | 153610 |
| 41 | $0.04 | 153899 |
| 42 | $0.11 | 162245 |
| 43 | $0.05 | 163351 |
| 44 | $0.04 | 163569 |
| 45 | $0.04 | 164053 |
| 46 | $0.05 | 164823 |
| 47 | $0.04 | 165248 |
| 48 | $0.05 | 165443 |
| 49 | $0.04 | 165831 |
| 50 | $0.04 | 166373 |
| 51 | $0.05 | 167016 |
| 52 | $0.04 | 167253 |
| 53 | $0.05 | 167714 |
| 54 | $0.04 | 168230 |
| 55 | $0.05 | 168637 |
| 56 | $0.05 | 169552 |
| 57 | $0.04 | 170283 |
| 58 | $0.05 | 170857 |
| 59 | $0.04 | 171262 |
| 60 | $0.05 | 171550 |
| 61 | $0.05 | 172149 |
| 62 | $0.04 | 172588 |
| 63 | $0.05 | 173740 |
| 64 | $0.05 | 174644 |
| 65 | $0.06 | 175983 |
| 66 | $0.05 | 177615 |
| 67 | $0.06 | 178983 |
| 68 | $0.04 | 179758 |
| 69 | $0.05 | 180288 |
| 70 | $0.05 | 180905 |
| 71 | $0.05 | 181228 |
| 72 | $0.05 | 181916 |
| 73 | $0.05 | 182527 |
| 74 | $0.04 | 182745 |
| 75 | $0.05 | 183671 |
| 76 | $0.05 | 183972 |
| 77 | $0.05 | 184553 |
| 78 | $0.05 | 184941 |
| 79 | $0.04 | 185231 |
| 80 | $0.05 | 186019 |
| 81 | $0.06 | 187059 |
| 82 | $0.05 | 187831 |
| 83 | $0.05 | 188135 |
| 84 | $0.05 | 188665 |
| 85 | $0.05 | 189263 |
| 86 | $0.05 | 190299 |
| 87 | $0.05 | 190502 |
| 88 | $0.05 | 191687 |
| 89 | $0.06 | 192912 |
| 90 | $0.06 | 194533 |
| 91 | $0.05 | 195870 |
| 92 | $0.06 | 196959 |
| 93 | $0.06 | 198259 |
| 94 | $0.06 | 200506 |
| 95 | $0.05 | 201052 |
| 96 | $0.06 | 201755 |
| 97 | $0.05 | 202170 |
| 98 | $0.05 | 202324 |
| 99 | $0.05 | 202931 |
| 100 | $0.05 | 203302 |
| 101 | $0.06 | 204277 |
| 102 | $0.05 | 204512 |
| 103 | $0.05 | 205048 |
| 104 | $0.05 | 205369 |
| 105 | $0.05 | 205856 |
| 106 | $0.06 | 207122 |
| 107 | $0.06 | 207837 |
| 108 | $0.05 | 208220 |
| 109 | $0.05 | 208626 |
| 110 | $0.06 | 209048 |
| 111 | $0.05 | 209534 |
| 112 | $0.05 | 209815 |
| 113 | $0.06 | 211152 |
| 114 | $0.07 | 213015 |
| 115 | $0.05 | 213683 |
| 116 | $0.05 | 213978 |
| 117 | $0.06 | 215303 |
| 118 | $0.06 | 215735 |
| 119 | $0.05 | 216152 |
| 120 | $0.06 | 216544 |
| 121 | $0.07 | 219230 |
| 122 | $0.06 | 220341 |
| 123 | $0.05 | 220666 |
| 124 | $0.06 | 221122 |
| 125 | $0.06 | 222495 |
| 126 | $0.06 | 222686 |
| 127 | $0.06 | 223653 |
| 128 | $0.05 | 224242 |
| 129 | $0.06 | 224797 |
| 130 | $0.06 | 226017 |
| 131 | $0.06 | 226766 |
| 132 | $0.06 | 227148 |
| 133 | $0.05 | 227304 |
| 134 | $0.06 | 227502 |
| 135 | $0.06 | 228453 |
| 136 | $0.05 | 228817 |
| 137 | $0.06 | 229524 |
| 138 | $0.06 | 229797 |
| 139 | $0.05 | 229969 |
| 140 | $0.06 | 230395 |
| 141 | $0.06 | 230717 |
| 142 | $0.05 | 231430 |
| 143 | $0.06 | 231729 |
| 144 | $0.06 | 231916 |
| 145 | $0.05 | 232253 |
| 146 | $0.06 | 232954 |
| 147 | $0.06 | 233242 |
| 148 | $0.06 | 233521 |
| 149 | $0.05 | 233855 |
| 150 | $0.06 | 234541 |
| 151 | $0.06 | 234799 |
| 152 | $0.06 | 235388 |
| 153 | $0.05 | 235659 |
| 154 | $0.06 | 235964 |
| 155 | $0.06 | 236274 |
| 156 | $0.06 | 236486 |
| 157 | $0.05 | 236978 |
| 158 | $0.06 | 237254 |
| 159 | $0.06 | 237534 |
| 160 | $0.06 | 237864 |
| 161 | $0.06 | 238535 |
| 162 | $0.05 | 238797 |
| 163 | $0.06 | 239003 |
| 164 | $0.06 | 239188 |
| 165 | $0.06 | 239477 |
| 166 | $0.05 | 239691 |
| 167 | $0.06 | 240258 |
| 168 | $0.06 | 240504 |
| 169 | $0.06 | 240729 |
| 170 | $0.06 | 241093 |
| 171 | $0.06 | 241791 |
| 172 | $0.06 | 242070 |
| 173 | $0.06 | 242522 |
| 174 | $0.06 | 243974 |
| 175 | $0.07 | 244759 |
| 176 | $0.06 | 245940 |
| 177 | $0.08 | 248328 |
| 178 | $0.06 | 248804 |
| 179 | $0.06 | 249468 |
| 180 | $0.10 | 254373 |
| 181 | $0.07 | 256439 |
| 182 | $0.07 | 257328 |
| 183 | $0.57 | 87214 |
| 184 | $0.08 | 93902 |
| 185 | $0.04 | 95455 |
| 186 | $0.04 | 97066 |
| 187 | $0.04 | 97575 |
| 188 | $0.05 | 100725 |
| 189 | $0.04 | 101628 |
| 190 | $0.04 | 102705 |
| 191 | $0.05 | 105349 |
| 192 | $0.08 | 112128 |
| 193 | $0.04 | 112735 |
| 194 | $0.04 | 113933 |
| 195 | $0.05 | 116184 |
| 196 | $0.05 | 117857 |
| 197 | $0.04 | 118124 |
| 198 | $0.57 | 88033 |
| 199 | $0.09 | 94893 |
| 200 | $0.04 | 96478 |
| 201 | $0.04 | 97764 |
| 202 | $0.05 | 100520 |
| 203 | $0.06 | 103601 |
| 204 | $0.16 | 119285 |
| 205 | $0.04 | 119969 |
| 206 | $0.04 | 120533 |
| 207 | $0.06 | 123713 |
| 208 | $0.04 | 124697 |
| 209 | $0.04 | 125176 |
| 210 | $0.04 | 125802 |
| 211 | $0.04 | 126124 |
| 212 | $0.04 | 126527 |
| 213 | $0.04 | 126860 |
| 214 | $0.04 | 127741 |
| 215 | $0.07 | 131916 |
| 216 | $0.04 | 132447 |
| 217 | $0.04 | 132941 |
| 218 | $0.04 | 133671 |
| 219 | $0.05 | 134412 |
| 220 | $0.04 | 134633 |
| 221 | $0.05 | 135924 |
| 222 | $0.04 | 136871 |
| 223 | $0.04 | 137391 |
| 224 | $0.05 | 138518 |
| 225 | $0.04 | 139097 |
| 226 | $0.05 | 139900 |
| 227 | $0.04 | 140537 |
| 228 | $0.05 | 141532 |
| 229 | $0.04 | 142306 |
| 230 | $0.06 | 143783 |
| 231 | $0.05 | 145099 |
| 232 | $0.04 | 146209 |
| 233 | $0.06 | 148588 |
| 234 | $0.05 | 149283 |
| 235 | $0.05 | 150121 |
| 236 | $0.05 | 152206 |
| 237 | $0.05 | 153060 |
| 238 | $0.06 | 154980 |
| 239 | $0.05 | 155771 |
| 240 | $0.05 | 157183 |
| 241 | $0.11 | 165940 |
| 242 | $0.06 | 167319 |
| 243 | $0.05 | 168001 |
| 244 | $0.06 | 170225 |
| 245 | $0.05 | 171084 |
| 246 | $0.05 | 171811 |
| 247 | $0.05 | 172577 |
| 248 | $0.05 | 172939 |
| 249 | $0.06 | 174169 |
| 250 | $0.05 | 174626 |
| 251 | $0.05 | 175341 |
| 252 | $0.05 | 176113 |
| 253 | $0.05 | 176593 |
| 254 | $0.05 | 177397 |
| 255 | $0.05 | 177882 |
| 256 | $0.06 | 179259 |
| 257 | $0.05 | 180268 |
| 258 | $0.05 | 180722 |
| 259 | $0.06 | 181974 |
| 260 | $0.05 | 182697 |
| 261 | $0.06 | 183398 |
| 262 | $0.05 | 184227 |
| 263 | $0.06 | 185191 |
| 264 | $0.05 | 185941 |
| 265 | $0.06 | 187507 |
| 266 | $0.05 | 187881 |
| 267 | $0.07 | 189837 |
| 268 | $0.05 | 190990 |
| 269 | $0.07 | 192840 |
| 270 | $0.05 | 193124 |
| 271 | $0.06 | 194740 |
| 272 | $0.05 | 195045 |
| 273 | $0.06 | 196358 |
| 274 | $0.06 | 197333 |
| 275 | $0.06 | 197980 |
| 276 | $0.05 | 198503 |
| 277 | $0.05 | 198788 |
| 278 | $0.06 | 199646 |
| 279 | $0.06 | 199981 |
| 280 | $0.05 | 200706 |
| 281 | $0.07 | 202381 |
| 282 | $0.05 | 203223 |
| 283 | $0.06 | 203790 |
| 284 | $0.06 | 204694 |
| 285 | $0.05 | 205098 |
| 286 | $0.07 | 206427 |
| 287 | $0.05 | 207123 |
| 288 | $0.06 | 208178 |
| 289 | $0.06 | 208460 |
| 290 | $0.06 | 208967 |
| 291 | $0.05 | 209217 |
| 292 | $0.06 | 209798 |
| 293 | $0.07 | 212022 |
| 294 | $0.09 | 216989 |
| 295 | $0.07 | 218429 |
| 296 | $0.06 | 219246 |
| 297 | $0.07 | 220901 |
| 298 | $0.05 | 221161 |
| 299 | $0.58 | 88361 |
| 300 | $0.08 | 95516 |
| 301 | $0.04 | 97036 |
| 302 | $0.05 | 98927 |
| 303 | $0.05 | 101617 |
| 304 | $0.03 | 102202 |
| 305 | $0.06 | 105360 |
| 306 | $0.03 | 105684 |
| 307 | $0.05 | 107492 |
| 308 | $0.03 | 107842 |
| 309 | $0.04 | 108153 |
| 310 | $0.03 | 108456 |
| 311 | $0.04 | 108788 |
| 312 | $0.03 | 109049 |
| 313 | $0.04 | 109710 |
| 314 | $0.06 | 113642 |
| 315 | $0.07 | 118075 |
| 316 | $0.04 | 118836 |
| 317 | $0.04 | 119839 |
| 318 | $0.04 | 120397 |
| 319 | $0.08 | 126179 |
| 320 | $0.04 | 126536 |
| 321 | $0.04 | 127227 |
| 322 | $0.04 | 128004 |
| 323 | $0.05 | 129442 |
| 324 | $0.04 | 129736 |
| 325 | $0.04 | 130658 |
| 326 | $0.04 | 131146 |
| 327 | $0.04 | 131716 |
| 328 | $0.04 | 132438 |
| 329 | $0.04 | 132992 |
| 330 | $0.04 | 133351 |
| 331 | $0.05 | 134015 |
| 332 | $0.04 | 135317 |
| 333 | $0.05 | 135960 |
| 334 | $0.04 | 136994 |
| 335 | $0.05 | 137945 |
| 336 | $0.04 | 138301 |
| 337 | $0.04 | 139202 |
| 338 | $0.05 | 139975 |
| 339 | $0.04 | 140753 |
| 340 | $0.04 | 141410 |
| 341 | $0.04 | 141682 |
| 342 | $0.05 | 142673 |
| 343 | $0.05 | 143488 |
| 344 | $0.04 | 143823 |
| 345 | $0.05 | 144950 |
| 346 | $0.04 | 145864 |
| 347 | $0.06 | 147941 |
| 348 | $0.04 | 148839 |
| 349 | $0.11 | 156690 |
| 350 | $0.05 | 158180 |
| 351 | $0.05 | 159001 |
| 352 | $0.04 | 159484 |
| 353 | $0.06 | 161145 |
| 354 | $0.08 | 165856 |
| 355 | $0.05 | 166656 |
| 356 | $0.05 | 167343 |
| 357 | $0.04 | 167582 |
| 358 | $0.06 | 168958 |
| 359 | $0.58 | 88993 |
| 360 | $0.09 | 96147 |
| 361 | $0.04 | 97716 |
| 362 | $0.05 | 99607 |
| 363 | $0.05 | 102143 |
| 364 | $0.06 | 106645 |
| 365 | $0.06 | 110223 |
| 366 | $0.04 | 110844 |
| 367 | $0.06 | 114059 |
| 368 | $0.04 | 114441 |
| 369 | $0.04 | 115266 |
| 370 | $0.03 | 115502 |
| 371 | $0.05 | 117091 |
| 372 | $0.05 | 118707 |
| 373 | $0.07 | 123838 |
| 374 | $0.07 | 127697 |
| 375 | $0.05 | 129630 |
| 376 | $0.05 | 131663 |
| 377 | $0.58 | 89184 |
| 378 | $0.09 | 96337 |
| 379 | $0.04 | 97893 |
| 380 | $0.04 | 99389 |
| 381 | $0.05 | 101923 |
| 382 | $0.04 | 103724 |
| 383 | $0.06 | 106624 |
| 384 | $0.04 | 107854 |
| 385 | $0.03 | 108379 |
| 386 | $0.04 | 108831 |
| 387 | $0.04 | 109369 |
| 388 | $0.03 | 109724 |
| 389 | $0.04 | 110140 |
| 390 | $0.03 | 110553 |
| 391 | $0.04 | 111009 |
| 392 | $0.03 | 111764 |
| 393 | $0.04 | 112627 |
| 394 | $0.07 | 116719 |
| 395 | $0.04 | 117312 |
| 396 | $0.03 | 117798 |
| 397 | $0.04 | 118621 |
| 398 | $0.04 | 119223 |
| 399 | $0.04 | 119803 |
| 400 | $0.13 | 132061 |
| 401 | $0.06 | 134865 |
| 402 | $0.06 | 137415 |
| 403 | $0.05 | 139465 |
| 404 | $0.04 | 140123 |
| 405 | $0.05 | 141404 |
| 406 | $0.08 | 146563 |
| 407 | $0.04 | 147150 |
| 408 | $0.11 | 155259 |
| 409 | $0.05 | 156896 |
| 410 | $0.61 | 92622 |
| 411 | $0.09 | 100081 |
| 412 | $0.04 | 101652 |
| 413 | $0.04 | 103183 |
| 414 | $0.07 | 107740 |
| 415 | $0.03 | 108106 |
| 416 | $0.04 | 108443 |
| 417 | $0.03 | 108805 |
| 418 | $0.04 | 109109 |
| 419 | $0.03 | 109591 |
| 420 | $0.04 | 109965 |
| 421 | $0.03 | 110305 |
| 422 | $0.04 | 110953 |
| 423 | $0.04 | 111793 |
| 424 | $0.06 | 116057 |
| 425 | $0.04 | 116695 |
| 426 | $0.04 | 117162 |
| 427 | $0.04 | 117806 |
| 428 | $0.04 | 118454 |
| 429 | $0.03 | 118640 |
| 430 | $0.05 | 120511 |
| 431 | $0.04 | 121332 |
| 432 | $0.05 | 123709 |
| 433 | $0.05 | 125521 |
| 434 | $0.05 | 127065 |
| 435 | $0.05 | 128360 |
| 436 | $0.05 | 131206 |
| 437 | $0.05 | 132364 |
| 438 | $0.04 | 133001 |
| 439 | $0.05 | 134853 |
| 440 | $0.06 | 137480 |
| 441 | $0.04 | 138335 |
| 442 | $0.05 | 138921 |
| 443 | $0.05 | 140670 |
| 444 | $0.06 | 143525 |
| 445 | $0.05 | 144634 |
| 446 | $0.05 | 145988 |
| 447 | $0.04 | 147093 |
| 448 | $0.05 | 148237 |
| 449 | $0.05 | 148965 |
| 450 | $0.04 | 149845 |
| 451 | $0.08 | 154597 |
| 452 | $0.05 | 155360 |
| 453 | $0.05 | 157017 |
| 454 | $0.60 | 92855 |
| 455 | $0.08 | 100483 |
| 456 | $0.03 | 102052 |
| 457 | $0.03 | 103855 |
| 458 | $0.05 | 107345 |
| 459 | $0.03 | 108540 |
| 460 | $0.04 | 110683 |
| 461 | $0.03 | 111435 |
| 462 | $0.05 | 114968 |
| 463 | $0.03 | 115485 |
| 464 | $0.03 | 116024 |
| 465 | $0.03 | 116314 |
| 466 | $0.03 | 117190 |
| 467 | $0.03 | 117482 |
| 468 | $0.03 | 117853 |
| 469 | $0.03 | 118191 |
| 470 | $0.03 | 118950 |
| 471 | $0.06 | 123492 |
| 472 | $0.03 | 124149 |
| 473 | $0.03 | 124705 |
| 474 | $0.03 | 125516 |
| 475 | $0.03 | 126024 |
| 476 | $0.03 | 126893 |
| 477 | $0.03 | 127653 |
| 478 | $0.13 | 141114 |
| 479 | $0.05 | 143393 |
| 480 | $0.06 | 146907 |
| 481 | $0.05 | 149347 |
| 482 | $0.04 | 150521 |
| 483 | $0.05 | 153127 |
| 484 | $0.04 | 154012 |
| 485 | $0.05 | 156023 |
| 486 | $0.04 | 157199 |
| 487 | $0.07 | 162571 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 3 | 2 | 1 | 0 | 47 | 35 | 3 | 6 | 4483 | 17157 | 80717 | 0.25 |
| red | 67 | 26 | 2 | 0 | 4419 | 1416 | 379 | 710 | 140629 | 10393238 | 1598082 | 8.32 |
| green | 78 | 20 | 17 | 0 | 12899 | 1561 | 467 | 856 | 132154 | 12530479 | 1419335 | 6.98 |
| refactor | 27 | 6 | 0 | 0 | 1042 | 276 | 98 | 196 | 19331 | 2586277 | 474042 | 1.64 |
| red-missing | 9 | 0 | 0 | 0 | 449 | 193 | 37 | 72 | 22568 | 960940 | 225650 | 0.89 |
| pin | 8 | 8 | 0 | 0 | 395 | 143 | 34 | 62 | 11857 | 837613 | 124585 | 0.51 |
| red-supersede | 3 | 0 | 0 | 0 | 187 | 122 | 20 | 40 | 12045 | 653024 | 67180 | 0.35 |
| exhausted | 1 | 0 | 0 | 0 | 69 | 10 | 3 | 6 | 1040 | 75812 | 13050 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 82 | 62 | 20 | 0 | 9697 | 1321 | 364 | 676 | 115273 | 9136581 | 1381756 | 5.52 |
| developer | claude-sonnet-5-5 | 79 | 0 | 0 | 0 | 5826 | 1445 | 420 | 772 | 132243 | 11168034 | 1679926 | 6.96 |
| developer | claude-opus-5-5 | 35 | 0 | 0 | 0 | 3984 | 990 | 257 | 500 | 96591 | 7749925 | 940959 | 6.56 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 812 | 1.34 | 383 | 0.75 |
| green | 11147 | 6.12 | 1814 | 0.95 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 99 | 0.20 |
| pin | 0 | 0.00 | 69 | 0.08 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| preflight | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `status.sh --report` exits 0 and prints the section headings Landed, Running, Queue and Waiting, in that order (logic in `veri/status.py`, the `.sh` shim unchanged) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 50 | 22 | 38 | 5418 | 504788 | 93367 | 0.34 | 463 | unknown | 0/5 | nothing-left |  |  | full |
| With no `.tdd/report-cache.json` snapshot, Queue says there is no snapshot while Landed, Running and Waiting still print ⟦criterion 3⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 88 | 32 | 64 | 8551 | 868204 | 124603 | 0.60 | 743 | 1/2 | 0/5 | nothing-left |  |  | full |
| An empty Landed, Running or Waiting section keeps its heading and says "none" ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 20 | 40 | 5363 | 544342 | 72329 | 0.29 | 427 | unknown | 0/5 | nothing-left |  |  | full |
| With a snapshot present, Queue's first line states the snapshot's age, computed from its `fetched_at` ⟦criterion 3⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 121 | 34 | 68 | 10416 | 941759 | 132126 | 0.63 | 774 | 1/2 | 0/5 | nothing-left |  |  | full |
| Queue counts the snapshot's open opted-in (`VERI_LABEL`) issues by label ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 111 | 27 | 54 | 8038 | 764079 | 93081 | 0.39 | 712 | unknown | 1/5 | nothing-left |  |  | full |
| Queue lists each open opted-in issue the snapshot shows blocked, with the open issue blocking it, taken from that issue's `blockedBy` ⟦criterion 1⟧ | 12 | 4 | 1 | 0 | 0 | 0 | 178 | 65 | 124 | 19769 | 1773835 | 208804 | 1.13 | 1296 | 2/2 | 1/5 | nothing-left |  |  | already-satisfied |
| Landed lists one line per local `vN.M` tag, carrying the tag and its message (the capability) ⟦criterion 1⟧ | 14 | 3 | 3 | 0 | 0 | 0 | 383 | 98 | 188 | 37572 | 2974521 | 384281 | 2.01 | 2588 | red 2/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| Landed leaves out a tag cut before the time in `.tdd/status-last` ⟦criterion 1⟧ | 7 | 2 | 0 | 0 | 0 | 0 | 150 | 39 | 72 | 14843 | 989722 | 192410 | 0.95 | 1028 | 2/2 | 0/5 | nothing-left |  |  | full |
| Running lists one block headed `#<n>` for each run whose journal (`$VERI_HOME/runs/<owner>-<repo>/<n>.jsonl`) holds a `conductor-start` event whose `pid` answers `kill -0` with a start time matching its `started` ⟦criterion 1⟧ | 12 | 3 | 2 | 0 | 0 | 0 | 316 | 74 | 134 | 23701 | 1988251 | 249905 | 1.34 | 1309 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| Running leaves out a run whose journal's `conductor-start` pid is dead or whose start time does not match `started` ⟦criterion 1⟧ | 11 | 3 | 1 | 0 | 0 | 0 | 221 | 57 | 106 | 22235 | 1509848 | 217619 | 1.19 | 964 | 2/2 | 0/5 | structural-owed |  |  | already-satisfied |
| A Running block shows the run's steps ticked of planned: its journal's `step-done` events of the latest `plan` event's `steps` ⟦criterion 1⟧ | 7 | 2 | 0 | 0 | 0 | 0 | 144 | 48 | 88 | 15757 | 1316716 | 195417 | 1.08 | 981 | 2/2 | 0/5 | nothing-left |  |  | full |
| A Running block shows the run's phase now, from its journal's latest `launch` event ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 40 | 74 | 9826 | 1091663 | 95558 | 0.45 | 673 | unknown | 1/5 | nothing-left |  |  | full |
| A Running block shows the attempts in the run's current phase, from its journal's `launch` events ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 76 | 29 | 50 | 7953 | 721096 | 80644 | 0.35 | 595 | unknown | 0/5 | nothing-left |  |  | full |
| A Running block shows the run's PASS and REJECT verdict counts, from its journal's `verdict` events ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 83 | 27 | 48 | 6033 | 687039 | 78805 | 0.33 | 655 | unknown | 0/5 | nothing-left |  |  | full |
| A Running block shows the run's cost as the `| total |` row of its metrics, computed in-process from its journal ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 175 | 50 | 94 | 14643 | 1328367 | 201613 | 0.88 | 1739 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| A Running block shows the model each role (developer, revise, verifier, conductor) ran on, computed in-process from its journal ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 231 | 54 | 100 | 17406 | 1384024 | 218520 | 0.97 | 1654 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| Running's awake wall time for a run is its journal's last event's `awake` minus its first event's `awake` ⟦criterion 5⟧ | 17 | 5 | 0 | 0 | 0 | 0 | 353 | 92 | 170 | 32335 | 2420894 | 405923 | 2.05 | 1198 | 3/2 | 0/5 | nothing-left |  |  | full |
| Running's steps carry their delta since the time in `.tdd/status-last`: the run's `step-done` events after that time ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 118 | 23 | 42 | 7292 | 600281 | 84177 | 0.34 | 549 | unknown | 0/5 | nothing-left |  |  | full |
| Running's cost carries its delta since the time in `.tdd/status-last`: the cost of the run's journal events after that time ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 28 | 50 | 7515 | 716313 | 98703 | 0.39 | 603 | unknown | 1/5 | structural-owed |  |  | full |
| Queue's counts each carry their delta against the queue counts recorded in `.tdd/status-last` ⟦criterion 1⟧ | 16 | 6 | 2 | 0 | 0 | 0 | 283 | 75 | 140 | 24314 | 1975843 | 267906 | 1.11 | 12318 | unknown | 1/5 | nothing-left |  |  | already-satisfied |
| Waiting lists each bail since the time in `.tdd/status-last`, from the journals' `bail` events, with its cause ⟦criterion 1⟧ | 18 | 3 | 4 | 0 | 0 | 0 | 416 | 104 | 198 | 40644 | 2935798 | 426133 | 1.98 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `status.sh --report` exits 0 and prints the section headings Landed, Running, Queue and Waiting, in that order (logic in `veri/status.py`, the `.sh` shim unchanged) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| With no `.tdd/report-cache.json` snapshot, Queue says there is no snapshot while Landed, Running and Waiting still print ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 12 | 0.09 |
| An empty Landed, Running or Waiting section keeps its heading and says "none" ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 13 | 0.05 |
| With a snapshot present, Queue's first line states the snapshot's age, computed from its `fetched_at` ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 12 | 0.09 |
| Queue counts the snapshot's open opted-in (`VERI_LABEL`) issues by label ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 125 | 0.11 |
| Queue lists each open opted-in issue the snapshot shows blocked, with the open issue blocking it, taken from that issue's `blockedBy` ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 172 | 0.12 |
| Landed lists one line per local `vN.M` tag, carrying the tag and its message (the capability) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.08 |
| Landed leaves out a tag cut before the time in `.tdd/status-last` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 39 | 0.07 |
| Running lists one block headed `#<n>` for each run whose journal (`$VERI_HOME/runs/<owner>-<repo>/<n>.jsonl`) holds a `conductor-start` event whose `pid` answers `kill -0` with a start time matching its `started` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 26 | 0.05 |
| Running leaves out a run whose journal's `conductor-start` pid is dead or whose start time does not match `started` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 9 | 0.04 |
| A Running block shows the run's steps ticked of planned: its journal's `step-done` events of the latest `plan` event's `steps` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| A Running block shows the run's phase now, from its journal's latest `launch` event ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 171 | 0.15 |
| A Running block shows the attempts in the run's current phase, from its journal's `launch` events ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| A Running block shows the run's PASS and REJECT verdict counts, from its journal's `verdict` events ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 17 | 0.04 |
| A Running block shows the run's cost as the `| total |` row of its metrics, computed in-process from its journal ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.04 |
| A Running block shows the model each role (developer, revise, verifier, conductor) ran on, computed in-process from its journal ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.04 |
| Running's awake wall time for a run is its journal's last event's `awake` minus its first event's `awake` ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 16 | 0.05 |
| Running's steps carry their delta since the time in `.tdd/status-last`: the run's `step-done` events after that time ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 20 | 0.05 |
| Running's cost carries its delta since the time in `.tdd/status-last`: the cost of the run's journal events after that time ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 100 | 0.11 |
| Queue's counts each carry their delta against the queue counts recorded in `.tdd/status-last` ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 131 | 0.14 |
| Queue's counts each carry their delta against the queue counts recorded in `.tdd/status-last` ⟦criterion 1⟧ | 2 | 1/5 | nothing-left | PASS | 0 | 129 | 0.18 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s | run 147 s | run 148 s | run 149 s | run 150 s | run 151 s | run 152 s | run 153 s | run 154 s | run 155 s | run 156 s | run 157 s | run 158 s | run 159 s | run 160 s | run 161 s | run 162 s | run 163 s | run 164 s | run 165 s | run 166 s | run 167 s | run 168 s | run 169 s | run 170 s | run 171 s | run 172 s | run 173 s | run 174 s | run 175 s | run 176 s | run 177 s | run 178 s | run 179 s | run 180 s | run 181 s | run 182 s | run 183 s | run 184 s | run 185 s | run 186 s | run 187 s | run 188 s | run 189 s | run 190 s | run 191 s | run 192 s | run 193 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 6 | 12 | 12 | 6 | 6 | 8 | 10 | 11 | 11 | 6 | 6 | 6 | 11 | 8 | 10 | 14 | 10 | 8 | 6 | 9 | 7 | 6 | 11 | 11 | 8 | 9 | 7 | 5 | 5 | 5 | 9 | 7 | 9 | 13 | 8 | 1 | 9 | 7 | 8 | 17 | 17 | 9 | 9 | 7 | 11 | 14 | 13 | 7 | 8 | 17 | 11 | 9 | 9 | 11 | 12 | 18 | 18 | 16 | 11 | 9 | 12 | 10 | 15 | 9 | 13 | 8 | 10 | 12 | 8 | 12 | 8 | 11 | 7 | 9 | 8 | 9 | 8 | 8 | 11 | 0 | 12 | 9 | 10 | 9 | 10 | 10 | 12 | 12 | 13 | 9 | 11 | 12 | 8 | 8 | 11 | 10 | 8 | 7 | 7 | 11 | 11 | 9 | 10 | 9 | 13 | 11 | 9 | 9 | 7 | 8 | 19 | 17 | 11 | 11 | 13 | 33 | 17 | 23 | 26 | 23 | 15 | 11 | 12 | 16 | 13 | 18 | 19 | 11 | 11 | 12 | 11 | 10 | 9 | 10 | 15 | 11 | 10 | 7 | 8 | 9 | 7 | 6 | 6 | 11 | 10 | 6 | 5 | 7 | 11 | 6 | 6 | 9 | 6 | 7 | 6 | 6 | 9 | 10 | 6 | 10 | 14 | 8 | 9 | 6 | 5 | 7 | 10 | 7 | 9 | 8 | 9 | 7 | 11 | 0 | 13 | 14 | 9 | 16 | 10 | 9 | 9 | 6 | 11 | 11 | 14 | 13 | 9 | 3 | 2 | 4 | 8 | 6 |
| fast | 62 | 77 | 73 | 62 | 85 | 53 | 60 | 53 | 88 | 74 | 72 | 55 | 68 | 88 | 81 | 59 | 59 | 108 | 73 | 90 | 98 | 82 | 83 | 80 | 82 | 94 | 81 | 96 | 62 | 57 | 65 | 50 | 51 | 59 | 60 | 56 | 61 | 65 | 49 | 61 | 85 | 56 | 54 | 52 | 64 | 59 | 63 | 68 | 66 | 92 | 72 | 73 | 74 | 126 | 108 | 150 | 85 | 76 | 70 | 91 | 86 | 66 | 50 | 74 | 74 | 63 | 76 | 48 | 57 | 59 | 48 | 58 | 62 | 58 | 62 | 72 | 75 | 62 | 64 | 94 | 66 | 64 | 88 | 82 | 65 | 84 | 73 | 89 | 72 | 89 | 63 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 6 | 7 | 7 | 9 | 7 | 7 | 6 | 5 | 9 | 9 | 8 | 6 | 6 | 7 | 10 | 11 | 11 | 6 | 10 | 8 | 9 | 8 | 12 | 16 | 14 | 10 | 8 | 10 | 7 | 9 | 8 | 7 | 8 | 8 | 8 | 7 | 7 | 6 | 5 | 6 | 9 | 10 | 10 | 7 | 10 | 11 | 10 | 11 | 12 | 10 | 7 | 9 | 9 | 8 | 8 | 8 | 8 | 8 | 10 | 9 | 10 | 9 | 9 | 10 | 10 | 7 | 7 | 7 | 7 | 7 | 7 | 13 | 16 | 13 | 12 | 11 | 13 | 13 | 11 | 13 | 20 | 18 | 16 | 14 | 14 | 18 | 13 | 12 | 12 | 11 | 10 | 10 | 11 | 10 | 11 | 8 | 9 | 8 | 7 | 9 | 9 | 9 | 9 | 9 | 10 | 9 | 8 | 7 | 7 | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 6 | 8 | 7 | 6 | 5 | 5 | 5 | 5 | 6 | 5 | 5 | 5 | 6 | 6 | 7 | 6 | 6 | 5 | 5 | 5 | 6 | 7 | 6 | 6 | 6 | 5 | 5 | 7 | 7 | 7 | 8 | 7 | 7 | 7 | 7 | 6 | 7 | 8 | 9 | 10 | 7 | 8 | 8 | 6 | 6 | 7 | 6 | 10 | 9 | 6 | 8 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 1041 | 1948 | 344107 | 28054540 | 4002641 | 48.12 (estimate) |
