### 📊 Metrics — issue 2184

Wall time for the issue: 857 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 7 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.99 over 47 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87216 |
| 2 | $0.03 | 89205 |
| 3 | $0.03 | 91117 |
| 4 | $0.02 | 91481 |
| 5 | $0.02 | 91910 |
| 6 | $0.02 | 92208 |
| 7 | $0.02 | 92570 |
| 8 | $0.02 | 93038 |
| 9 | $0.02 | 93431 |
| 10 | $0.03 | 94284 |
| 11 | $0.04 | 97093 |
| 12 | $0.03 | 97894 |
| 13 | $0.03 | 99770 |
| 14 | $0.03 | 100933 |
| 15 | $0.02 | 101494 |
| 16 | $0.03 | 102537 |
| 17 | $0.03 | 104004 |
| 18 | $0.03 | 104900 |
| 19 | $0.03 | 105780 |
| 20 | $0.03 | 106677 |
| 21 | $0.03 | 107580 |
| 22 | $0.03 | 108603 |
| 23 | $0.03 | 109967 |
| 24 | $0.03 | 110757 |
| 25 | $0.03 | 111583 |
| 26 | $0.03 | 112323 |
| 27 | $0.03 | 112687 |
| 28 | $0.03 | 113423 |
| 29 | $0.03 | 114044 |
| 30 | $0.03 | 114752 |
| 31 | $0.03 | 116184 |
| 32 | $0.04 | 118597 |
| 33 | $0.03 | 119331 |
| 34 | $0.03 | 119628 |
| 35 | $0.03 | 120099 |
| 36 | $0.04 | 121619 |
| 37 | $0.03 | 122738 |
| 38 | $0.03 | 123794 |
| 39 | $0.04 | 125841 |
| 40 | $0.03 | 126921 |
| 41 | $0.03 | 127612 |
| 42 | $0.04 | 129558 |
| 43 | $0.04 | 131237 |
| 44 | $0.03 | 131979 |
| 45 | $0.03 | 132479 |
| 46 | $0.06 | 136728 |
| 47 | $0.03 | 137368 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1203 | 0 | 31546 | 0.09 |
| red | 5 | 2 | 0 | 0 | 221 | 95 | 29 | 52 | 10402 | 831455 | 123138 | 0.50 |
| green | 2 | 1 | 0 | 0 | 228 | 29 | 12 | 22 | 3462 | 324349 | 32625 | 0.15 |
| refactor | 2 | 1 | 0 | 0 | 66 | 24 | 5 | 10 | 710 | 124905 | 28414 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 38 | 10 | 3 | 6 | 728 | 76028 | 13473 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 241 | 61 | 16 | 32 | 5445 | 385519 | 104783 | 0.36 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 324 | 106 | 34 | 60 | 11060 | 971218 | 124413 | 0.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 89 | 0.17 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| verify-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A pytest leg sent SIGHUP while its pytest run is going removes its veri-pytest-* folder and exits as it does on SIGTERM, pinned by a process case that sends SIGHUP to a running leg and finds no folder left ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 28 | 50 | 8106 | 713392 | 118871 | 0.45 | 495 | unknown | 0/5 | nothing-left |  |  | full |
| When a pytest leg's main returns, the SIGHUP handler in force before it started is in force again ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 20 | 3342 | 321800 | 38120 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A pytest leg records its own pid in its veri-pytest-* folder when it creates it, readable there while its pytest run is going ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 10 | 20 | 3854 | 321545 | 40659 | 0.17 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A pytest leg sent SIGHUP while its pytest run is going removes its veri-pytest-* folder and exits as it does on SIGTERM, pinned by a process case that sends SIGHUP to a running leg and finds no folder left ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 66 | 0.09 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 16 | 16 | 16 | 15 | 27 | 16 | 15 | 25 | 16 |
| fast | 21 | 17 | 17 | 23 | 16 |  |  |  |  |
| target | 14 | 10 | 11 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 92 | 16505 | 1356737 | 229196 | 0.87 |
