### 📊 Metrics — issue 2173

Wall time for the issue: 964 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 21 of 22 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2240.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $25.06 over 464 turns, in 7 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88838 tokens, largest 207496 tokens
Conductor context: first turn 89063 tokens, largest 154070 tokens
Conductor context: first turn 89200 tokens, largest 143269 tokens
Conductor context: first turn 89504 tokens, largest 183628 tokens
Conductor context: first turn 90043 tokens, largest 153532 tokens
Conductor context: first turn 90404 tokens, largest 183302 tokens
Conductor context: first turn 90405 tokens, largest 129967 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88838 |
| 2 | $0.04 | 90751 |
| 3 | $0.05 | 92844 |
| 4 | $0.03 | 93166 |
| 5 | $0.03 | 93573 |
| 6 | $0.03 | 93864 |
| 7 | $0.03 | 94187 |
| 8 | $0.03 | 94801 |
| 9 | $0.03 | 95167 |
| 10 | $0.06 | 98092 |
| 11 | $0.04 | 99838 |
| 12 | $0.03 | 100409 |
| 13 | $0.04 | 101921 |
| 14 | $0.04 | 102615 |
| 15 | $0.04 | 103920 |
| 16 | $0.06 | 107360 |
| 17 | $0.03 | 107922 |
| 18 | $0.04 | 108556 |
| 19 | $0.04 | 109142 |
| 20 | $0.03 | 110199 |
| 21 | $0.05 | 111719 |
| 22 | $0.04 | 113118 |
| 23 | $0.04 | 113508 |
| 24 | $0.04 | 114391 |
| 25 | $0.03 | 114736 |
| 26 | $0.04 | 115410 |
| 27 | $0.04 | 116277 |
| 28 | $0.03 | 116829 |
| 29 | $0.04 | 117680 |
| 30 | $0.04 | 118277 |
| 31 | $0.04 | 119227 |
| 32 | $0.04 | 119928 |
| 33 | $0.04 | 120357 |
| 34 | $0.04 | 120909 |
| 35 | $0.03 | 121327 |
| 36 | $0.04 | 121797 |
| 37 | $0.04 | 122975 |
| 38 | $0.04 | 123568 |
| 39 | $0.05 | 124735 |
| 40 | $0.04 | 125397 |
| 41 | $0.04 | 126351 |
| 42 | $0.04 | 127790 |
| 43 | $0.04 | 128211 |
| 44 | $0.04 | 128611 |
| 45 | $0.05 | 130416 |
| 46 | $0.04 | 130647 |
| 47 | $0.05 | 132527 |
| 48 | $0.04 | 133164 |
| 49 | $0.04 | 133652 |
| 50 | $0.04 | 134518 |
| 51 | $0.04 | 134913 |
| 52 | $0.10 | 142385 |
| 53 | $0.04 | 143483 |
| 54 | $0.05 | 144180 |
| 55 | $0.04 | 144859 |
| 56 | $0.04 | 145573 |
| 57 | $0.05 | 146284 |
| 58 | $0.06 | 148580 |
| 59 | $0.04 | 148991 |
| 60 | $0.04 | 149860 |
| 61 | $0.05 | 150509 |
| 62 | $0.04 | 151208 |
| 63 | $0.05 | 151718 |
| 64 | $0.04 | 152284 |
| 65 | $0.04 | 152652 |
| 66 | $0.05 | 153332 |
| 67 | $0.04 | 153806 |
| 68 | $0.05 | 154422 |
| 69 | $0.05 | 155205 |
| 70 | $0.04 | 155645 |
| 71 | $0.05 | 156331 |
| 72 | $0.05 | 157469 |
| 73 | $0.05 | 158712 |
| 74 | $0.04 | 159339 |
| 75 | $0.05 | 160356 |
| 76 | $0.05 | 160817 |
| 77 | $0.04 | 161155 |
| 78 | $0.05 | 162003 |
| 79 | $0.05 | 162598 |
| 80 | $0.04 | 162964 |
| 81 | $0.05 | 163905 |
| 82 | $0.05 | 164774 |
| 83 | $0.05 | 165398 |
| 84 | $0.04 | 165992 |
| 85 | $0.05 | 166354 |
| 86 | $0.05 | 167172 |
| 87 | $0.05 | 167719 |
| 88 | $0.04 | 168183 |
| 89 | $0.05 | 169036 |
| 90 | $0.05 | 169416 |
| 91 | $0.05 | 170183 |
| 92 | $0.05 | 170797 |
| 93 | $0.05 | 171481 |
| 94 | $0.05 | 172346 |
| 95 | $0.04 | 172835 |
| 96 | $0.05 | 173542 |
| 97 | $0.05 | 174185 |
| 98 | $0.05 | 174567 |
| 99 | $0.05 | 175691 |
| 100 | $0.05 | 176568 |
| 101 | $0.05 | 177220 |
| 102 | $0.05 | 177811 |
| 103 | $0.06 | 178932 |
| 104 | $0.05 | 179902 |
| 105 | $0.05 | 180409 |
| 106 | $0.05 | 181557 |
| 107 | $0.05 | 182009 |
| 108 | $0.05 | 182258 |
| 109 | $0.05 | 182869 |
| 110 | $0.06 | 184118 |
| 111 | $0.05 | 185239 |
| 112 | $0.05 | 185686 |
| 113 | $0.05 | 186244 |
| 114 | $0.06 | 187117 |
| 115 | $0.05 | 187468 |
| 116 | $0.05 | 188011 |
| 117 | $0.05 | 188695 |
| 118 | $0.05 | 189417 |
| 119 | $0.05 | 189713 |
| 120 | $0.06 | 190623 |
| 121 | $0.05 | 191608 |
| 122 | $0.05 | 191858 |
| 123 | $0.06 | 192362 |
| 124 | $0.05 | 192921 |
| 125 | $0.05 | 193600 |
| 126 | $0.05 | 193987 |
| 127 | $0.05 | 194524 |
| 128 | $0.06 | 195312 |
| 129 | $0.05 | 195787 |
| 130 | $0.05 | 196276 |
| 131 | $0.06 | 197327 |
| 132 | $0.05 | 197884 |
| 133 | $0.06 | 198557 |
| 134 | $0.05 | 199259 |
| 135 | $0.06 | 200061 |
| 136 | $0.06 | 201223 |
| 137 | $0.05 | 201696 |
| 138 | $0.06 | 202293 |
| 139 | $0.05 | 202850 |
| 140 | $0.05 | 203347 |
| 141 | $0.06 | 203922 |
| 142 | $0.05 | 204432 |
| 143 | $0.06 | 204849 |
| 144 | $0.06 | 205988 |
| 145 | $0.05 | 207037 |
| 146 | $0.06 | 207496 |
| 147 | $0.58 | 89063 |
| 148 | $0.05 | 91536 |
| 149 | $0.04 | 92290 |
| 150 | $0.04 | 93391 |
| 151 | $0.07 | 98576 |
| 152 | $0.04 | 98892 |
| 153 | $0.03 | 99303 |
| 154 | $0.03 | 99588 |
| 155 | $0.04 | 99867 |
| 156 | $0.03 | 100483 |
| 157 | $0.04 | 101382 |
| 158 | $0.05 | 103654 |
| 159 | $0.06 | 106422 |
| 160 | $0.04 | 107729 |
| 161 | $0.05 | 108896 |
| 162 | $0.03 | 109294 |
| 163 | $0.05 | 110801 |
| 164 | $0.08 | 116908 |
| 165 | $0.04 | 117388 |
| 166 | $0.04 | 117833 |
| 167 | $0.04 | 118607 |
| 168 | $0.04 | 119455 |
| 169 | $0.12 | 129998 |
| 170 | $0.05 | 130670 |
| 171 | $0.04 | 131131 |
| 172 | $0.05 | 132471 |
| 173 | $0.10 | 140936 |
| 174 | $0.05 | 142007 |
| 175 | $0.05 | 142854 |
| 176 | $0.04 | 143600 |
| 177 | $0.06 | 145129 |
| 178 | $0.04 | 145584 |
| 179 | $0.05 | 146195 |
| 180 | $0.04 | 146906 |
| 181 | $0.05 | 147526 |
| 182 | $0.07 | 151542 |
| 183 | $0.06 | 153043 |
| 184 | $0.05 | 154070 |
| 185 | $0.58 | 89200 |
| 186 | $0.03 | 89689 |
| 187 | $0.05 | 91955 |
| 188 | $0.03 | 92431 |
| 189 | $0.04 | 93897 |
| 190 | $0.05 | 96921 |
| 191 | $0.05 | 100280 |
| 192 | $0.07 | 104812 |
| 193 | $0.03 | 105245 |
| 194 | $0.04 | 105772 |
| 195 | $0.03 | 106068 |
| 196 | $0.03 | 106386 |
| 197 | $0.03 | 106659 |
| 198 | $0.04 | 107347 |
| 199 | $0.04 | 108012 |
| 200 | $0.03 | 108636 |
| 201 | $0.04 | 109289 |
| 202 | $0.04 | 110681 |
| 203 | $0.04 | 111565 |
| 204 | $0.03 | 111925 |
| 205 | $0.04 | 112456 |
| 206 | $0.04 | 113618 |
| 207 | $0.03 | 114226 |
| 208 | $0.04 | 115193 |
| 209 | $0.04 | 115821 |
| 210 | $0.04 | 116499 |
| 211 | $0.04 | 117563 |
| 212 | $0.03 | 118119 |
| 213 | $0.04 | 118546 |
| 214 | $0.09 | 125896 |
| 215 | $0.04 | 126787 |
| 216 | $0.04 | 127384 |
| 217 | $0.04 | 128164 |
| 218 | $0.06 | 131091 |
| 219 | $0.04 | 131666 |
| 220 | $0.04 | 132424 |
| 221 | $0.04 | 133471 |
| 222 | $0.05 | 134515 |
| 223 | $0.04 | 135389 |
| 224 | $0.04 | 136241 |
| 225 | $0.05 | 137134 |
| 226 | $0.06 | 141184 |
| 227 | $0.05 | 142218 |
| 228 | $0.05 | 143269 |
| 229 | $0.59 | 89504 |
| 230 | $0.03 | 90045 |
| 231 | $0.05 | 92311 |
| 232 | $0.03 | 93278 |
| 233 | $0.07 | 97422 |
| 234 | $0.05 | 100690 |
| 235 | $0.04 | 101142 |
| 236 | $0.03 | 101594 |
| 237 | $0.03 | 101843 |
| 238 | $0.04 | 102129 |
| 239 | $0.03 | 102836 |
| 240 | $0.04 | 103882 |
| 241 | $0.06 | 107285 |
| 242 | $0.04 | 107997 |
| 243 | $0.04 | 108809 |
| 244 | $0.04 | 109522 |
| 245 | $0.03 | 110184 |
| 246 | $0.05 | 111301 |
| 247 | $0.03 | 111928 |
| 248 | $0.06 | 114802 |
| 249 | $0.04 | 115699 |
| 250 | $0.09 | 122941 |
| 251 | $0.05 | 123811 |
| 252 | $0.04 | 124613 |
| 253 | $0.04 | 125489 |
| 254 | $0.04 | 125867 |
| 255 | $0.04 | 126365 |
| 256 | $0.04 | 127493 |
| 257 | $0.04 | 127792 |
| 258 | $0.05 | 128737 |
| 259 | $0.04 | 129360 |
| 260 | $0.04 | 129720 |
| 261 | $0.04 | 130432 |
| 262 | $0.04 | 131046 |
| 263 | $0.04 | 131659 |
| 264 | $0.05 | 132637 |
| 265 | $0.04 | 133434 |
| 266 | $0.04 | 134319 |
| 267 | $0.05 | 135032 |
| 268 | $0.04 | 135696 |
| 269 | $0.04 | 136351 |
| 270 | $0.04 | 136740 |
| 271 | $0.05 | 137950 |
| 272 | $0.05 | 139097 |
| 273 | $0.06 | 141567 |
| 274 | $0.05 | 142852 |
| 275 | $0.04 | 143119 |
| 276 | $0.04 | 143739 |
| 277 | $0.05 | 144353 |
| 278 | $0.05 | 145555 |
| 279 | $0.05 | 147107 |
| 280 | $0.05 | 148121 |
| 281 | $0.05 | 149249 |
| 282 | $0.04 | 150162 |
| 283 | $0.05 | 151414 |
| 284 | $0.05 | 152068 |
| 285 | $0.05 | 152927 |
| 286 | $0.05 | 153894 |
| 287 | $0.04 | 154402 |
| 288 | $0.06 | 156227 |
| 289 | $0.04 | 156481 |
| 290 | $0.06 | 158290 |
| 291 | $0.05 | 159423 |
| 292 | $0.06 | 160919 |
| 293 | $0.04 | 161691 |
| 294 | $0.06 | 163197 |
| 295 | $0.05 | 163975 |
| 296 | $0.05 | 165168 |
| 297 | $0.06 | 166904 |
| 298 | $0.05 | 167796 |
| 299 | $0.06 | 169228 |
| 300 | $0.05 | 170293 |
| 301 | $0.05 | 170692 |
| 302 | $0.05 | 172183 |
| 303 | $0.06 | 172980 |
| 304 | $0.04 | 173413 |
| 305 | $0.06 | 175094 |
| 306 | $0.05 | 175816 |
| 307 | $0.05 | 176242 |
| 308 | $0.06 | 177074 |
| 309 | $0.05 | 177752 |
| 310 | $0.08 | 181812 |
| 311 | $0.05 | 182615 |
| 312 | $0.05 | 183628 |
| 313 | $0.59 | 90043 |
| 314 | $0.05 | 92648 |
| 315 | $0.04 | 93410 |
| 316 | $0.04 | 95554 |
| 317 | $0.06 | 98821 |
| 318 | $0.03 | 99236 |
| 319 | $0.04 | 99761 |
| 320 | $0.03 | 100187 |
| 321 | $0.03 | 100600 |
| 322 | $0.07 | 104752 |
| 323 | $0.03 | 105337 |
| 324 | $0.04 | 106075 |
| 325 | $0.04 | 106769 |
| 326 | $0.04 | 108156 |
| 327 | $0.04 | 109417 |
| 328 | $0.05 | 111488 |
| 329 | $0.04 | 111977 |
| 330 | $0.04 | 112693 |
| 331 | $0.04 | 113391 |
| 332 | $0.03 | 113727 |
| 333 | $0.04 | 114377 |
| 334 | $0.04 | 115318 |
| 335 | $0.04 | 116223 |
| 336 | $0.05 | 117218 |
| 337 | $0.03 | 117650 |
| 338 | $0.04 | 118376 |
| 339 | $0.04 | 118899 |
| 340 | $0.04 | 119792 |
| 341 | $0.04 | 120508 |
| 342 | $0.04 | 121248 |
| 343 | $0.05 | 123059 |
| 344 | $0.10 | 130746 |
| 345 | $0.04 | 131622 |
| 346 | $0.05 | 132314 |
| 347 | $0.05 | 134407 |
| 348 | $0.05 | 135637 |
| 349 | $0.05 | 137393 |
| 350 | $0.04 | 137907 |
| 351 | $0.05 | 138779 |
| 352 | $0.04 | 139851 |
| 353 | $0.05 | 140698 |
| 354 | $0.04 | 141018 |
| 355 | $0.05 | 142382 |
| 356 | $0.04 | 143152 |
| 357 | $0.05 | 144292 |
| 358 | $0.05 | 145527 |
| 359 | $0.05 | 146173 |
| 360 | $0.05 | 147336 |
| 361 | $0.07 | 151479 |
| 362 | $0.05 | 152413 |
| 363 | $0.05 | 153532 |
| 364 | $0.60 | 90404 |
| 365 | $0.05 | 93161 |
| 366 | $0.03 | 93601 |
| 367 | $0.06 | 97478 |
| 368 | $0.05 | 99504 |
| 369 | $0.09 | 106187 |
| 370 | $0.03 | 106781 |
| 371 | $0.04 | 107310 |
| 372 | $0.04 | 107658 |
| 373 | $0.03 | 108125 |
| 374 | $0.04 | 108663 |
| 375 | $0.04 | 109394 |
| 376 | $0.04 | 110062 |
| 377 | $0.04 | 110745 |
| 378 | $0.04 | 111416 |
| 379 | $0.13 | 123697 |
| 380 | $0.06 | 126195 |
| 381 | $0.04 | 126845 |
| 382 | $0.04 | 127181 |
| 383 | $0.04 | 127587 |
| 384 | $0.04 | 128445 |
| 385 | $0.05 | 129601 |
| 386 | $0.05 | 130467 |
| 387 | $0.04 | 130871 |
| 388 | $0.04 | 131580 |
| 389 | $0.10 | 138738 |
| 390 | $0.05 | 140766 |
| 391 | $0.05 | 141773 |
| 392 | $0.06 | 144047 |
| 393 | $0.05 | 144939 |
| 394 | $0.04 | 145441 |
| 395 | $0.05 | 146888 |
| 396 | $0.06 | 148147 |
| 397 | $0.04 | 148751 |
| 398 | $0.05 | 149563 |
| 399 | $0.04 | 149932 |
| 400 | $0.06 | 152008 |
| 401 | $0.05 | 153001 |
| 402 | $0.05 | 153407 |
| 403 | $0.06 | 155299 |
| 404 | $0.05 | 156210 |
| 405 | $0.05 | 157221 |
| 406 | $0.05 | 158145 |
| 407 | $0.05 | 158693 |
| 408 | $0.05 | 159704 |
| 409 | $0.05 | 161057 |
| 410 | $0.05 | 161910 |
| 411 | $0.06 | 163448 |
| 412 | $0.05 | 164708 |
| 413 | $0.06 | 166400 |
| 414 | $0.06 | 167700 |
| 415 | $0.05 | 168656 |
| 416 | $0.06 | 169925 |
| 417 | $0.05 | 170604 |
| 418 | $0.05 | 171073 |
| 419 | $0.06 | 173028 |
| 420 | $0.06 | 174272 |
| 421 | $0.05 | 174696 |
| 422 | $0.06 | 176191 |
| 423 | $0.08 | 180918 |
| 424 | $0.05 | 181737 |
| 425 | $0.06 | 182753 |
| 426 | $0.05 | 183302 |
| 427 | $0.58 | 90405 |
| 428 | $0.02 | 90863 |
| 429 | $0.04 | 93495 |
| 430 | $0.03 | 95183 |
| 431 | $0.03 | 96499 |
| 432 | $0.04 | 98574 |
| 433 | $0.04 | 100540 |
| 434 | $0.03 | 101524 |
| 435 | $0.02 | 101990 |
| 436 | $0.03 | 102808 |
| 437 | $0.02 | 103126 |
| 438 | $0.02 | 103669 |
| 439 | $0.05 | 107413 |
| 440 | $0.03 | 107969 |
| 441 | $0.03 | 108489 |
| 442 | $0.03 | 108912 |
| 443 | $0.02 | 109154 |
| 444 | $0.03 | 109680 |
| 445 | $0.03 | 110401 |
| 446 | $0.04 | 112248 |
| 447 | $0.04 | 114410 |
| 448 | $0.03 | 115431 |
| 449 | $0.03 | 116674 |
| 450 | $0.03 | 117791 |
| 451 | $0.03 | 118311 |
| 452 | $0.05 | 121879 |
| 453 | $0.04 | 123486 |
| 454 | $0.03 | 124366 |
| 455 | $0.03 | 125452 |
| 456 | $0.03 | 126123 |
| 457 | $0.03 | 126537 |
| 458 | $0.03 | 127144 |
| 459 | $0.03 | 127674 |
| 460 | $0.03 | 128420 |
| 461 | $0.03 | 129129 |
| 462 | $0.03 | 129560 |
| 463 | $0.03 | 129967 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 10 | 1 | 2 | 1212 | 0 | 32084 | 0.09 |
| red | 45 | 17 | 1 | 0 | 1624 | 944 | 227 | 440 | 99037 | 6527819 | 1064553 | 5.29 |
| green | 56 | 14 | 13 | 0 | 4141 | 949 | 264 | 522 | 88059 | 7697486 | 853573 | 4.77 |
| refactor | 26 | 12 | 0 | 0 | 604 | 177 | 76 | 146 | 15336 | 1870417 | 386216 | 1.31 |
| red-missing | 1 | 0 | 0 | 0 | 47 | 14 | 3 | 6 | 1651 | 82704 | 17081 | 0.07 |
| pin | 5 | 5 | 0 | 0 | 149 | 71 | 22 | 44 | 7300 | 589980 | 93312 | 0.37 |
| prose | 12 | 0 | 0 | 0 | 149 | 97 | 12 | 24 | 14943 | 16978 | 108559 | 0.42 |
| skill-edit | 3 | 0 | 0 | 0 | 35 | 22 | 9 | 16 | 2278 | 191541 | 31450 | 0.12 |
| cover | 4 | 0 | 0 | 0 | 128 | 59 | 21 | 42 | 6209 | 569862 | 96585 | 0.36 |
| predicate | 4 | 0 | 0 | 2 | 25 | 17 | 7 | 14 | 1113 | 183289 | 25054 | 0.09 |
| structural | 2 | 0 | 0 | 0 | 52 | 29 | 9 | 18 | 3473 | 251185 | 29461 | 0.13 |
| transform | 2 | 2 | 0 | 0 | 47 | 22 | 7 | 14 | 2210 | 149977 | 62741 | 0.19 |
| diff | 3 | 0 | 0 | 0 | 169 | 40 | 10 | 20 | 2932 | 241625 | 64051 | 0.33 |
| exhausted | 4 | 0 | 0 | 0 | 1428 | 79 | 12 | 24 | 4865 | 284082 | 88325 | 0.60 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 66 | 51 | 14 | 0 | 3317 | 756 | 240 | 476 | 74616 | 6445582 | 991119 | 3.87 |
| developer | claude-sonnet-5-5 | 57 | 0 | 0 | 2 | 2146 | 778 | 260 | 502 | 83582 | 7235489 | 1063759 | 4.43 |
| developer | claude-opus-5-5 | 30 | 0 | 0 | 0 | 2965 | 877 | 159 | 314 | 75199 | 4767355 | 758158 | 5.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 284 | 1.26 | 48 | 0.15 |
| green | 5050 | 7.07 | 341 | 0.61 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 12 | 0.03 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 96 | 0.26 |
| predicate | 0 | 0.00 | 9 | 0.04 |
| structural | 0 | 0.00 | 22 | 0.07 |
| transform | 0 | 0.00 | 19 | 0.10 |
| diff | 0 | 0.00 | 169 | 0.33 |
| exhausted | 0 | 0.00 | 993 | 0.34 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/tdd/scripts/merge-lock.sh` exists as a `/bin/sh` shim over `skills/tdd/scripts/veri/merge_lock.py` (the port convention, `status.sh` its example): with no argument, or a verb other than `take`, `release` or `holder`, it prints a usage line naming the three verbs on stderr and exits 2; `skills/tdd/SCRIPTS.md` carries its entry as an operator script the conductor does not call (veri-merge's and veri-handoff's), so `unreachable.sh` does not list it as unreached ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 63 | 25 | 48 | 6926 | 657246 | 111203 | 0.41 | 397 | unknown | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh holder` exits 3 and prints nothing on stdout when no `.tdd/merge.lock` exists in the main working tree of the repository it is run in, also when run from a linked worktree of it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 70 | 28 | 54 | 7299 | 765886 | 90890 | 0.38 | 343 | unknown | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh take` creates `.tdd/merge.lock` in the repository's main working tree (also when run from a linked worktree) atomically, as a directory, recording inside it the holder's pid (the caller's: the parent process of `merge-lock.sh`, or the pid `--pid <pid>` names), the host and the start time, and exits 0; `merge-lock.sh holder` then prints that pid, host and start time and exits 0 while that pid is live ⟦criterion 1⟧ | 11 | 4 | 1 | 0 | 0 | 0 | 122 | 39 | 76 | 12935 | 1026954 | 173257 | 0.76 | 654 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| `merge-lock.sh holder` exits 1 when the lock's recorded pid is dead on this host, printing the record marked as a stale lock ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 89 | 28 | 54 | 7863 | 715935 | 122934 | 0.56 | 538 | 1/2 | 0/5 | structural-owed |  |  | full |
| `merge-lock.sh holder` exits 2 when `.tdd/merge.lock` exists but its record is missing, unreadable or malformed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 22 | 3845 | 324273 | 33162 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `merge-lock.sh release` removes `.tdd/merge.lock` and exits 0 only when the caller (identified as `take` identifies it) is the recorded holder; a caller who is not the holder gets exit 1 with the lock left in place, and `release --force` removes the lock whoever holds it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 82 | 27 | 52 | 7874 | 738856 | 95763 | 0.39 | 409 | unknown | 1/5 | nothing-left |  |  | full |
| `merge-lock.sh take` waits while another live holder has the lock, polling at an interval read as `${VERI_MERGE_LOCK_POLL:-30}` seconds, and takes it once it is released: two takers racing for a free lock end with exactly one holding it while the other is still waiting, and the waiter takes it after the winner's release (a medium case with real processes, `@pytest.mark.process`) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 86 | 24 | 46 | 8742 | 644609 | 94720 | 0.39 | 379 | unknown | 0/5 | nothing-left |  |  | full |
| A stale lock (recorded pid dead on this host) is never removed silently: `merge-lock.sh take` on it reports the stale holder on stderr and keeps waiting with the lock left in place, and only `merge-lock.sh release --force` clears it, after which a waiting `take` gets it ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 76 | 25 | 50 | 7613 | 704485 | 93654 | 0.38 | 439 | unknown | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh release` and `merge-lock.sh take` exit 2 when `.tdd/merge.lock` exists but its record is missing, unreadable or malformed, as `holder` does, leaving the lock in place ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 12 | 24 | 4567 | 367254 | 36745 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/veri-merge/REQUIREMENTS.md`'s M4 is replaced by the issue's M4 row exactly as the issue states it, `skills/veri-merge/SKILL.md` states it in its prose (taking the lock with `$S/merge-lock.sh take` before its first write, releasing it with `$S/merge-lock.sh release` on every exit path, and leaving it held and saying so on a conflict or a refused push), the unit grades PASS against its whole list and `GRADED` carries a line whose signature matches its current text ⟦skill-edit⟧ ⟦criterion 3⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 26 | 5 | 10 | 3851 | 75152 | 29581 | 0.12 | 70 | unknown | unknown | unknown |  |  | full |
| `skills/veri-handoff/REQUIREMENTS.md`'s H2 is replaced by the issue's H2 row exactly as the issue states it, `skills/veri-handoff/SKILL.md` states it in its prose (for the dev role, refusing while `$S/merge-lock.sh holder` names a live holder, or a launch is half done), the unit grades PASS against its whole list and `GRADED` carries a line whose signature matches its current text ⟦skill-edit⟧ ⟦criterion 3⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 23 | 4 | 8 | 2723 | 47469 | 25555 | 0.10 | 60 | unknown | unknown | unknown |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_tunable_reads.py — FAILED test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment (and test_run_leaf_run_verdict_and_stop_run_take_their_veri_values_from_the_one_reader_and_no_module_is_exempt): AssertionError: assert [`.../skills/tdd/scripts/veri/merge_lock.py:43`] == [] (merge_lock.py reads a VERI_ name from the environment outside the one reader); skills/tdd/scripts/tests/py/test_github_sh.py — FAILED test_the_gh_function_reads_a_fast_wait_of_015_as_15_decimal_seconds_sleeping_the_retry_interval_until_then_issue_2132 - AssertionError: gh: not found on PATH, retrying in 2s ⟦suite-repair⟧ ⟦criterion 3⟧ | 12 | 4 | 0 | 1 | 0 | 0 | 126 | 46 | 88 | 12225 | 1165449 | 239986 | 0.84 | 3061 | unknown | 0/5 | nothing-left |  |  | full |
| the case `test_take_without_pid_records_the_parent_process_of_the_caller_and_holder_prints_it` is deleted from `skills/tdd/scripts/tests/py/test_merge_lock.py`, since it pins `take` without `--pid` recording the caller parent process, the behaviour criterion 4 removes; no other test and no production file changes ⟦diff-checked⟧ ⟦criterion 4⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 68 | 13 | 26 | 4367 | 288450 | 106583 | 0.58 | unknown | 2/2 | unknown | unknown |  |  | full |
| `merge-lock.sh take` with no `--pid <pid>`, and `merge-lock.sh release` with neither `--pid <pid>` nor `--force`, exit 2 with a stderr line naming `--pid`, creating no lock and removing none ⟦criterion 4⟧ | 16 | 4 | 3 | 0 | 0 | 0 | 303 | 70 | 140 | 26536 | 1980922 | 339388 | 1.75 | 477 | green 2/2, red 1/2 | 0/5 | structural-owed |  |  | full |
| with `--pid`, the lock stays live across separate shell calls for as long as that pid lives: `merge-lock.sh take --pid <long-lived pid>` run in one shell, then `merge-lock.sh holder` run in a later, separate shell reports that holder live and exits 0 (a medium case with real processes, `@pytest.mark.process`, in `skills/tdd/scripts/tests/py/test_merge_lock_process.py`) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 9 | 18 | 3070 | 263617 | 33479 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| `merge-lock.sh take` records the holder pid own process start time, and `merge-lock.sh holder` reads a record whose pid is alive but whose recorded start time differs from that process start time (pid reuse) as a stale lock: it prints the record marked stale and exits 1 ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 71 | 24 | 46 | 8315 | 649808 | 100183 | 0.40 | 278 | unknown | 1/5 | structural-owed |  |  | full |
| `merge-lock.sh holder` reports a live holder pid owned by another user (such as pid 1) as live, printing the record and exiting 0, not crashing ⟦criterion 6⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 98 | 30 | 60 | 9339 | 867488 | 133818 | 0.67 | 326 | 1/2 | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh take` on a lock whose record is missing, unreadable or malformed exits 2 with stderr naming the record path, instead of waiting, and leaves the lock in place ⟦criterion 6⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 156 | 39 | 78 | 13337 | 1145503 | 142447 | 0.85 | unknown | 2/2 | unknown | unknown |  |  | full |
| `merge-lock.sh take` makes the lock visible only once its holder record is complete: it writes the record in a temporary directory beside `.tdd/merge.lock` and renames that directory into place, so no other `take` or `holder` ever sees the lock directory without its full record; pinned by a case that observes the lock directory only with a complete record ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 89 | 23 | 46 | 8960 | 617981 | 135441 | 0.49 | 326 | unknown | 1/5 | nothing-left |  |  | full |
| `merge-lock.sh take` on a lock whose record is missing, unreadable or malformed (an empty record, a non-integer pid) exits 2 with stderr naming the record path, instead of waiting, and leaves the lock in place; pinned by one case each for a missing, an unreadable and a malformed record ⟦criterion 6⟧ | 23 | 3 | 6 | 0 | 0 | 0 | 628 | 122 | 240 | 58693 | 3811604 | 433436 | 3.16 | 851 | red 4/2, green 4/2 | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh take` against a live holder owned by another user (where `os.kill` raises `PermissionError`) waits on it as a live holder, never refusing; pinned by a case ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 14 | 26 | 5297 | 380660 | 54709 | 0.23 | unknown | unknown | unknown | unknown |  |  | pin |
| `merge-lock.sh release --pid <pid>` and `merge-lock.sh release --force` with no lock exit 3, and the usage line printed on a missing or unknown verb names `--pid` and `--force` beside the three verbs ⟦criterion 6⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 49 | 21 | 40 | 5673 | 572592 | 84764 | 0.33 | 240 | unknown | 0/5 | nothing-left |  |  | full |
| `skills/veri-merge/REQUIREMENTS.md` M4 is replaced by the issue amended M4 row exactly as the issue states it (take and release naming `--pid <driver>`, a human clearing with `release --force`), `skills/veri-merge/SKILL.md` states amended M4 in its prose, and the unit grades PASS against its whole list and `GRADED` carries a line whose signature matches its current text ⟦skill-edit⟧ ⟦criterion 7⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 27 | 6 | 10 | 4270 | 77409 | 30911 | 0.13 | 71 | unknown | unknown | unknown |  |  | full |
| `skills/veri-handoff/SKILL.md` no longer states the "a merge is in flight" refusal that H2 does not name, keeping the `$S/merge-lock.sh holder` live-holder and half-done-launch refusals, and the unit grades PASS against its whole list and `GRADED` carries a line whose signature matches its current text ⟦skill-edit⟧ ⟦criterion 7⟧ | 8 | 1 | 0 | 1 | 0 | 0 | 89 | 29 | 58 | 9787 | 760422 | 132998 | 0.51 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `skills/tdd/scripts/merge-lock.sh` exists as a `/bin/sh` shim over `skills/tdd/scripts/veri/merge_lock.py` (the port convention, `status.sh` its example): with no argument, or a verb other than `take`, `release` or `holder`, it prints a usage line naming the three verbs on stderr and exits 2; `skills/tdd/SCRIPTS.md` carries its entry as an operator script the conductor does not call (veri-merge's and veri-handoff's), so `unreachable.sh` does not list it as unreached ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 44 | 0.09 |
| `merge-lock.sh holder` exits 3 and prints nothing on stdout when no `.tdd/merge.lock` exists in the main working tree of the repository it is run in, also when run from a linked worktree of it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 46 | 0.09 |
| `merge-lock.sh take` creates `.tdd/merge.lock` in the repository's main working tree (also when run from a linked worktree) atomically, as a directory, recording inside it the holder's pid (the caller's: the parent process of `merge-lock.sh`, or the pid `--pid <pid>` names), the host and the start time, and exits 0; `merge-lock.sh holder` then prints that pid, host and start time and exits 0 while that pid is live ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 47 | 0.09 |
| `merge-lock.sh holder` exits 1 when the lock's recorded pid is dead on this host, printing the record marked as a stale lock ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 65 | 0.10 |
| `merge-lock.sh release` removes `.tdd/merge.lock` and exits 0 only when the caller (identified as `take` identifies it) is the recorded holder; a caller who is not the holder gets exit 1 with the lock left in place, and `release --force` removes the lock whoever holds it ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 70 | 0.11 |
| `merge-lock.sh take` waits while another live holder has the lock, polling at an interval read as `${VERI_MERGE_LOCK_POLL:-30}` seconds, and takes it once it is released: two takers racing for a free lock end with exactly one holding it while the other is still waiting, and the waiter takes it after the winner's release (a medium case with real processes, `@pytest.mark.process`) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.09 |
| A stale lock (recorded pid dead on this host) is never removed silently: `merge-lock.sh take` on it reports the stale holder on stderr and keeps waiting with the lock left in place, and only `merge-lock.sh release --force` clears it, after which a waiting `take` gets it ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 48 | 0.10 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_tunable_reads.py — FAILED test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment (and test_run_leaf_run_verdict_and_stop_run_take_their_veri_values_from_the_one_reader_and_no_module_is_exempt): AssertionError: assert [`.../skills/tdd/scripts/veri/merge_lock.py:43`] == [] (merge_lock.py reads a VERI_ name from the environment outside the one reader); skills/tdd/scripts/tests/py/test_github_sh.py — FAILED test_the_gh_function_reads_a_fast_wait_of_015_as_15_decimal_seconds_sleeping_the_retry_interval_until_then_issue_2132 - AssertionError: gh: not found on PATH, retrying in 2s ⟦suite-repair⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.13 |
| `merge-lock.sh take` with no `--pid <pid>`, and `merge-lock.sh release` with neither `--pid <pid>` nor `--force`, exit 2 with a stderr line naming `--pid`, creating no lock and removing none ⟦criterion 4⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 36 | 0.09 |
| `merge-lock.sh take` records the holder pid own process start time, and `merge-lock.sh holder` reads a record whose pid is alive but whose recorded start time differs from that process start time (pid reuse) as a stale lock: it prints the record marked stale and exits 1 ⟦criterion 5⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 45 | 0.12 |
| `merge-lock.sh holder` reports a live holder pid owned by another user (such as pid 1) as live, printing the record and exiting 0, not crashing ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 40 | 0.09 |
| `merge-lock.sh take` makes the lock visible only once its holder record is complete: it writes the record in a temporary directory beside `.tdd/merge.lock` and renames that directory into place, so no other `take` or `holder` ever sees the lock directory without its full record; pinned by a case that observes the lock directory only with a complete record ⟦criterion 6⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 53 | 0.11 |
| `merge-lock.sh take` on a lock whose record is missing, unreadable or malformed (an empty record, a non-integer pid) exits 2 with stderr naming the record path, instead of waiting, and leaves the lock in place; pinned by one case each for a missing, an unreadable and a malformed record ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |
| `merge-lock.sh release --pid <pid>` and `merge-lock.sh release --force` with no lock exit 3, and the usage line printed on a missing or unknown verb names `--pid` and `--force` beside the three verbs ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 11 | 27 | 10 | 12 | 9 | 11 | 9 | 11 | 11 | 10 | 11 | 12 | 12 | 13 | 12 | 3 | 12 | 3 | 7 | 16 | 26 | 13 | 13 | 13 | 15 | 9 | 10 | 11 | 4 | 10 | 10 | 10 | 10 | 10 | 11 | 12 | 12 | 11 | 11 | 0 | 13 | 11 | 23 | 23 | 18 | 9 | 8 | 11 | 11 | 10 | 0 | 13 | 18 | 12 | 10 | 20 | 10 | 13 | 4 | 3 | 3 | 10 | 10 | 10 | 11 | 17 | 10 | 10 | 10 | 11 | 33 | 4 | 4 | 5 | 3 | 2 | 4 | 5 | 3 | 3 | 4 | 5 | 4 | 4 | 5 | 4 | 4 | 4 | 2 | 4 | 6 | 3 | 2 | 2 | 4 | 7 | 2 | 4 | 3 | 4 | 3 | 4 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 5 | 4 | 4 | 2 | 3 | 4 | 6 | 2 | 4 | 5 | 7 | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 5 | 4 | 4 | 3 | 4 | 4 | 1 | 7 | 1 | 5 | 6 | 15 | 5 | 5 |
| fast | 16 | 17 | 18 | 16 | 18 | 16 | 18 | 20 | 31 | 19 | 20 | 39 | 27 | 20 | 17 | 22 | 21 | 19 | 18 | 17 | 16 | 16 | 18 | 37 | 60 | 17 | 104 | 25 | 15 | 13 | 50 | 15 | 35 | 15 | 53 | 14 | 13 | 13 | 14 | 27 | 16 | 15 | 15 | 15 | 15 | 17 | 17 | 17 | 16 | 16 | 21 | 15 | 55 | 17 | 16 | 22 | 22 | 22 | 22 | 24 | 25 | 23 | 23 | 22 | 23 | 24 | 23 | 22 | 23 | 23 | 22 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 10 | 10 | 13 | 12 | 14 | 12 | 4 | 12 | 3 | 3 | 10 | 12 | 12 | 4 | 4 | 3 | 10 | 14 | 11 | 10 | 0 | 1 | 3 | 4 | 4 | 7 | 7 | 3 | 4 | 4 | 4 | 0 | 4 | 0 | 3 | 2 | 1 | 1 | 1 | 3 | 4 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 680 | 1332 | 250618 | 18656945 | 2953045 | 14.14 |
