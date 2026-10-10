### 📊 Metrics — issue 1309

Wall time for the issue: 2681 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1383.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 8 | 1 | 2 | 1093 | 10863 | 33257 | 0.15 |
| red | 11 | 5 | 0 | 0 | 362 | 290 | 78 | 148 | 27168 | 3629813 | 505552 | 4.37 |
| green | 12 | 5 | 1 | 0 | 688 | 238 | 74 | 144 | 26173 | 3213640 | 465939 | 3.80 |
| refactor | 10 | 5 | 0 | 0 | 397 | 188 | 59 | 116 | 18304 | 2603692 | 415163 | 3.26 |
| pin | 1 | 1 | 0 | 0 | 17 | 12 | 5 | 10 | 1547 | 206845 | 39383 | 0.19 |
| predicate | 2 | 0 | 0 | 0 | 32 | 22 | 6 | 12 | 1281 | 208782 | 73846 | 0.66 |
| structural | 2 | 0 | 0 | 0 | 43 | 34 | 7 | 14 | 2587 | 257892 | 74642 | 0.70 |
| transform | 2 | 0 | 2 | 0 | 21 | 12 | 6 | 12 | 1268 | 236057 | 41520 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 20 | 17 | 3 | 0 | 714 | 272 | 97 | 188 | 29636 | 3892787 | 711229 | 3.53 |
| developer | claude-opus-5-5 | 21 | 0 | 0 | 0 | 859 | 532 | 139 | 270 | 49785 | 6474797 | 938073 | 9.80 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 225 | 1.21 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 42 | 0.40 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On an open ledger step whose line lists its phases (expand, migrate, contract (a), contract (b)), `tick-ledger.sh --phase expand <ledger> <matcher>` writes the expand phase's mark onto that same line in one write and exits 0, leaving the step unchecked and every other line unchanged ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 145 | 42 | 84 | 15062 | 2063106 | 272545 | 2.31 | 361 | unknown | 2/5 | nothing-structural |  |  | full |
| `ledger-steps.sh next-phase` prints, for the first phased step not yet finished, which of its phases is next — expand on a step with no phase marked, migrate once expand is marked — and exits 3 when no phased step is unfinished ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 200 | 57 | 110 | 20310 | 2671011 | 324030 | 2.86 | 458 | 1/2 | 2/5 | nothing-structural |  |  | full |
| Once `tick-ledger.sh --phase` has marked every phase a step lists, in the order expand, migrate, contract (a), contract (b), readers treat it as a finished step: `ledger-steps.sh` reports it done, `next-unchecked.sh` no longer answers it, and `ledger-steps.sh next-phase` moves on to the next unfinished phased step ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 39 | 72 | 13636 | 1646943 | 259579 | 2.07 | 306 | unknown | 0/5 | structural-owed |  |  | full |
| For a phased step that lists only some phases (say expand and contract (b)), `ledger-steps.sh next-phase` never answers a phase the step does not list: after expand is marked it answers contract (b), not migrate ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 13 | 26 | 4515 | 585133 | 82819 | 0.68 | unknown | unknown | unknown | unknown |  |  | pin |
| `tick-ledger.sh --phase <phase>` naming a phase the matched step does not list exits 2 and leaves the ledger byte-identical ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 109 | 34 | 66 | 10246 | 1436938 | 247731 | 1.91 | 283 | unknown | 0/5 | nothing-left |  |  | full |
| `tick-ledger.sh --phase <phase>` naming a listed phase while an earlier phase the step lists is still unmarked (migrate before expand) exits 2 and leaves the ledger byte-identical ⟦criterion 2⟧ | 12 | 3 | 2 | 0 | 0 | 0 | 166 | 50 | 98 | 14559 | 1953590 | 429341 | 3.36 | 267 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| On an open ledger step whose line lists its phases (expand, migrate, contract (a), contract (b)), `tick-ledger.sh --phase expand <ledger> <matcher>` writes the expand phase's mark onto that same line in one write and exits 0, leaving the step unchecked and every other line unchanged ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 86 | 0.70 |
| `ledger-steps.sh next-phase` prints, for the first phased step not yet finished, which of its phases is next — expand on a step with no phase marked, migrate once expand is marked — and exits 3 when no phased step is unfinished ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 105 | 0.80 |
| Once `tick-ledger.sh --phase` has marked every phase a step lists, in the order expand, migrate, contract (a), contract (b), readers treat it as a finished step: `ledger-steps.sh` reports it done, `next-unchecked.sh` no longer answers it, and `ledger-steps.sh next-phase` moves on to the next unfinished phased step ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 71 | 0.61 |
| `tick-ledger.sh --phase <phase>` naming a phase the matched step does not list exits 2 and leaves the ledger byte-identical ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 75 | 0.60 |
| `tick-ledger.sh --phase <phase>` naming a listed phase while an earlier phase the step lists is still unmarked (migrate before expand) exits 2 and leaves the ledger byte-identical ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 60 | 0.54 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 3 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 1 |
| fast | 28 | 28 | 28 | 28 | 29 | 28 | 28 | 28 | 28 | 26 | 27 | 28 | 27 | 27 | 28 | 28 | 27 | 28 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 236 | 458 | 79421 | 10367584 | 1649302 | 13.33 |
