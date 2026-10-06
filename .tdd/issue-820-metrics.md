### 📊 Metrics — issue 820

Wall time for the issue: 3413 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1082.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 11 | 2 | 4 | 943 | 62654 | 41269 | 0.36 |
| red | 6 | 2 | 0 | 0 | 195 | 149 | 40 | 78 | 14389 | 1931443 | 292985 | 3.02 |
| green | 6 | 2 | 1 | 0 | 539 | 198 | 48 | 94 | 18425 | 2421793 | 245297 | 2.82 |
| refactor | 4 | 2 | 0 | 0 | 167 | 63 | 18 | 36 | 5926 | 785049 | 175274 | 1.68 |
| pin | 2 | 2 | 0 | 0 | 50 | 37 | 10 | 20 | 3680 | 436110 | 85160 | 0.84 |
| diff | 2 | 1 | 0 | 0 | 176 | 73 | 15 | 30 | 5254 | 711945 | 88665 | 0.96 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 11 | 10 | 1 | 0 | 658 | 303 | 75 | 148 | 27753 | 3612260 | 460675 | 4.96 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 485 | 228 | 58 | 114 | 20864 | 2736734 | 467975 | 4.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 359 | 1.83 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| refactor-triage.sh given a report whose `CANDIDATES: structural |` line has nothing after the bar exits 2, with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 39 | 76 | 13190 | 1822637 | 276674 | 2.84 | 417 | unknown | 0/5 | nothing-left |  |  | full |
| refactor-triage.sh given a report whose `CANDIDATES: structural |` line has only whitespace after the bar exits 2, with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 11 | 22 | 4806 | 515349 | 91060 | 0.93 | unknown | unknown | unknown | unknown |  |  | pin |
| refactor-owed.sh append given a report holding a `CANDIDATES: structural |` line with nothing after the bar and another structural candidate records only the other candidate under the step's heading, with no bare `- ` bullet ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 204 | 54 | 106 | 19627 | 2666881 | 340773 | 3.65 | 591 | 1/2 | 0/5 | nothing-left |  |  | full |
| refactor-owed.sh append given a report holding a `CANDIDATES: structural |` line with only whitespace after the bar and another structural candidate records only the other candidate under the step's heading ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 12 | 24 | 4797 | 569528 | 90209 | 0.93 | unknown | unknown | unknown | unknown |  |  | pin |
| no existing assertion in refactor-triage's or refactor-owed's suites (bash or pytest) changes, except one that pinned the empty-candidate defect, changed only to the exit code, stderr or file state criterion 1 or 2 names ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 15 | 30 | 5254 | 711945 | 88665 | 0.96 | 196 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| refactor-triage.sh given a report whose `CANDIDATES: structural |` line has nothing after the bar exits 2, with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 84 | 0.83 |
| refactor-owed.sh append given a report holding a `CANDIDATES: structural |` line with nothing after the bar and another structural candidate records only the other candidate under the step's heading, with no bare `- ` bullet ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.85 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 2 | 1 | 4 | 1 | 3 | 0 | 2 | 1 | 1 | 1 | 2 | 7 | 1 | 0 | 1 | 4 | 1 | 1 | 2 | 1 | 3 | 0 | 0 | 1 | 1 | 2 |
| fast | 46 | 41 | 41 | 46 | 46 | 42 | 41 | 41 | 40 | 41 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 1 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 133 | 262 | 48617 | 6348994 | 928650 | 9.67 |
