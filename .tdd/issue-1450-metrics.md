### 📊 Metrics — issue 1450

Wall time for the issue: 2354 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1462.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 15 | 2 | 4 | 1851 | 56633 | 38112 | 0.18 |
| red | 10 | 4 | 0 | 0 | 284 | 251 | 65 | 126 | 23518 | 2941405 | 443222 | 3.85 |
| green | 8 | 4 | 0 | 0 | 660 | 233 | 62 | 122 | 25142 | 2880737 | 350778 | 3.03 |
| refactor | 7 | 3 | 0 | 0 | 195 | 96 | 35 | 70 | 9408 | 1471869 | 283768 | 2.17 |
| pin | 2 | 2 | 0 | 0 | 38 | 30 | 11 | 22 | 3530 | 466774 | 81424 | 0.41 |
| predicate | 2 | 0 | 0 | 0 | 22 | 16 | 7 | 14 | 1811 | 256197 | 74701 | 0.69 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 14 | 0 | 0 | 500 | 211 | 73 | 146 | 24106 | 3066785 | 556683 | 2.77 |
| developer | claude-opus-5-5 | 16 | 0 | 0 | 0 | 717 | 430 | 109 | 212 | 41154 | 5006830 | 715322 | 7.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| ledger-steps.sh reports a step whose prose quotes a criterion marker with only the criterion of its trailing marker run, and a step whose prose quotes a phases marker as a plain open step whose next-phase answer is exit 3 ⟦criterion 1⟧ | 11 | 5 | 0 | 0 | 0 | 0 | 287 | 73 | 144 | 28136 | 3343158 | 483442 | 4.08 | 767 | unknown | 0/5 | nothing-structural |  |  | full |
| ledger-steps.sh reports a step whose prose quotes a full-suite, human-owed or diff-checked kind marker followed by a criterion marker as kind step, keeping the kind only when that marker sits in the trailing marker run ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 103 | 35 | 68 | 10977 | 1484433 | 247260 | 1.91 | 239 | unknown | 1/5 | nothing-left |  |  | full |
| next-unchecked.sh hands out an open step whose prose quotes a phases marker as an ordinary step, printing its text ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 15 | 30 | 5941 | 725723 | 91208 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| tick-ledger.sh ticks a step whose prose quotes a phases marker with a plain tick and no phase refusal ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 15 | 28 | 5773 | 665522 | 90170 | 0.76 | unknown | unknown | unknown | unknown |  |  | pin |
| criterion-finished.sh accepts a ledger whose step prose quotes a criterion marker, with no more-than-one-criterion-tag refusal, and counts that step only toward the criterion of its trailing marker run ⟦criterion 2⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 125 | 42 | 84 | 12582 | 1798146 | 321813 | 2.60 | 251 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| ledger-steps.sh reports a step whose prose quotes a criterion marker with only the criterion of its trailing marker run, and a step whose prose quotes a phases marker as a plain open step whose next-phase answer is exit 3 ⟦criterion 1⟧ | 2 | 0/5 | nothing-structural | PASS | 0 | 71 | 1.00 |
| ledger-steps.sh reports a step whose prose quotes a full-suite, human-owed or diff-checked kind marker followed by a criterion marker as kind step, keeping the kind only when that marker sits in the trailing marker run ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 70 | 0.63 |
| criterion-finished.sh accepts a ledger whose step prose quotes a criterion marker, with no more-than-one-criterion-tag refusal, and counts that step only toward the criterion of its trailing marker run ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 54 | 0.54 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 64 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 1 |
| fast | 26 | 25 | 26 | 25 | 26 | 26 | 25 | 24 | 24 | 25 | 26 | 26 | 25 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 182 | 358 | 65260 | 8073615 | 1272005 | 10.32 |
