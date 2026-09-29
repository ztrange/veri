### 📊 Metrics — issue 554

Wall time for the issue: unknown s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 1 of 7 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 0 | 9 | 1 | 2 | 1209 | 11624 | 27200 | 0.12 |
| red | 4 | 2 | 0 | 0 | 0 | 74 | 18 | 36 | 9391 | 663323 | 140202 | 0.79 |
| green | 8 | 1 | 3 | 0 | 0 | 228 | 68 | 132 | 26887 | 2972466 | 301379 | 2.07 |
| refactor | 2 | 1 | 0 | 0 | 0 | 13 | 5 | 10 | 1312 | 150212 | 60786 | 0.29 |
| exhausted | 1 | 0 | 0 | 0 | 0 | 86 | 22 | 42 | 10477 | 1426348 | 76258 | 0.70 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.41 |
| green | 0 | 0.00 | 0 | 1.67 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.70 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| projects/docs/ carries the generator and its inputs (build-walkthrough.py, check-walkthrough.py, wt/*, docs-owed.sh, merge-gates.sh, hooks/reference-transaction, walkthrough.html) with ROOT resolved to the repo root two levels up, and `python3 projects/docs/build-walkthrough.py --stdout` is byte-identical to `python3 docs/build-walkthrough.py --stdout` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 83 | 25 | 48 | 9572 | 855860 | 198864 | 1.06 | 0 | unknown | 0/5 | nothing-left |  |  | full |
| the seven pipeline suites (build-guards, commentary-figures, docs-guard-filter, docs-owed, generator-inputs, lane-insulation, merge-gates) are copied to projects/docs/tests/ naming projects/docs/… paths, and each ends in its `<n> passed, 0 failed` count line when run directly, with the ADR suites and suite-lanes not copied ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 318 | 88 | 172 | 38495 | 4356489 | 379761 | 2.78 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| projects/docs/ carries the generator and its inputs (build-walkthrough.py, check-walkthrough.py, wt/*, docs-owed.sh, merge-gates.sh, hooks/reference-transaction, walkthrough.html) with ROOT resolved to the repo root two levels up, and `python3 projects/docs/build-walkthrough.py --stdout` is byte-identical to `python3 docs/build-walkthrough.py --stdout` ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 0 | 0.29 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 4 | 3 | 4 | 0 | 0 | 4 | 0 | 0 | 242 |
| fast | 21 | 3 | 3 | 3 | 3 | 4 | 3 |  |  |  |  |
| target | 4 | 0 | 0 | 0 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 114 | 222 | 49276 | 5223973 | 605825 | 3.96 |
