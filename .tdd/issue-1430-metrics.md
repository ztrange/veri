### 📊 Metrics — issue 1430

Wall time for the issue: 1520 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1444.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 3 | 6 | 995 | 105443 | 37663 | 0.17 |
| red | 2 | 1 | 0 | 0 | 47 | 39 | 10 | 20 | 4367 | 429141 | 85599 | 0.67 |
| green | 2 | 1 | 0 | 0 | 84 | 31 | 12 | 22 | 3494 | 469050 | 79414 | 0.60 |
| refactor | 2 | 1 | 0 | 0 | 355 | 18 | 9 | 16 | 1806 | 316718 | 78993 | 0.55 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 411 | 44 | 18 | 32 | 5090 | 625832 | 154744 | 0.73 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 86 | 53 | 16 | 32 | 5572 | 694520 | 126925 | 1.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tick-ledger.sh --phase-owed with a phase other than contract-a or contract-b (expand or migrate) exits 2, leaves the ledger byte-identical, and names that phase in its refusal on stderr, while --phase-owed contract-a and contract-b still mark the phase owed as today ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 31 | 58 | 9667 | 1214909 | 244006 | 1.83 | 568 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tick-ledger.sh --phase-owed with a phase other than contract-a or contract-b (expand or migrate) exits 2, leaves the ledger byte-identical, and names that phase in its refusal on stderr, while --phase-owed contract-a and contract-b still mark the phase owed as today ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 355 | 0.55 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 0 | 310 |
| fast | 23 | 23 | 22 |  |  |
| target | 1 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 34 | 64 | 10662 | 1320352 | 281669 | 2.00 |
