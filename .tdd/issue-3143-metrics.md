### 📊 Metrics — issue 3143

Wall time for the issue: 3687 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 8 planned.
Outcome: the run bailed — missing-reroutes-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.73 over 76 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92084 tokens, largest 198547 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 92084 |
| 2 | $0.08 | 99597 |
| 3 | $0.03 | 101270 |
| 4 | $0.04 | 103194 |
| 5 | $0.04 | 105353 |
| 6 | $0.02 | 105751 |
| 7 | $0.03 | 106232 |
| 8 | $0.02 | 106487 |
| 9 | $0.03 | 106980 |
| 10 | $0.02 | 107238 |
| 11 | $0.03 | 107932 |
| 12 | $0.03 | 109410 |
| 13 | $0.06 | 113711 |
| 14 | $0.03 | 115149 |
| 15 | $0.03 | 116633 |
| 16 | $0.03 | 117509 |
| 17 | $0.04 | 119062 |
| 18 | $0.04 | 121704 |
| 19 | $0.03 | 122792 |
| 20 | $0.08 | 129853 |
| 21 | $0.04 | 131677 |
| 22 | $0.03 | 132403 |
| 23 | $0.07 | 138285 |
| 24 | $0.03 | 138780 |
| 25 | $0.05 | 141801 |
| 26 | $0.04 | 142722 |
| 27 | $0.03 | 143515 |
| 28 | $0.03 | 143909 |
| 29 | $0.03 | 144291 |
| 30 | $0.05 | 146405 |
| 31 | $0.04 | 147800 |
| 32 | $0.03 | 148380 |
| 33 | $0.04 | 149934 |
| 34 | $0.03 | 150546 |
| 35 | $0.04 | 151177 |
| 36 | $0.04 | 152484 |
| 37 | $0.04 | 153419 |
| 38 | $0.06 | 157012 |
| 39 | $0.03 | 157422 |
| 40 | $0.04 | 158064 |
| 41 | $0.04 | 158945 |
| 42 | $0.04 | 159619 |
| 43 | $0.04 | 160779 |
| 44 | $0.04 | 161622 |
| 45 | $0.04 | 162384 |
| 46 | $0.03 | 162696 |
| 47 | $0.04 | 163476 |
| 48 | $0.04 | 164013 |
| 49 | $0.04 | 165334 |
| 50 | $0.04 | 165958 |
| 51 | $0.04 | 166830 |
| 52 | $0.04 | 167362 |
| 53 | $0.05 | 168876 |
| 54 | $0.04 | 169526 |
| 55 | $0.08 | 175179 |
| 56 | $0.04 | 176385 |
| 57 | $0.04 | 177009 |
| 58 | $0.04 | 177412 |
| 59 | $0.05 | 179108 |
| 60 | $0.04 | 179696 |
| 61 | $0.05 | 181350 |
| 62 | $0.05 | 182688 |
| 63 | $0.04 | 183120 |
| 64 | $0.05 | 184564 |
| 65 | $0.04 | 185272 |
| 66 | $0.04 | 185776 |
| 67 | $0.05 | 186968 |
| 68 | $0.05 | 189095 |
| 69 | $0.04 | 189651 |
| 70 | $0.05 | 190716 |
| 71 | $0.04 | 191102 |
| 72 | $0.05 | 191950 |
| 73 | $0.04 | 192390 |
| 74 | $0.05 | 193474 |
| 75 | $0.04 | 193965 |
| 76 | $0.08 | 198547 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 3 | 1 | 2 | 0 | 75 | 64 | 13 | 26 | 6141 | 370137 | 72322 | 0.28 |
| red | 7 | 3 | 1 | 0 | 398 | 161 | 35 | 70 | 12468 | 1022367 | 139234 | 0.69 |
| green | 12 | 1 | 5 | 0 | 1309 | 292 | 66 | 126 | 21889 | 1904668 | 189811 | 1.02 |
| refactor | 1 | 0 | 0 | 0 | 8 | 5 | 2 | 4 | 157 | 48450 | 13962 | 0.04 |
| red-missing | 3 | 0 | 0 | 0 | 116 | 73 | 13 | 24 | 7009 | 330423 | 71685 | 0.28 |
| pin | 2 | 2 | 0 | 0 | 77 | 48 | 9 | 18 | 3739 | 254487 | 32352 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 7 | 8 | 0 | 1117 | 340 | 63 | 126 | 26876 | 1805016 | 248003 | 1.07 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 787 | 247 | 60 | 112 | 18830 | 1640942 | 230517 | 1.06 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 79 | 56 | 15 | 30 | 5697 | 484574 | 40846 | 0.32 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 268 | 0.51 |
| green | 0 | 0.00 | 1073 | 0.86 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 116 | 0.28 |
| pin | 0 | 0.00 | 77 | 0.14 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `plan-reverify.sh`, a new `/bin/sh` shim over `veri/plan_reverify.py`, called with no argument exits 2 printing the usage line `usage: plan-reverify.sh <ledger-file>` on stderr; its case asserts that line by name, so the repo-wide unreachable audit (`test_main_lists_no_unreachable_script_in_this_repository`) lists the script as `test-only:` and stays green until RESUME.md becomes its caller in a later step; unit-tier, run in-process with `run_cli` ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 96 | 24 | 46 | 6022 | 652688 | 98693 | 0.37 | 499 | unknown | 0/5 | nothing-left |  |  | full |
| `plan-reverify.sh <ledger-file>` exits 0 (verify-plan owed) when the ledger's history holds a `plan:` commit newer than the last verify-plan PASS verdict event (actor verifier, phase plan, verdict PASS) in the `events.jsonl` beside the ledger, so the resume runs verify-plan before any `step-start`; unit-tier cases faking git, no real process ⟦criterion 1⟧ | 20 | 4 | 6 | 0 | 0 | 0 | 483 | 101 | 196 | 39240 | 2907707 | 348351 | 1.80 | unknown | green 1/2, red 1/2 | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `plan-reverify.sh`, a new `/bin/sh` shim over `veri/plan_reverify.py`, called with no argument exits 2 printing the usage line `usage: plan-reverify.sh <ledger-file>` on stderr; its case asserts that line by name, so the repo-wide unreachable audit (`test_main_lists_no_unreachable_script_in_this_repository`) lists the script as `test-only:` and stays green until RESUME.md becomes its caller in a later step; unit-tier, run in-process with `run_cli` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 10 | 7 | 5 | 3 | 4 | 3 | 4 | 5 | 6 | 5 | 5 | 6 | 5 | 6 | 5 |
| fast | 81 | 52 | 51 | 39 | 83 | 44 | 64 | 58 | 72 | 44 | 55 | 52 | 43 |  |  |  |  |
| target | 7 | 6 | 5 | 6 | 4 | 4 | 4 | 4 | 5 | 5 | 4 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 138 | 268 | 51403 | 3930532 | 519366 | 6.18 (estimate) |
