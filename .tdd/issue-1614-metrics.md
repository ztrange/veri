### 📊 Metrics — issue 1614

Wall time for the issue: 1709 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1697.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 17 | 2 | 4 | 1900 | 57983 | 36027 | 0.17 |
| red | 3 | 1 | 0 | 0 | 117 | 77 | 20 | 38 | 6847 | 879168 | 129261 | 0.67 |
| green | 2 | 1 | 0 | 0 | 144 | 51 | 16 | 30 | 4868 | 667503 | 79067 | 0.43 |
| refactor | 2 | 1 | 0 | 0 | 68 | 26 | 7 | 14 | 1668 | 256644 | 70719 | 0.33 |
| pin | 1 | 1 | 0 | 0 | 22 | 15 | 5 | 10 | 1786 | 196613 | 36446 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 178 | 92 | 23 | 46 | 8800 | 900568 | 181902 | 0.91 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 194 | 94 | 27 | 50 | 8269 | 1157343 | 169618 | 0.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A step inserted or replaced through add-ledger-step.sh whose text carries ⟦full-suite⟧, ⟦human-owed⟧ or ⟦diff-checked⟧ is read by ledger-steps.sh with that kind (full-suite, human-owed, diff-checked), not as an ordinary step; pinned in-process (small pytest case, no process) for each of the three kinds ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 120 | 34 | 66 | 9935 | 1415394 | 232806 | 1.17 | 367 | unknown | 0/5 | nothing-left |  |  | full |
| A step inserted through add-ledger-step.sh whose text carries ⟦full-suite⟧, ⟦human-owed⟧ or ⟦diff-checked⟧ is still read as added: it counts against VERI_STEP_GROWTH exactly as an added step without a kind mark does, so a ledger whose budget is already full of such steps refuses the next insertion (exit 1, filed under ## Owed steps); pinned by a case ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 14 | 26 | 5234 | 584534 | 82687 | 0.44 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A step inserted or replaced through add-ledger-step.sh whose text carries ⟦full-suite⟧, ⟦human-owed⟧ or ⟦diff-checked⟧ is read by ledger-steps.sh with that kind (full-suite, human-owed, diff-checked), not as an ordinary step; pinned in-process (small pytest case, no process) for each of the three kinds ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 68 | 0.33 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 17 | 2 |
| fast | 18 | 18 | 17 |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 1 | 0 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 96 | 17069 | 2057911 | 351520 | 1.78 |
