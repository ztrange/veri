### 📊 Metrics — issue 3096

Wall time for the issue: 4898 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3103.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.94 over 115 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90536 tokens, largest 165206 tokens
Conductor context: first turn 90512 tokens, largest 171458 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90536 |
| 2 | $0.09 | 97756 |
| 3 | $0.04 | 99170 |
| 4 | $0.05 | 101177 |
| 5 | $0.03 | 101530 |
| 6 | $0.04 | 101915 |
| 7 | $0.03 | 102216 |
| 8 | $0.04 | 102548 |
| 9 | $0.03 | 102809 |
| 10 | $0.03 | 103148 |
| 11 | $0.04 | 103530 |
| 12 | $0.04 | 104527 |
| 13 | $0.03 | 104945 |
| 14 | $0.04 | 105856 |
| 15 | $0.05 | 107843 |
| 16 | $0.05 | 110204 |
| 17 | $0.05 | 111617 |
| 18 | $0.03 | 111941 |
| 19 | $0.04 | 112788 |
| 20 | $0.04 | 113349 |
| 21 | $0.04 | 114236 |
| 22 | $0.09 | 120859 |
| 23 | $0.06 | 124026 |
| 24 | $0.04 | 124751 |
| 25 | $0.04 | 125028 |
| 26 | $0.04 | 125570 |
| 27 | $0.04 | 126069 |
| 28 | $0.05 | 128054 |
| 29 | $0.04 | 128887 |
| 30 | $0.04 | 129431 |
| 31 | $0.05 | 130040 |
| 32 | $0.05 | 131524 |
| 33 | $0.04 | 132676 |
| 34 | $0.05 | 133677 |
| 35 | $0.05 | 135145 |
| 36 | $0.04 | 135632 |
| 37 | $0.06 | 138513 |
| 38 | $0.05 | 140479 |
| 39 | $0.05 | 141207 |
| 40 | $0.10 | 149454 |
| 41 | $0.06 | 151012 |
| 42 | $0.05 | 151875 |
| 43 | $0.04 | 152711 |
| 44 | $0.05 | 153079 |
| 45 | $0.05 | 154738 |
| 46 | $0.08 | 159309 |
| 47 | $0.08 | 164039 |
| 48 | $0.05 | 165206 |
| 49 | $0.58 | 90512 |
| 50 | $0.07 | 97582 |
| 51 | $0.03 | 99028 |
| 52 | $0.04 | 100959 |
| 53 | $0.04 | 102867 |
| 54 | $0.06 | 107988 |
| 55 | $0.03 | 108902 |
| 56 | $0.03 | 109316 |
| 57 | $0.02 | 109621 |
| 58 | $0.02 | 109909 |
| 59 | $0.02 | 110165 |
| 60 | $0.03 | 111215 |
| 61 | $0.03 | 111864 |
| 62 | $0.05 | 115809 |
| 63 | $0.04 | 117728 |
| 64 | $0.04 | 120076 |
| 65 | $0.03 | 120671 |
| 66 | $0.03 | 121355 |
| 67 | $0.03 | 122133 |
| 68 | $0.06 | 126606 |
| 69 | $0.03 | 127274 |
| 70 | $0.03 | 127618 |
| 71 | $0.03 | 128105 |
| 72 | $0.03 | 128638 |
| 73 | $0.03 | 129519 |
| 74 | $0.03 | 130256 |
| 75 | $0.03 | 130848 |
| 76 | $0.04 | 132185 |
| 77 | $0.03 | 132712 |
| 78 | $0.03 | 132991 |
| 79 | $0.03 | 133787 |
| 80 | $0.03 | 134400 |
| 81 | $0.04 | 135531 |
| 82 | $0.03 | 136228 |
| 83 | $0.03 | 136827 |
| 84 | $0.04 | 137802 |
| 85 | $0.04 | 139508 |
| 86 | $0.03 | 140245 |
| 87 | $0.03 | 140851 |
| 88 | $0.04 | 141870 |
| 89 | $0.03 | 142688 |
| 90 | $0.04 | 144082 |
| 91 | $0.04 | 145443 |
| 92 | $0.09 | 153516 |
| 93 | $0.05 | 156086 |
| 94 | $0.04 | 156980 |
| 95 | $0.05 | 158781 |
| 96 | $0.04 | 159726 |
| 97 | $0.03 | 159960 |
| 98 | $0.05 | 161957 |
| 99 | $0.04 | 162951 |
| 100 | $0.04 | 163898 |
| 101 | $0.04 | 165047 |
| 102 | $0.04 | 165610 |
| 103 | $0.04 | 166211 |
| 104 | $0.04 | 166708 |
| 105 | $0.04 | 167399 |
| 106 | $0.04 | 167959 |
| 107 | $0.04 | 168447 |
| 108 | $0.04 | 168809 |
| 109 | $0.04 | 169103 |
| 110 | $0.04 | 169373 |
| 111 | $0.04 | 169638 |
| 112 | $0.04 | 170471 |
| 113 | $0.04 | 170714 |
| 114 | $0.04 | 170976 |
| 115 | $0.04 | 171458 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 903 | 0 | 31889 | 0.09 |
| red | 8 | 3 | 0 | 0 | 1166 | 222 | 51 | 102 | 21202 | 1641441 | 230856 | 1.10 |
| pin | 4 | 3 | 1 | 0 | 171 | 83 | 20 | 40 | 7411 | 540919 | 101827 | 0.38 |
| green | 9 | 1 | 3 | 0 | 1681 | 301 | 74 | 144 | 26011 | 2480096 | 193809 | 1.16 |
| red-supersede | 1 | 0 | 0 | 0 | 63 | 48 | 9 | 18 | 4767 | 338871 | 30523 | 0.16 |
| diff | 4 | 0 | 2 | 0 | 320 | 67 | 18 | 36 | 5461 | 493527 | 100626 | 0.56 |
| red-missing | 2 | 0 | 0 | 0 | 125 | 75 | 12 | 24 | 5560 | 359024 | 78510 | 0.29 |
| refactor | 1 | 0 | 0 | 0 | 15 | 12 | 3 | 6 | 606 | 62883 | 32304 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 8 | 6 | 0 | 1595 | 286 | 62 | 124 | 23139 | 1710341 | 288403 | 1.12 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 964 | 205 | 40 | 80 | 18558 | 1278570 | 224117 | 0.87 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 992 | 324 | 86 | 168 | 30224 | 2927850 | 287824 | 1.83 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 78 | 0.13 | 0 | 0.00 |
| green | 5043 | 3.47 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| diff | 450 | 0.86 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A fresh launch of issue-worktree.sh <n> <slug> onto an issue whose tdd/<n>-<slug> branch is on origin (a local bare repo) and which carries another lane's taken:* label, with no local branch or worktree, still exits 2 with the existing "already on origin" message and creates no worktree — a medium case with real git against a local bare repo as origin, the issue's labels faked through veri's GitHub wrapper, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 1 | 0 | 60 | 14 | 28 | 5948 | 400538 | 71947 | 0.28 | unknown | unknown | unknown | unknown |  |  | pin |
| A resume of issue-worktree.sh <n> <slug> onto an issue carrying this machine's own taken:<lane> label (the lane being the text after VERI_LABEL's last ':', or main when it has none), with no local branch, no .tdd/wt/<n> and tdd/<n>-<slug> on origin (a local bare repo) carrying a committed ledger .tdd/issue-<n>.md, recreates the worktree at that branch's origin tip, exits 0 printing the worktree path, and the worktree holds the committed ledger — a medium case with real git against a local bare repo as origin, the issue's labels faked through veri's GitHub wrapper ⟦criterion 1⟧ | 25 | 5 | 6 | 0 | 0 | 0 | 692 | 158 | 312 | 58916 | 5052345 | 617891 | 3.15 | 2466 | diff 2/2, red 1/2, green 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| The 4 older test_issue_worktree.py cases fake another lane's claim (the gh label), so they pin the cross-lane refusal and stay green with or without step 2's change ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 15 | 30 | 6154 | 463878 | 78617 | 0.30 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A resume of issue-worktree.sh <n> <slug> onto an issue carrying this machine's own taken:<lane> label (the lane being the text after VERI_LABEL's last ':', or main when it has none), with no local branch, no .tdd/wt/<n> and tdd/<n>-<slug> on origin (a local bare repo) carrying a committed ledger .tdd/issue-<n>.md, recreates the worktree at that branch's origin tip, exits 0 printing the worktree path, and the worktree holds the committed ledger — a medium case with real git against a local bare repo as origin, the issue's labels faked through veri's GitHub wrapper ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 15 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 14 | 9 | 11 | 14 | 17 | 11 | 14 | 14 | 12 | 11 | 9 | 10 | 0 | 11 | 13 | 13 | 11 | 7 | 8 | 7 | 7 | 9 |
| target | 6 | 4 | 5 | 7 | 8 | 7 | 7 | 3 | 6 | 6 | 3 | 8 | 10 | 8 | 6 | 7 | 6 | 12 | 12 |  |  |  |  |
| fast | 63 | 58 | 35 | 44 | 44 | 34 | 29 | 32 | 35 | 33 | 37 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 188 | 372 | 71921 | 5916761 | 800344 | 9.76 (estimate) |
