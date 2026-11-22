# Conductor cost audit: the 122 hot conductor turns of veri-dashboard runs #13, #26 and #27

Issue #4574. Read-only measurement; no production or test file changes. Sources: `~/.veri/runs/ztrange-veri-dashboard/{13,26,27}.*` (journals and `metrics.json`), the runs' `issue-<n>-metrics.md` per-turn tables, and each run's conductor stream log `conductor-<n>.log` (the only record of what a turn read or ran). A *hot* turn is one whose recorded dollars are at or above $0.50 in `Conductor per turn`: 33 in #13, 25 in #26, 64 in #27 (122 turns, $97.23).

## Finding

**The dominant cause is a measurement artifact, not conductor behaviour: $93.06 of the $97.23 (95.7%) is dollars the recorded per-turn table attributes to a turn that the turn did not spend.** The conductor is one long-lived `claude` session that is woken once per finished leaf, and each wake ends in a `result` record whose `total_cost_usd` is cumulative over the whole session. The metrics that produced the recorded tables treated each wake's `total_cost_usd` as that wake's own spend and spread its remainder evenly over the wake's turns, so every wake re-billed all earlier spend. The 122 hot turns, priced from their own usage (the same pricing `metrics.py` applies to a turn's non-output tokens), cost **$4.17** (4.3%).

Evidence the totals are cumulative: in #27 one session id `f326a61d` returns 18 `result` records whose `total_cost_usd` rises monotonically 2.16 → 7.50 while the sum of the 18 figures is $81.88; the recorded conductor spend ($74.87 in `27.metrics.json`) is that kind of sum, the true session spend is its last value, $7.50.

| run | recorded conductor spend | conductor spend from the last cumulative total of each session | hot turns | hot $ recorded | hot $ from the turns' own usage |
|---|---:|---:|---:|---:|---:|
| #13 | $58.84 | $20.04 | 33 | $28.77 | $0.87 |
| #26 | $35.07 | $7.01 | 25 | $15.31 | $1.11 |
| #27 | $74.85 | $7.50 | 64 | $53.15 | $2.19 |
| total | $168.76 | $34.55 | 122 | $97.23 | $4.17 |

