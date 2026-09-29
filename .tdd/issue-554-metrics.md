### 📊 Metrics — issue 554

Wall time for the issue: 0 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 2334 s, excluded from it.
Steps done: 8 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/561.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 0 | 9 | 1 | 2 | 1209 | 11624 | 27200 | 0.12 |
| red | 17 | 7 | 0 | 0 | 0 | 372 | 84 | 166 | 39761 | 3197610 | 626724 | 3.54 |
| green | 20 | 6 | 4 | 0 | 0 | 564 | 167 | 318 | 62070 | 7221542 | 740889 | 5.03 |
| refactor | 12 | 6 | 0 | 0 | 0 | 126 | 43 | 86 | 12747 | 1469212 | 398825 | 2.02 |
| exhausted | 1 | 0 | 0 | 0 | 0 | 86 | 22 | 42 | 10477 | 1426348 | 76258 | 0.70 |
| pin | 2 | 2 | 0 | 0 | 0 | 22 | 8 | 16 | 2068 | 273794 | 65007 | 0.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 6.80 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| projects/docs/ carries the generator and its inputs (build-walkthrough.py, check-walkthrough.py, wt/*, docs-owed.sh, merge-gates.sh, hooks/reference-transaction, walkthrough.html) with ROOT resolved to the repo root two levels up, and `python3 projects/docs/build-walkthrough.py --stdout` is byte-identical to `python3 docs/build-walkthrough.py --stdout` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 83 | 25 | 48 | 9572 | 855860 | 198864 | 1.06 | 0 | unknown | 0/5 | nothing-left |  |  | full |
| the seven pipeline suites (build-guards, commentary-figures, docs-guard-filter, docs-owed, generator-inputs, lane-insulation, merge-gates) are copied to projects/docs/tests/ naming projects/docs/… paths, and each ends in its `<n> passed, 0 failed` count line when run directly, with the ADR suites and suite-lanes not copied ⟦criterion 1⟧ | 15 | 4 | 3 | 0 | 0 | 0 | 520 | 134 | 262 | 55874 | 6590707 | 621252 | 4.36 | 0 | 2/2 | 0/5 | structural-owed |  |  | full |
| the copied docs-owed.sh and merge-gates.sh in projects/docs/ name projects/docs/ paths (walkthrough.html, wt/, tests/) instead of docs/ ones, so each works when run from the copy ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 148 | 41 | 80 | 17347 | 1553217 | 263033 | 1.54 | 0 | 1/2 | 1/5 | nothing-structural |  |  | full |
| the copied docs-owed.sh in projects/docs/ names projects/docs/ paths (walkthrough.html, wt/, tests/) instead of docs/ ones, so it works when run from the copy ⟦added⟧ ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 141 | 39 | 74 | 14621 | 1464721 | 263084 | 1.49 | 0 | 1/2 | 0/5 | nothing-left |  |  | full |
| a projects/docs/Makefile exists, so the copied scripts and suites that call make from projects/docs/ resolve ⟦added⟧ ⟦criterion 1⟧ | 5 | 3 | 0 | 0 | 0 | 0 | 106 | 33 | 64 | 10732 | 1289035 | 180017 | 1.09 | 0 | unknown | 1/5 | structural-owed |  |  | full |
| `make -C projects/docs test` runs every suite globbed from projects/docs/tests/ and fails, naming the suite, one that never reaches its count line ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 42 | 13 | 26 | 4605 | 471301 | 104785 | 0.56 | unknown | unknown | unknown | unknown |  |  | pin |
| projects/docs/Makefile also carries the `docs`, `fresh` and `check` targets, working from the copy's paths | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 8 | 16 | 3817 | 290968 | 71463 | 0.38 | unknown | unknown | unknown | unknown |  |  | pin |
| projects/docs/CLAUDE.md carries the docs project's working notes (the one trap, the docs command rows, the docs-suite rules) written for the projects/docs/ paths | 6 | 3 | 0 | 0 | 0 | 0 | 99 | 31 | 58 | 10555 | 1072697 | 205205 | 1.14 | 0 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| projects/docs/ carries the generator and its inputs (build-walkthrough.py, check-walkthrough.py, wt/*, docs-owed.sh, merge-gates.sh, hooks/reference-transaction, walkthrough.html) with ROOT resolved to the repo root two levels up, and `python3 projects/docs/build-walkthrough.py --stdout` is byte-identical to `python3 docs/build-walkthrough.py --stdout` ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 0 | 0.29 |
| the copied docs-owed.sh and merge-gates.sh in projects/docs/ name projects/docs/ paths (walkthrough.html, wt/, tests/) instead of docs/ ones, so each works when run from the copy ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 0 | 0.37 |
| the copied docs-owed.sh in projects/docs/ names projects/docs/ paths (walkthrough.html, wt/, tests/) instead of docs/ ones, so it works when run from the copy ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 0 | 0.33 |
| a projects/docs/Makefile exists, so the copied scripts and suites that call make from projects/docs/ resolve ⟦added⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 0 | 0.17 |
| the seven pipeline suites (build-guards, commentary-figures, docs-guard-filter, docs-owed, generator-inputs, lane-insulation, merge-gates) are copied to projects/docs/tests/ naming projects/docs/… paths, and each ends in its `<n> passed, 0 failed` count line when run directly, with the ADR suites and suite-lanes not copied ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 0 | 0.37 |
| projects/docs/CLAUDE.md carries the docs project's working notes (the one trap, the docs command rows, the docs-suite rules) written for the projects/docs/ paths | 1 | 0/5 | nothing-left | PASS | 0 | 0 | 0.32 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
