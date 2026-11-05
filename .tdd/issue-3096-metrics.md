### 📊 Metrics — issue 3096

Wall time for the issue: 3906 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 3 planned.
Outcome: the run bailed — revise-impossible, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.24 over 46 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90536 tokens, largest 159309 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90536 |
| 2 | $0.08 | 97756 |
| 3 | $0.03 | 99170 |
| 4 | $0.04 | 101177 |
| 5 | $0.02 | 101530 |
| 6 | $0.02 | 101915 |
| 7 | $0.02 | 102216 |
| 8 | $0.02 | 102548 |
| 9 | $0.02 | 102809 |
| 10 | $0.02 | 103148 |
| 11 | $0.02 | 103530 |
| 12 | $0.03 | 104527 |
| 13 | $0.02 | 104945 |
| 14 | $0.03 | 105856 |
| 15 | $0.04 | 107843 |
| 16 | $0.04 | 110204 |
| 17 | $0.03 | 111617 |
| 18 | $0.02 | 111941 |
| 19 | $0.03 | 112788 |
| 20 | $0.03 | 113349 |
| 21 | $0.03 | 114236 |
| 22 | $0.08 | 120859 |
| 23 | $0.05 | 124026 |
| 24 | $0.03 | 124751 |
| 25 | $0.03 | 125028 |
| 26 | $0.03 | 125570 |
| 27 | $0.03 | 126069 |
| 28 | $0.04 | 128054 |
| 29 | $0.03 | 128887 |
| 30 | $0.03 | 129431 |
| 31 | $0.03 | 130040 |
| 32 | $0.04 | 131524 |
| 33 | $0.04 | 132676 |
| 34 | $0.03 | 133677 |
| 35 | $0.04 | 135145 |
| 36 | $0.03 | 135632 |
| 37 | $0.05 | 138513 |
| 38 | $0.04 | 140479 |
| 39 | $0.03 | 141207 |
| 40 | $0.09 | 149454 |
| 41 | $0.04 | 151012 |
| 42 | $0.04 | 151875 |
| 43 | $0.04 | 152711 |
| 44 | $0.03 | 153079 |
| 45 | $0.04 | 154738 |
| 46 | $0.07 | 159309 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 903 | 0 | 31889 | 0.09 |
| red | 3 | 1 | 0 | 0 | 812 | 75 | 20 | 40 | 7498 | 630882 | 81962 | 0.34 |
| pin | 1 | 1 | 0 | 0 | 54 | 26 | 6 | 12 | 2431 | 156174 | 33589 | 0.12 |
| green | 1 | 0 | 0 | 0 | 170 | 76 | 18 | 36 | 7613 | 735641 | 35008 | 0.24 |
| red-supersede | 1 | 0 | 0 | 0 | 63 | 48 | 9 | 18 | 4767 | 338871 | 30523 | 0.16 |
| diff | 4 | 0 | 2 | 0 | 320 | 67 | 18 | 36 | 5461 | 493527 | 100626 | 0.56 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 3 | 2 | 0 | 240 | 86 | 18 | 36 | 7002 | 438026 | 130657 | 0.44 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 959 | 176 | 42 | 84 | 18278 | 1559834 | 130040 | 0.66 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 230 | 37 | 12 | 24 | 3393 | 357235 | 52900 | 0.40 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 117 | 0.19 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 170 | 0.24 |
| red-supersede | 0 | 0.00 | 63 | 0.16 |
| diff | 0 | 0.00 | 320 | 0.56 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A fresh launch of issue-worktree.sh <n> <slug> onto an issue whose tdd/<n>-<slug> branch is on origin (a local bare repo) and which carries another lane's taken:* label, with no local branch or worktree, still exits 2 with the existing "already on origin" message and creates no worktree — a medium case with real git against a local bare repo as origin, the issue's labels faked through veri's GitHub wrapper, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 1 | 0 | 60 | 14 | 28 | 5948 | 400538 | 71947 | 0.28 | unknown | unknown | unknown | unknown |  |  | pin |
| A resume of issue-worktree.sh <n> <slug> onto an issue carrying this machine's own taken:<lane> label (the lane being the text after VERI_LABEL's last ':', or main when it has none), with no local branch, no .tdd/wt/<n> and tdd/<n>-<slug> on origin (a local bare repo) carrying a committed ledger .tdd/issue-<n>.md, recreates the worktree at that branch's origin tip, exits 0 printing the worktree path, and the worktree holds the committed ledger — a medium case with real git against a local bare repo as origin, the issue's labels faked through veri's GitHub wrapper ⟦criterion 1⟧ | 8 | 1 | 2 | 0 | 0 | 0 | 232 | 57 | 114 | 21822 | 1954557 | 209761 | 1.14 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 14 | 9 | 11 | 14 | 17 |
| target | 6 | 4 |  |  |  |  |
| fast | 63 | 58 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 72 | 144 | 28673 | 2355095 | 313597 | 3.75 (estimate) |
