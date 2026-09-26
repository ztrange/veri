### 📊 Metrics — issue 102

Wall time for the issue: 558 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 18 of 19 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/485.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 14 | 1 | 2 | 1466 | 11207 | 37921 | 0.33 |
| red | 34 | 15 | 0 | 0 | 13722 | 1495 | 272 | 522 | 142909 | 14082313 | 1778519 | 20.56 |
| green | 46 | 15 | 8 | 0 | 11335 | 1839 | 419 | 820 | 182987 | 20660104 | 1940429 | 23.32 |
| refactor | 30 | 15 | 0 | 0 | 2579 | 1023 | 242 | 476 | 102510 | 12274491 | 1419575 | 15.86 |
| pin | 3 | 3 | 0 | 0 | 143 | 68 | 17 | 34 | 6793 | 742354 | 126917 | 1.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 8265 | 16.14 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| parallel-conductors.sh exits 2 and launches no conductor when VERI_PARALLEL is not a whole number ≥ 1 (0, a word, or set-but-empty) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 196 | 45 | 88 | 19687 | 2142902 | 278577 | 3.05 | 491 | unknown | 0/5 | nothing-left |
| With VERI_PARALLEL unset (default 1) parallel-conductors.sh runs two solvable issues' conductors one after another — the second starts only after the first has ended ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 351 | 72 | 140 | 33684 | 3638245 | 349482 | 4.20 | 1659 | 1/2 | 1/5 | structural-owed |
| With VERI_PARALLEL=2 parallel-conductors.sh runs two conductors at once — their start and end stamps overlap ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 327 | 70 | 138 | 32143 | 3554272 | 350404 | 4.16 | 1060 | 1/2 | 2/5 | nothing-structural |
| Launches follow solvable-issues.sh's printed order and never include an issue it did not print, such as one blocked by an open issue ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 17 | 32 | 7459 | 832482 | 97803 | 1.10 | unknown | unknown | unknown | unknown |
| An issue solvable-issues.sh still prints after its conductor finished is not launched a second time in the same invocation ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 236 | 51 | 100 | 24186 | 2541593 | 280859 | 3.24 | 423 | unknown | 3/5 | structural-owed |
| The solvable set is re-asked after every completion, so an issue that became solvable while another conductor ran is launched next ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 15 | 28 | 7034 | 697532 | 94533 | 1.04 | unknown | unknown | unknown | unknown |
| VERI_MAX_ISSUES caps the launches of one invocation, 0 meaning no cap | 6 | 3 | 0 | 0 | 0 | 0 | 199 | 46 | 92 | 19386 | 2279438 | 280074 | 3.08 | 385 | unknown | 3/5 | nothing-structural |
| A finished conductor whose PR is ready is reported `#<n> — done <pr-url>`, and one whose PR is a draft and whose event log ends in a bail is reported `#<n> — bailed <pr-url>` ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 306 | 66 | 132 | 30329 | 3385237 | 350457 | 4.09 | 1061 | 1/2 | 2/5 | structural-owed |
| A conductor its supervisor killed (supervise exit 2) is reported `#<n> — killed after <VERI_RUN_TIMEOUT>s` ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 331 | 73 | 142 | 31790 | 3579764 | 397062 | 4.53 | 1594 | 2/2 | 1/5 | structural-owed |
| The first bail or kill stops new launches while conductors already running are waited to completion, and --continue-on-bail keeps launching and skips the bailed number ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 303 | 58 | 114 | 26369 | 2831651 | 396217 | 4.92 | 12372 | 1/2 | 2/5 | structural-owed |
| The caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL reach each conductor exactly as they were, set or unset ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 15 | 28 | 10723 | 733403 | 103241 | 1.19 | unknown | unknown | unknown | unknown |
| The outer supervisor of each conductor runs with heartbeat and timeout both VERI_RUN_TIMEOUT (default 14400) and no stuck retries ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 335 | 66 | 130 | 34127 | 3624821 | 312769 | 3.91 | 899 | unknown | 3/5 | structural-owed |
| In a target repo that has never seen veri, the caller's git status --porcelain stays empty after a launch ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 368 | 77 | 152 | 37326 | 4036145 | 360955 | 4.44 | 1811 | 1/2 | 3/5 | structural-owed |
| Supervising a conductor-<n> prints no leaf-role.sh refusal ⟦criterion 5⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 255 | 60 | 116 | 22703 | 3009182 | 335171 | 3.74 | 1070 | 1/2 | 1/5 | structural-owed |
| Exit 0 when every launched issue is done, 1 when one bailed or was killed, 2 when solvable-issues.sh exits 2, 3 when nothing is solvable and nothing was launched — and .tdd/parallel.exit carries that final code on every exit path ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 264 | 55 | 106 | 26757 | 2839926 | 305942 | 3.55 | 697 | unknown | 2/5 | nothing-structural |
| The report prints one line per issue in launch order followed by one line naming what stopped the loop ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 320 | 72 | 136 | 32481 | 3660164 | 404119 | 4.62 | 1562 | 1/2 | 2/5 | structural-owed |
| SCOPE-LOOP.md documents VERI_PARALLEL: at 1 rung 2 is unchanged, above 1 it runs parallel-conductors.sh detach-then-wait and relays the report ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 183 | 46 | 92 | 18198 | 2261253 | 282034 | 3.07 | 1741 | unknown | 0/5 | nothing-left |
| CONTEXT.md's rung 3 entry names parallel-conductors.sh, a glossary entry defines in flight as local to one invocation, and a new ADR records rung 3's design and the rejected remote claim ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 204 | 46 | 86 | 20817 | 2111252 | 285741 | 3.12 | 1935 | unknown | 0/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 79 | 1 | 79 | 0 | 0 | 1 | 0 | 3 | 37 | 45 | 3 | 4 | 0 | 6 | 6 | 31 | 32 | 31 | 32 | 31 | 0 | 4 | 5 | 6 | 6 | 6 | 33 | 5 | 5 | 6 | 5 | 6 | 9 | 9 | 9 | 9 | 8 | 9 | 9 | 9 | 8 | 9 | 10 | 11 | 11 | 53 | 11 | 11 | 12 | 12 | 12 | 12 | 12 | 12 | 35 | 0 | 86 | 13 | 13 | 375 | 17 | 18 | 193 | 52 | 17 | 17 | 17 | 20 | 22 | 21 | 22 | 20 | 61 | 20 | 21 | 0 | 22 | 19 | 20 | 20 | 20 | 22 | 23 | 62 | 2 | 23 | 23 | 23 | 26 | 25 | 25 | 27 | 27 | 1 | 0 | 27 | 0 | 1 | 29 | 29 | 32 | 68 | 29 | 30 | 30 | 30 | 33 | 32 | 32 | 72 | 68 | 34 | 35 | 36 | 34 | 36 | 412 | 444 | 439 | 37 | 36 | 38 | 428 | 405 | 42 |
| fast | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 3 | 3 | 4 | 4 | 5 | 5 | 5 | 7 | 5 | 0 | 8 | 11 | 11 | 12 | 12 | 13 | 18 | 18 | 19 | 19 | 21 | 24 | 23 | 26 | 32 | 34 | 34 | 36 | 34 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 379 | 383 | 377 | 389 | 387 | 398 | 403 | 410 | 429 | 441 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 951 | 1854 | 436665 | 47770469 | 5303361 | 61.37 |
