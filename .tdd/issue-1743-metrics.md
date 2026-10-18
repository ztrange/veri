### 📊 Metrics — issue 1743

Wall time for the issue: 2398 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1753.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 866 | 0 | 30581 | 0.09 |
| red | 11 | 5 | 0 | 0 | 202 | 153 | 51 | 102 | 16553 | 1485659 | 200088 | 0.81 |
| green | 10 | 5 | 0 | 0 | 359 | 134 | 52 | 94 | 12302 | 1323093 | 149124 | 0.63 |
| refactor | 10 | 5 | 0 | 0 | 188 | 68 | 28 | 56 | 5307 | 713417 | 135584 | 0.46 |
| pin | 1 | 1 | 0 | 0 | 25 | 19 | 5 | 10 | 1593 | 138615 | 15091 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 17 | 0 | 0 | 446 | 195 | 67 | 132 | 16335 | 1763813 | 259291 | 0.99 |
| developer | claude-sonnet-5-5 | 16 | 0 | 0 | 0 | 338 | 186 | 70 | 132 | 20286 | 1896971 | 271177 | 1.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `claims <file> <unit>` on a unit whose table header is `| Requirement | ID |` (columns other than exactly `| ID | Requirement | Why |`) exits 2, prints nothing on stdout, and names the header's line number on stderr ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 66 | 24 | 48 | 6460 | 648623 | 106123 | 0.39 | 235 | unknown | 0/5 | nothing-left |  |  | full |
| `claims <file> <unit>` on a unit whose table has no leading pipes (`ID | Requirement | Why` header and rows) exits 2, prints nothing on stdout, and names the offending line number on stderr ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 61 | 24 | 44 | 6285 | 604675 | 89637 | 0.35 | 208 | unknown | 0/5 | nothing-left |  |  | full |
| `claims <file> <unit>` on a `## U` heading followed by prose and no table exits 2, prints nothing on stdout, and names the heading's line number on stderr, so a heading `units` does not list is never a silently empty unit for `claims` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 63 | 21 | 42 | 5502 | 571711 | 87871 | 0.33 | 188 | unknown | 0/5 | nothing-left |  |  | full |
| `claims <file> <unit>` on a unit holding a second `| ID | Requirement | Why |` table after its first exits 2, prints nothing on stdout, and names the second table's header line number on stderr ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 78 | 28 | 52 | 6612 | 737788 | 92429 | 0.37 | 189 | unknown | 0/5 | nothing-left |  |  | full |
| `claims <file> <unit>` keeps an escaped `\|` inside a requirement cell: the row `| A1 | Pipes a \| b. | Why. |` prints `A1<TAB>Pipes a \| b.` (the whole requirement, not cut at the escaped pipe) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 58 | 25 | 48 | 6066 | 665070 | 88673 | 0.35 | 170 | unknown | 0/5 | nothing-left |  |  | full |
| `units <file>` on a missing file exits 2 with exactly one stderr line naming the file, and no Python traceback ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 14 | 28 | 4830 | 432917 | 35154 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `claims <file> <unit>` on a unit whose table header is `| Requirement | ID |` (columns other than exactly `| ID | Requirement | Why |`) exits 2, prints nothing on stdout, and names the header's line number on stderr ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 38 | 0.09 |
| `claims <file> <unit>` on a unit whose table has no leading pipes (`ID | Requirement | Why` header and rows) exits 2, prints nothing on stdout, and names the offending line number on stderr ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 38 | 0.09 |
| `claims <file> <unit>` on a `## U` heading followed by prose and no table exits 2, prints nothing on stdout, and names the heading's line number on stderr, so a heading `units` does not list is never a silently empty unit for `claims` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| `claims <file> <unit>` on a unit holding a second `| ID | Requirement | Why |` table after its first exits 2, prints nothing on stdout, and names the second table's header line number on stderr ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.09 |
| `claims <file> <unit>` keeps an escaped `\|` inside a requirement cell: the row `| A1 | Pipes a \| b. | Why. |` prints `A1<TAB>Pipes a \| b.` (the whole requirement, not cut at the escaped pipe) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 |
| fast | 19 | 18 | 19 | 18 | 18 | 19 | 17 | 18 | 17 | 17 | 16 | 17 | 16 | 17 | 16 |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 137 | 264 | 36621 | 3660784 | 530468 | 2.06 |
