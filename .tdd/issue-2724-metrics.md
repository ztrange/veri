### 📊 Metrics — issue 2724

Wall time for the issue: 2231 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2737.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $7.21 over 106 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86624 tokens, largest 141169 tokens
Conductor context: first turn 86630 tokens, largest 181667 tokens
Conductor context: first turn 86630 tokens, largest 124588 tokens
Conductor context: first turn 86681 tokens, largest 110217 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 86624 |
| 2 | $0.10 | 93628 |
| 3 | $0.04 | 94389 |
| 4 | $0.06 | 96514 |
| 5 | $0.05 | 97775 |
| 6 | $0.06 | 100575 |
| 7 | $0.05 | 101805 |
| 8 | $0.04 | 102116 |
| 9 | $0.08 | 107040 |
| 10 | $0.09 | 112122 |
| 11 | $0.08 | 117243 |
| 12 | $0.07 | 120624 |
| 13 | $0.13 | 130731 |
| 14 | $0.10 | 137034 |
| 15 | $0.05 | 138313 |
| 16 | $0.07 | 141169 |
| 17 | $0.57 | 86630 |
| 18 | $0.09 | 93633 |
| 19 | $0.04 | 94824 |
| 20 | $0.06 | 97621 |
| 21 | $0.13 | 110111 |
| 22 | $0.05 | 110682 |
| 23 | $0.04 | 111280 |
| 24 | $0.04 | 111700 |
| 25 | $0.04 | 112045 |
| 26 | $0.04 | 112491 |
| 27 | $0.08 | 117328 |
| 28 | $0.05 | 119223 |
| 29 | $0.15 | 132190 |
| 30 | $0.05 | 134086 |
| 31 | $0.07 | 136483 |
| 32 | $0.05 | 137369 |
| 33 | $0.06 | 139865 |
| 34 | $0.05 | 140888 |
| 35 | $0.06 | 143133 |
| 36 | $0.07 | 145449 |
| 37 | $0.05 | 147011 |
| 38 | $0.07 | 149507 |
| 39 | $0.05 | 150313 |
| 40 | $0.06 | 152254 |
| 41 | $0.07 | 154958 |
| 42 | $0.05 | 155813 |
| 43 | $0.07 | 157802 |
| 44 | $0.07 | 160315 |
| 45 | $0.05 | 161427 |
| 46 | $0.06 | 163093 |
| 47 | $0.06 | 163897 |
| 48 | $0.06 | 166123 |
| 49 | $0.06 | 166856 |
| 50 | $0.05 | 167125 |
| 51 | $0.05 | 167569 |
| 52 | $0.06 | 167981 |
| 53 | $0.05 | 168613 |
| 54 | $0.05 | 168877 |
| 55 | $0.05 | 169131 |
| 56 | $0.06 | 169537 |
| 57 | $0.05 | 170489 |
| 58 | $0.12 | 178715 |
| 59 | $0.08 | 181667 |
| 60 | $0.56 | 86630 |
| 61 | $0.09 | 93633 |
| 62 | $0.03 | 94529 |
| 63 | $0.09 | 102125 |
| 64 | $0.06 | 105438 |
| 65 | $0.04 | 106067 |
| 66 | $0.03 | 106436 |
| 67 | $0.04 | 106833 |
| 68 | $0.03 | 107269 |
| 69 | $0.04 | 107668 |
| 70 | $0.04 | 108563 |
| 71 | $0.06 | 112685 |
| 72 | $0.05 | 114282 |
| 73 | $0.04 | 115534 |
| 74 | $0.09 | 121974 |
| 75 | $0.05 | 124588 |
| 76 | $0.55 | 86681 |
| 77 | $0.07 | 93683 |
| 78 | $0.03 | 94515 |
| 79 | $0.05 | 98884 |
| 80 | $0.06 | 103286 |
| 81 | $0.03 | 104010 |
| 82 | $0.02 | 104527 |
| 83 | $0.02 | 104917 |
| 84 | $0.02 | 105404 |
| 85 | $0.04 | 107223 |
| 86 | $0.03 | 108227 |
| 87 | $0.02 | 108555 |
| 88 | $0.02 | 108830 |
| 89 | $0.03 | 109307 |
| 90 | $0.03 | 110217 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 0 | 1 | 0 | 20 | 16 | 2 | 4 | 1906 | 31707 | 34165 | 0.11 |
| red | 6 | 2 | 0 | 0 | 411 | 204 | 43 | 74 | 23506 | 1234211 | 206718 | 1.13 |
| green | 6 | 2 | 1 | 0 | 823 | 137 | 35 | 68 | 14977 | 1034717 | 116333 | 0.70 |
| refactor | 3 | 1 | 0 | 0 | 99 | 22 | 11 | 22 | 2172 | 284442 | 62834 | 0.21 |
| pin | 1 | 1 | 0 | 0 | 36 | 15 | 6 | 12 | 1824 | 174198 | 17152 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 6 | 2 | 0 | 649 | 114 | 34 | 64 | 12507 | 862008 | 150885 | 0.59 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 448 | 176 | 30 | 52 | 19729 | 849603 | 164426 | 1.11 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 292 | 104 | 33 | 64 | 12149 | 1047664 | 121891 | 0.53 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 530 | 0.51 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A re-record of a step whose ledger line went through phased `⟂ <phase> done` marks keeps the pins and renames that step committed, and no later step's, pinned by one real-git process case in test_tests_frozen_process.py whose committed ledger has that phased shape ⟦criterion 1⟧ | 8 | 2 | 1 | 0 | 0 | 0 | 234 | 47 | 84 | 25593 | 1273011 | 252649 | 1.43 | 996 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| A re-record of a fixture-repair step, whose ledger line ends in the fixture-repair marker, keeps the pins and renames that step committed, pinned by one real-git process case in test_tests_frozen_process.py whose committed ledger has that shape | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 15 | 30 | 5922 | 515117 | 45015 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| A case renamed by a step's own refactor commit, landed between its green tick and its refactor-verified commit, is attributed on a later re-record to that step and not to the next step, pinned by one real-git process case in test_tests_frozen_process.py ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 33 | 62 | 10964 | 939440 | 105373 | 0.47 | 652 | unknown | 1/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A re-record of a step whose ledger line went through phased `⟂ <phase> done` marks keeps the pins and renames that step committed, and no later step's, pinned by one real-git process case in test_tests_frozen_process.py whose committed ledger has that phased shape ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.09 |
| A case renamed by a step's own refactor commit, landed between its green tick and its refactor-verified commit, is attributed on a later re-record to that step and not to the next step, pinned by one real-git process case in test_tests_frozen_process.py ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 90 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 23 | 17 | 4 | 22 | 21 | 23 | 14 | 15 | 23 | 24 | 23 | 23 | 16 | 21 |
| fast | 28 | 30 | 37 | 24 | 35 | 34 | 28 |  |  |  |  |  |  |  |
| target | 4 | 4 | 4 | 4 | 5 | 4 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 180 | 44385 | 2759275 | 437202 | 9.44 (estimate) |