Recorded spend is the sum of every turn row in the run's `issue-<n>-metrics.md`; the second column is the last `total_cost_usd` of each contiguous session id in the stream log (#13: 6.60 + 3.66 + 1.70 + 5.44 + 2.64; #26: 3.24 + 3.77; #27: 7.50), which equals the sum of the turns' own usage ($20.04, $7.01, $7.52). The current `metrics.py` (after #4599's wake handling) already reproduces the second column; it was run over these three logs to take the per-turn figures in the last column.

## Hot turns grouped by cause

| cause | turns | $ recorded | $ from own usage | share of the recorded $97.23 |
|---|---:|---:|---:|---:|
| 1. each wake's cumulative `total_cost_usd` re-billed to the wake's turns (all 122 turns) | 122 | $93.06 | n/a | 95.7% |
| 2. the turns' own usage (cache reads of a 47k–117k token context, plus a few cache writes) | 122 | $4.17 | $4.17 | 4.3% |

The 122 hot turns by what they read or ran (a turn is assigned by the tool call in its message; both dollar columns, so the gap is cause 1):

| what the turn read or ran | turns | $ recorded | $ from own usage |
|---|---:|---:|---:|
| ran a veri snapshot script | 60 | $44.32 | $1.89 |
| text-only reply | 21 | $19.07 | $0.58 |
| git/gh/log check | 14 | $11.52 | $0.45 |
| read a finished leaf run's background-task output, then git/log checks | 13 | $11.20 | $0.33 |
| read a saved tool result | 8 | $6.48 | $0.26 |
| other tool call | 6 | $4.64 | $0.66 |

The own-usage cost of a hot turn is $0.034 on average (max $0.50, the first turn of #26's session, which writes 59,566 tokens to the cache), the same as any other conductor turn at that context size: a conductor turn costs about its context × the cache-read rate, and the 122 turns sit at contexts of 47524–113818 tokens. No turn read or ran anything that made it expensive; a turn that reads a leaf's `tasks/*.output` file costs the same as a text-only reply.

## Per wake

A wake is the stretch of turns between two `result` records. Each wake's hot turns are recorded at about the wake's cumulative total (a wake's hot $ recorded equals its cumulative total when all its turns are hot), and the lowest such total is $1.61:

| run | wake | cumulative `total_cost_usd` at its end | hot turns in it | hot $ recorded | hot $ from own usage |
|---|---:|---:|---:|---:|---:|
| #13 | 4 | $3.49 | 3 | $3.49 | $0.09 |
| #13 | 8 | $4.82 | 7 | $4.82 | $0.15 |
| #13 | 9 | $4.87 | 3 | $4.87 | $0.06 |
| #13 | 10 | $4.95 | 4 | $4.95 | $0.08 |
| #13 | 11 | $5.20 | 9 | $5.20 | $0.25 |
| #13 | 12 | $5.44 | 7 | $5.44 | $0.24 |
| #26 | 0 | $1.61 | 1 | $0.50 | $0.50 |
| #26 | 6 | $2.25 | 3 | $2.25 | $0.06 |
| #26 | 8 | $2.58 | 3 | $2.58 | $0.06 |
| #26 | 10 | $3.16 | 6 | $3.16 | $0.16 |
| #26 | 11 | $3.32 | 6 | $3.32 | $0.16 |
| #26 | 12 | $3.50 | 6 | $3.50 | $0.17 |
| #27 | 6 | $3.81 | 5 | $3.81 | $0.21 |
| #27 | 8 | $4.70 | 9 | $4.70 | $0.30 |
| #27 | 9 | $4.77 | 3 | $4.77 | $0.07 |
| #27 | 10 | $4.94 | 6 | $4.94 | $0.18 |
| #27 | 11 | $5.11 | 6 | $5.11 | $0.17 |
| #27 | 12 | $5.46 | 10 | $5.46 | $0.35 |
| #27 | 13 | $5.86 | 10 | $5.86 | $0.40 |
| #27 | 14 | $5.96 | 3 | $5.96 | $0.10 |
| #27 | 15 | $6.17 | 6 | $6.17 | $0.21 |
| #27 | 16 | $6.37 | 6 | $6.37 | $0.20 |

## The 122 hot turns

`turn` is the row number in the run's recorded `Conductor per turn` table; `wake` the 0-based `result` record that closed the turn; `context` the turn's input tokens (cache read + cache write + uncached); `cache read` and `cache write` its two cached components; `$ rec.` the recorded dollars; `$ own` the turn's own usage priced.

| run | turn | wake | context | cache read | cache write | what it read or ran | $ rec. | $ own |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| #13 | 345 | 4 | 101096 | 100700 | 392 | read a finished leaf run's background-task output, then git/log checks | $1.16 | $0.03 |
| #13 | 346 | 4 | 102599 | 101092 | 1505 | ran a veri snapshot script | $1.17 | $0.03 |
| #13 | 347 | 4 | 103126 | 102597 | 527 | text-only reply | $1.16 | $0.03 |
| #13 | 383 | 8 | 51105 | 50694 | 407 | read a finished leaf run's background-task output, then git/log checks | $0.69 | $0.02 |
| #13 | 384 | 8 | 51656 | 51101 | 553 | ran a veri snapshot script | $0.68 | $0.02 |
| #13 | 385 | 8 | 52470 | 51654 | 814 | ran a veri snapshot script | $0.70 | $0.03 |
| #13 | 386 | 8 | 52834 | 52468 | 364 | ran a veri snapshot script | $0.68 | $0.02 |
| #13 | 387 | 8 | 53574 | 52832 | 740 | ran a veri snapshot script | $0.69 | $0.02 |
| #13 | 388 | 8 | 54014 | 53572 | 440 | ran a veri snapshot script | $0.69 | $0.02 |
| #13 | 389 | 8 | 54451 | 54012 | 437 | text-only reply | $0.69 | $0.02 |
| #13 | 390 | 9 | 54876 | 54449 | 423 | read a finished leaf run's background-task output, then git/log checks | $1.62 | $0.02 |
| #13 | 391 | 9 | 55615 | 54872 | 741 | ran a veri snapshot script | $1.63 | $0.02 |
| #13 | 392 | 9 | 56089 | 55613 | 474 | text-only reply | $1.62 | $0.02 |
| #13 | 393 | 10 | 56508 | 56087 | 417 | read a finished leaf run's background-task output, then git/log checks | $1.24 | $0.02 |
| #13 | 394 | 10 | 56919 | 56504 | 413 | ran a veri snapshot script | $1.23 | $0.02 |
| #13 | 395 | 10 | 57965 | 56917 | 1046 | ran a veri snapshot script | $1.25 | $0.02 |
| #13 | 396 | 10 | 58460 | 57963 | 495 | text-only reply | $1.23 | $0.02 |
| #13 | 397 | 11 | 58903 | 58458 | 441 | read a finished leaf run's background-task output, then git/log checks | $0.57 | $0.02 |
| #13 | 398 | 11 | 59285 | 58899 | 384 | other tool call | $0.57 | $0.02 |
| #13 | 399 | 11 | 59857 | 59283 | 572 | read a saved tool result | $0.58 | $0.03 |
| #13 | 400 | 11 | 60829 | 59855 | 972 | read a saved tool result | $0.57 | $0.02 |
| #13 | 401 | 11 | 65508 | 60827 | 4679 | other tool call | $0.61 | $0.06 |
| #13 | 402 | 11 | 66257 | 65506 | 749 | ran a veri snapshot script | $0.58 | $0.02 |
| #13 | 403 | 11 | 67050 | 66255 | 793 | ran a veri snapshot script | $0.57 | $0.03 |
| #13 | 404 | 11 | 67319 | 67048 | 269 | ran a veri snapshot script | $0.58 | $0.02 |
| #13 | 405 | 11 | 67762 | 67317 | 443 | text-only reply | $0.57 | $0.03 |
| #13 | 406 | 12 | 68265 | 67760 | 501 | read a finished leaf run's background-task output, then git/log checks | $0.77 | $0.03 |
| #13 | 407 | 12 | 68684 | 68261 | 421 | ran a veri snapshot script | $0.77 | $0.02 |
| #13 | 408 | 12 | 69380 | 68682 | 696 | ran a veri snapshot script | $0.77 | $0.03 |
| #13 | 409 | 12 | 70829 | 69378 | 1449 | ran a veri snapshot script | $0.77 | $0.03 |
| #13 | 410 | 12 | 75952 | 70827 | 5123 | ran a veri snapshot script | $0.81 | $0.07 |
| #13 | 411 | 12 | 77275 | 75950 | 1323 | git/gh/log check | $0.78 | $0.03 |
| #13 | 412 | 12 | 77587 | 77273 | 312 | text-only reply | $0.77 | $0.03 |
| #26 | 1 | 0 | 78156 | 18588 | 59566 | other tool call | $0.50 | $0.50 |
| #26 | 116 | 6 | 57346 | 56871 | 471 | read a finished leaf run's background-task output, then git/log checks | $0.75 | $0.02 |
| #26 | 117 | 6 | 57970 | 57342 | 626 | ran a veri snapshot script | $0.75 | $0.02 |
| #26 | 118 | 6 | 58371 | 57968 | 401 | text-only reply | $0.75 | $0.02 |
| #26 | 130 | 8 | 68035 | 67632 | 399 | read a finished leaf run's background-task output, then git/log checks | $0.86 | $0.02 |
| #26 | 131 | 8 | 68285 | 68031 | 252 | ran a veri snapshot script | $0.86 | $0.02 |
| #26 | 132 | 8 | 68674 | 68283 | 389 | text-only reply | $0.86 | $0.02 |
| #26 | 146 | 10 | 82505 | 82104 | 397 | read a finished leaf run's background-task output, then git/log checks | $0.53 | $0.03 |
| #26 | 147 | 10 | 82810 | 82501 | 307 | ran a veri snapshot script | $0.52 | $0.02 |
| #26 | 148 | 10 | 83604 | 82808 | 794 | ran a veri snapshot script | $0.53 | $0.03 |
| #26 | 149 | 10 | 83798 | 83602 | 194 | ran a veri snapshot script | $0.52 | $0.03 |
| #26 | 150 | 10 | 84532 | 83796 | 734 | ran a veri snapshot script | $0.53 | $0.02 |
| #26 | 151 | 10 | 84949 | 84530 | 417 | text-only reply | $0.53 | $0.03 |
| #26 | 152 | 11 | 85350 | 84947 | 399 | read a finished leaf run's background-task output, then git/log checks | $0.55 | $0.03 |
| #26 | 153 | 11 | 85657 | 85346 | 309 | ran a veri snapshot script | $0.55 | $0.02 |
| #26 | 154 | 11 | 86433 | 85655 | 776 | ran a veri snapshot script | $0.56 | $0.03 |
| #26 | 155 | 11 | 86848 | 86431 | 415 | ran a veri snapshot script | $0.55 | $0.03 |
| #26 | 156 | 11 | 87272 | 86846 | 424 | ran a veri snapshot script | $0.56 | $0.03 |
| #26 | 157 | 11 | 87687 | 87270 | 415 | text-only reply | $0.55 | $0.02 |
| #26 | 158 | 12 | 88085 | 87685 | 396 | read a finished leaf run's background-task output, then git/log checks | $0.58 | $0.03 |
| #26 | 159 | 12 | 88391 | 88081 | 308 | ran a veri snapshot script | $0.58 | $0.02 |
| #26 | 160 | 12 | 89107 | 88389 | 716 | ran a veri snapshot script | $0.59 | $0.03 |
| #26 | 161 | 12 | 89926 | 89105 | 819 | ran a veri snapshot script | $0.58 | $0.04 |
| #26 | 162 | 12 | 90529 | 89924 | 603 | ran a veri snapshot script | $0.58 | $0.03 |
| #26 | 163 | 12 | 90960 | 90527 | 431 | text-only reply | $0.59 | $0.02 |
| #27 | 84 | 6 | 109610 | 108855 | 751 | git/gh/log check | $0.76 | $0.04 |
| #27 | 85 | 6 | 110363 | 109606 | 755 | ran a veri snapshot script | $0.76 | $0.04 |
| #27 | 86 | 6 | 111955 | 110361 | 1592 | ran a veri snapshot script | $0.77 | $0.05 |
| #27 | 87 | 6 | 112705 | 111953 | 750 | git/gh/log check | $0.76 | $0.04 |
| #27 | 88 | 6 | 113212 | 112703 | 507 | text-only reply | $0.76 | $0.04 |
| #27 | 100 | 8 | 47524 | 46464 | 1056 | git/gh/log check | $0.51 | $0.03 |
| #27 | 101 | 8 | 48413 | 47520 | 891 | git/gh/log check | $0.52 | $0.02 |
| #27 | 102 | 8 | 51363 | 48411 | 2950 | ran a veri snapshot script | $0.53 | $0.04 |
| #27 | 103 | 8 | 56726 | 51361 | 5363 | git/gh/log check | $0.55 | $0.06 |
| #27 | 104 | 8 | 59325 | 56724 | 2599 | ran a veri snapshot script | $0.53 | $0.04 |
| #27 | 105 | 8 | 60611 | 59323 | 1286 | ran a veri snapshot script | $0.52 | $0.03 |
| #27 | 106 | 8 | 61258 | 60609 | 647 | git/gh/log check | $0.51 | $0.03 |
| #27 | 107 | 8 | 61872 | 61256 | 614 | other tool call | $0.52 | $0.02 |
| #27 | 108 | 8 | 62248 | 61870 | 376 | text-only reply | $0.51 | $0.03 |
| #27 | 109 | 9 | 63063 | 62246 | 813 | git/gh/log check | $1.59 | $0.02 |
| #27 | 110 | 9 | 63610 | 63059 | 549 | other tool call | $1.59 | $0.03 |
| #27 | 111 | 9 | 64145 | 63608 | 535 | text-only reply | $1.59 | $0.02 |
| #27 | 112 | 10 | 64805 | 64143 | 658 | git/gh/log check | $0.82 | $0.02 |
| #27 | 113 | 10 | 66236 | 64801 | 1433 | ran a veri snapshot script | $0.83 | $0.04 |
| #27 | 114 | 10 | 67791 | 66234 | 1555 | ran a veri snapshot script | $0.82 | $0.03 |
| #27 | 115 | 10 | 69014 | 67789 | 1223 | ran a veri snapshot script | $0.83 | $0.03 |
| #27 | 116 | 10 | 70255 | 69012 | 1241 | ran a veri snapshot script | $0.82 | $0.03 |
| #27 | 117 | 10 | 70974 | 70253 | 719 | text-only reply | $0.82 | $0.03 |
| #27 | 118 | 11 | 71721 | 70972 | 745 | read a finished leaf run's background-task output, then git/log checks | $0.85 | $0.03 |
| #27 | 119 | 11 | 72335 | 71717 | 616 | other tool call | $0.85 | $0.03 |
| #27 | 120 | 11 | 73340 | 72333 | 1005 | ran a veri snapshot script | $0.86 | $0.03 |
| #27 | 121 | 11 | 74035 | 73338 | 695 | ran a veri snapshot script | $0.85 | $0.02 |
| #27 | 122 | 11 | 74656 | 74033 | 621 | ran a veri snapshot script | $0.85 | $0.03 |
| #27 | 123 | 11 | 75298 | 74654 | 642 | text-only reply | $0.85 | $0.03 |
| #27 | 124 | 12 | 75964 | 75296 | 664 | git/gh/log check | $0.54 | $0.03 |
| #27 | 125 | 12 | 76614 | 75960 | 652 | ran a veri snapshot script | $0.54 | $0.03 |
| #27 | 126 | 12 | 79816 | 76612 | 3202 | ran a veri snapshot script | $0.56 | $0.05 |
| #27 | 127 | 12 | 80561 | 79814 | 745 | ran a veri snapshot script | $0.54 | $0.03 |
| #27 | 128 | 12 | 80987 | 80559 | 426 | ran a veri snapshot script | $0.54 | $0.03 |
| #27 | 129 | 12 | 82447 | 80985 | 1460 | ran a veri snapshot script | $0.55 | $0.03 |
| #27 | 130 | 12 | 84130 | 82445 | 1683 | ran a veri snapshot script | $0.55 | $0.04 |
| #27 | 131 | 12 | 85363 | 84128 | 1233 | ran a veri snapshot script | $0.55 | $0.04 |
| #27 | 132 | 12 | 86785 | 85361 | 1422 | git/gh/log check | $0.55 | $0.04 |
| #27 | 133 | 12 | 87264 | 86783 | 479 | text-only reply | $0.54 | $0.03 |
| #27 | 134 | 13 | 88108 | 87262 | 842 | git/gh/log check | $0.58 | $0.03 |
| #27 | 135 | 13 | 88638 | 88104 | 532 | ran a veri snapshot script | $0.58 | $0.04 |
| #27 | 136 | 13 | 89735 | 88636 | 1097 | ran a veri snapshot script | $0.58 | $0.03 |
| #27 | 137 | 13 | 90685 | 89733 | 950 | read a saved tool result | $0.58 | $0.04 |
| #27 | 138 | 13 | 91082 | 90683 | 397 | read a saved tool result | $0.58 | $0.03 |
| #27 | 139 | 13 | 93411 | 91080 | 2329 | ran a veri snapshot script | $0.59 | $0.05 |
| #27 | 140 | 13 | 97367 | 93409 | 3956 | ran a veri snapshot script | $0.61 | $0.06 |
| #27 | 141 | 13 | 97777 | 97365 | 410 | ran a veri snapshot script | $0.58 | $0.03 |
| #27 | 142 | 13 | 98991 | 97775 | 1214 | ran a veri snapshot script | $0.58 | $0.04 |
| #27 | 143 | 13 | 101822 | 98989 | 2831 | text-only reply | $0.60 | $0.05 |
| #27 | 144 | 14 | 102679 | 101820 | 855 | git/gh/log check | $1.99 | $0.03 |
| #27 | 145 | 14 | 103374 | 102675 | 697 | ran a veri snapshot script | $1.98 | $0.04 |
| #27 | 146 | 14 | 103973 | 103372 | 599 | text-only reply | $1.99 | $0.03 |
| #27 | 147 | 15 | 104689 | 103971 | 714 | read a finished leaf run's background-task output, then git/log checks | $1.03 | $0.03 |
| #27 | 148 | 15 | 105206 | 104685 | 519 | read a saved tool result | $1.02 | $0.03 |
| #27 | 149 | 15 | 106029 | 105204 | 823 | read a saved tool result | $1.03 | $0.04 |
| #27 | 150 | 15 | 108539 | 106027 | 2510 | ran a veri snapshot script | $1.04 | $0.05 |
| #27 | 151 | 15 | 109241 | 108537 | 702 | ran a veri snapshot script | $1.02 | $0.03 |
| #27 | 152 | 15 | 109857 | 109239 | 616 | text-only reply | $1.03 | $0.03 |
| #27 | 153 | 16 | 110424 | 109855 | 565 | git/gh/log check | $1.06 | $0.03 |
| #27 | 154 | 16 | 110945 | 110420 | 523 | read a saved tool result | $1.06 | $0.03 |
| #27 | 155 | 16 | 111500 | 110943 | 555 | read a saved tool result | $1.06 | $0.04 |
| #27 | 156 | 16 | 112678 | 111498 | 1178 | ran a veri snapshot script | $1.07 | $0.03 |
| #27 | 157 | 16 | 113239 | 112676 | 561 | ran a veri snapshot script | $1.06 | $0.04 |
| #27 | 158 | 16 | 113818 | 113237 | 579 | text-only reply | $1.06 | $0.03 |

## Scope

Only runs #13, #26 and #27 were read; the issue's $188 / 82% figure covers nine runs and the other six were not re-measured here. In the three runs measured, the conductor's true spend is $34.55 against $168.76 recorded, so the conductor's share of the three runs' total cost is correspondingly smaller than the recorded 82%; the leaf figures were not re-derived.

## Proposed fixes, one per named cause (issue titles; none is made here)

1. Cause 1 (cumulative `total_cost_usd` re-billed per wake): `metrics: regenerate the conductor spend and per-turn dollars of runs recorded before #4599 from their stream logs`
2. Cause 1, detection: `metrics: refuse a conductor per-turn table whose turn dollars sum to more than the last cumulative total_cost_usd of its sessions`
3. Cause 2 (own usage, a 47k–117k context re-read each turn): `conductor: report its real spend per run (last cumulative total per session) so a cost reduction can be filed against a measured figure`
