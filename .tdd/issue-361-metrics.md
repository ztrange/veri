### 📊 Metrics — issue 361

Wall time for the issue: 6781 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/396.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 8 | 3 | 0 | 0 | 760 | 704 | 122 | 210 | 57711 | 6076613 | 463156 | 9.11 |
| green | 6 | 3 | 0 | 0 | 1563 | 558 | 118 | 218 | 43354 | 6246866 | 313917 | 7.35 |
| refactor | 6 | 3 | 0 | 0 | 2064 | 617 | 102 | 190 | 49082 | 5762904 | 322118 | 7.33 |
| pin | 2 | 2 | 0 | 0 | 115 | 103 | 17 | 32 | 5902 | 743765 | 86169 | 1.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The prompt `build-develop-prompt.sh refactor …` builds ends its report with `NEW_STEP:` lines (or `NEW_STEP: none`) and carries no `FLAGS:` line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 455 | 89 | 160 | 36073 | 4269098 | 289253 | 5.93 | 1360 | unknown | 2/5 | nothing-structural |
| SKILL.md's Refactor section passes the leaf's `NEW_STEP:` values to one `add-ledger-step.sh … after '<STEP>'` call after verify-refactor's final PASS, and commits the ledger with the refactor-pending clear ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 582 | 121 | 222 | 47416 | 6848041 | 358725 | 8.20 | 2886 | unknown | 2/5 | nothing-structural |
| SKILL.md's Refactor section marks each such insertion with a `step-added` event beside the `add-ledger-step.sh` call it made | 2 | 1 | 0 | 0 | 0 | 0 | 148 | 23 | 46 | 11103 | 1259990 | 106629 | 1.97 | unknown | unknown | unknown | unknown |
| SKILL.md's Refactor section narrates `add-ledger-step.sh` exit 1 as owed steps and does not bail on it ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 659 | 104 | 182 | 51700 | 5383110 | 333576 | 7.32 | 1917 | unknown | 3/5 | nothing-structural |
| `refactor-triage.sh` exits with the same code for a report with `NEW_STEP:` lines as for the same report without them ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 138 | 22 | 40 | 9757 | 1069909 | 97177 | 1.75 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 184 | 184 | 183 | 184 | 1 | 0 | 1 | 57 | 58 | 184 | 48 | 47 | 54 | 0 | 1 | 1 | 1 | 49 | 47 | 182 | 182 | 183 | 181 | 184 | 53 | 1 |
| fast | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 0 | 0 | 0 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 359 | 650 | 156049 | 18830148 | 1185360 | 25.17 |
