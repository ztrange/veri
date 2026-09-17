### 📊 Metrics — issue 168

Wall time for the issue: 12991 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/269.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 9 | 4 | 0 | 0 | 806 | 338 | 60 | 102 | 31933 | 2280581 | 338548 | 3.92 |
| green | 12 | 4 | 1 | 0 | 7297 | 450 | 92 | 168 | 27555 | 4045400 | 333509 | 4.58 |
| refactor | 11 | 4 | 1 | 0 | 4407 | 517 | 105 | 202 | 38705 | 5338614 | 361923 | 4.65 |
| pin | 1 | 1 | 0 | 0 | 71 | 66 | 16 | 18 | 4676 | 475987 | 39672 | 0.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2958 | 2.09 | 0 | 0.00 |
| refactor | 1924 | 1.70 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Given a ledger where two steps carry ` ⟦criterion k⟧` for the same k and only the first is ticked with no refactor-pending mark, a criterion-finished script exits 3 for criterion k; once both are ticked with no ` ⟂ refactor pending` mark it exits 0 ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 1 | 458 | 86 | 154 | 31474 | 3704618 | 327854 | 4.45 | 5088 | 2/2 | 0/5 | nothing-left |
| A ticked step that carries no ` ⟦criterion k⟧` token makes no criterion finished: for a criterion no step serves, the criterion-finished script exits 3 even when every step in the ledger is ticked and verified ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 250 | 57 | 112 | 18230 | 2892301 | 222576 | 2.35 | 1666 | unknown | 0/5 | nothing-left |
| `next-unchecked.sh`, `next-pending-refactor.sh`, `tick-ledger.sh` and `clear-refactor-pending.sh` each have a suite case on a ledger whose steps carry the ` ⟦criterion k⟧` notation, matching and printing step text exactly as they do without it ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 107 | 22 | 30 | 9006 | 716794 | 79323 | 0.93 | unknown | unknown | unknown | unknown |
| `SKILL.md`'s *Step done* and pin paths run the criterion-finished script and tick the issue criterion only on its exit 0, posting `### ✅ Step done` and ticking nothing on exit 3 ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 237 | 47 | 78 | 16159 | 1906826 | 199619 | 2.93 | 3265 | unknown | 0/5 | triage |
| `SKILL.md` step 2's plan-writing guidance tells the conductor to end each ledger step with ` ⟦criterion k⟧` for the criterion it serves, and to leave a gap step without one ⟦criterion 3⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 319 | 61 | 116 | 28000 | 2920043 | 244280 | 2.79 | 2805 | unknown | 1/5 | nothing-left |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 273 | 490 | 102869 | 12140582 | 1073652 | 13.45 |
