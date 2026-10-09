### 📊 Metrics — issue 1224

Wall time for the issue: 2483 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1233.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 854 | 12385 | 29881 | 0.13 |
| red | 7 | 3 | 0 | 0 | 190 | 159 | 44 | 84 | 16561 | 1888628 | 300999 | 2.62 |
| green | 6 | 3 | 0 | 0 | 394 | 122 | 40 | 76 | 12607 | 1642359 | 236215 | 1.96 |
| refactor | 6 | 3 | 0 | 0 | 195 | 86 | 26 | 52 | 8221 | 1019405 | 234461 | 1.74 |
| pin | 1 | 1 | 0 | 0 | 15 | 12 | 4 | 8 | 1351 | 150934 | 37189 | 0.19 |
| diff | 2 | 1 | 0 | 0 | 95 | 34 | 11 | 22 | 3292 | 446546 | 73683 | 0.59 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 396 | 152 | 58 | 114 | 17819 | 2259999 | 443299 | 2.40 |
| developer | claude-opus-5-5 | 11 | 0 | 0 | 0 | 502 | 267 | 68 | 130 | 25067 | 2900258 | 469129 | 4.83 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| add-ledger-step.sh given `--criterion <k>` tags every inserted line `⟦criterion k⟧`, whatever criterion the anchor step carries ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 126 | 36 | 70 | 12317 | 1511595 | 244834 | 2.00 | 354 | unknown | 0/5 | nothing-left |  |  | full |
| add-ledger-step.sh called without `--criterion` still tags inserted lines with the anchor's criterion, and an anchor with no criterion still yields untagged lines ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 14 | 26 | 5718 | 617944 | 87991 | 0.78 | unknown | unknown | unknown | unknown |  |  | pin |
| add-ledger-step.sh given `--criterion <k>` for a k no ledger step carries exits 2 with one stderr line naming k and leaves the ledger byte-identical ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 31 | 58 | 10345 | 1182606 | 238443 | 1.85 | 290 | unknown | 0/5 | nothing-left |  |  | full |
| add-ledger-step.sh refusing a call with too few arguments prints a usage line that names the optional leading `--criterion <k>` ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 106 | 33 | 66 | 10360 | 1389181 | 237596 | 1.89 | 374 | unknown | 0/5 | nothing-left |  |  | full |
| the contract header of `skills/tdd/scripts/add-ledger-step.sh` says a leading `--criterion <k>` overrides the inherited criterion and lists the refusal of a criterion no ledger step carries among its exit-2 causes, and this step changes no other file ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 22 | 3292 | 446546 | 73683 | 0.59 | 120 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| add-ledger-step.sh given `--criterion <k>` tags every inserted line `⟦criterion k⟧`, whatever criterion the anchor step carries ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 77 | 0.63 |
| add-ledger-step.sh given `--criterion <k>` for a k no ledger step carries exits 2 with one stderr line naming k and leaves the ledger byte-identical ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 60 | 0.57 |
| add-ledger-step.sh refusing a call with too few arguments prints a usage line that names the optional leading `--criterion <k>` ⟦added⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 58 | 0.54 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 3 | 1 | 0 | 2 | 1 | 0 | 0 |
| fast | 28 | 28 | 28 | 28 | 30 | 29 | 26 | 26 | 27 | 25 | 27 | 27 |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 126 | 244 | 42886 | 5160257 | 912428 | 7.24 |
