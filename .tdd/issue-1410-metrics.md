### 📊 Metrics — issue 1410

Wall time for the issue: 3200 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1426.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 1 | 2 | 1296 | 12489 | 31765 | 0.14 |
| red | 11 | 4 | 0 | 0 | 379 | 301 | 83 | 160 | 30721 | 3874698 | 501451 | 4.64 |
| green | 8 | 4 | 0 | 0 | 729 | 219 | 63 | 124 | 21105 | 2878524 | 336709 | 2.87 |
| refactor | 8 | 4 | 0 | 0 | 244 | 101 | 37 | 70 | 10279 | 1422891 | 322842 | 2.31 |
| pin | 3 | 3 | 0 | 0 | 57 | 46 | 19 | 38 | 5848 | 829817 | 123986 | 0.64 |
| predicate | 2 | 0 | 0 | 0 | 29 | 24 | 7 | 14 | 2012 | 258701 | 74650 | 0.69 |
| structural | 1 | 0 | 0 | 0 | 30 | 25 | 8 | 16 | 2654 | 365658 | 43519 | 0.47 |
| transform | 1 | 1 | 0 | 0 | 348 | 10 | 5 | 8 | 1183 | 154983 | 38828 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 17 | 0 | 0 | 900 | 229 | 86 | 168 | 27527 | 3496019 | 668916 | 3.30 |
| developer | claude-opus-5-5 | 18 | 0 | 0 | 0 | 929 | 508 | 137 | 264 | 47571 | 6301742 | 804834 | 8.65 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `ledger-steps.sh next-phase` answers exit 3, printing no phase, on a ledger whose only open phased step carries ` ⟂ <phase> owed` on its contract phase — neither the owed contract phase nor any phase listed after it is handed back ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 38 | 72 | 12317 | 1599586 | 248343 | 1.97 | 299 | unknown | 0/5 | nothing-left |  |  | full |
| A phased step whose contract phase is marked ` ⟂ <phase> owed` reads as `done` to `ledger-steps.sh`, and `next-unchecked.sh` skips it and hands over the next open step ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 18 | 36 | 5601 | 883361 | 89781 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| `tick-ledger.sh --phase-owed <phase> <ledger> <matcher>` appends ` ⟂ <phase> owed` to the matching phased step's line, leaving its checkbox `[ ]`, its expand and migrate marks and every other line byte-identical; exit 2, ledger untouched, when the step does not list that phase or it is not the step's next unmarked phase ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 38 | 74 | 13566 | 1682079 | 260758 | 2.09 | 294 | unknown | 0/5 | structural-owed |  |  | full |
| tick-ledger.sh's usage line, printed with exit 2 on a bad argument, names the `--phase-owed <phase>` flag beside `--phase <phase>` ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 35 | 70 | 10440 | 1526414 | 244192 | 1.90 | 361 | unknown | 0/5 | nothing-left |  |  | full |
| Marking a contract phase owed leaves it visible as owed: the bullet under `## Owed steps` is unchanged, the step's line says `owed` and never ` ⟂ <phase> done`, and its checkbox stays `[ ]` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 15 | 30 | 7325 | 731264 | 94891 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| On a ledger whose phased step has its contract filed under `## Owed steps` and marked owed, `ledger-steps.sh next-phase` and `next-unchecked.sh` run through their entry points both exit 3 ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 18 | 32 | 5547 | 777590 | 89274 | 0.78 | unknown | unknown | unknown | unknown |  |  | pin |
| `SKILL.md`'s exhausted-contract paragraph says to mark the contract phase owed with `tick-ledger.sh --phase-owed <phase>` before committing the ledger, pinned by a prose case ⟦criterion 3⟧ | 10 | 4 | 0 | 0 | 0 | 0 | 191 | 60 | 116 | 19006 | 2584978 | 414746 | 3.45 | 528 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `ledger-steps.sh next-phase` answers exit 3, printing no phase, on a ledger whose only open phased step carries ` ⟂ <phase> owed` on its contract phase — neither the owed contract phase nor any phase listed after it is handed back ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 61 | 0.59 |
| `tick-ledger.sh --phase-owed <phase> <ledger> <matcher>` appends ` ⟂ <phase> owed` to the matching phased step's line, leaving its checkbox `[ ]`, its expand and migrate marks and every other line byte-identical; exit 2, ledger untouched, when the step does not list that phase or it is not the step's next unmarked phase ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 60 | 0.60 |
| tick-ledger.sh's usage line, printed with exit 2 on a bad argument, names the `--phase-owed <phase>` flag beside `--phase <phase>` ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 53 | 0.55 |
| `SKILL.md`'s exhausted-contract paragraph says to mark the contract phase owed with `tick-ledger.sh --phase-owed <phase>` before committing the ledger, pinned by a prose case ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 70 | 0.57 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 20 | 19 | 0 | 144 | 2 | 337 |
| fast | 24 | 25 | 25 | 24 | 24 | 25 | 24 | 24 | 24 | 24 | 22 | 23 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 1 | 1 | 24 | 0 | 0 | 0 | 1 | 1 | 20 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 223 | 432 | 75098 | 9797761 | 1473750 | 11.95 |
