### 📊 Metrics — issue 1743

Wall time for the issue: 2573 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 13 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1753.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 866 | 0 | 30581 | 0.09 |
| red | 23 | 10 | 0 | 0 | 481 | 370 | 120 | 240 | 40030 | 3595317 | 427637 | 1.83 |
| green | 20 | 10 | 0 | 0 | 743 | 270 | 103 | 184 | 25180 | 2596917 | 303070 | 1.27 |
| refactor | 20 | 10 | 0 | 0 | 399 | 156 | 59 | 118 | 12185 | 1531982 | 276822 | 0.97 |
| pin | 3 | 3 | 0 | 0 | 62 | 45 | 15 | 30 | 4626 | 400887 | 62726 | 0.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 34 | 34 | 0 | 0 | 917 | 403 | 137 | 272 | 35107 | 3660434 | 522223 | 2.02 |
| developer | claude-sonnet-5-5 | 33 | 0 | 0 | 0 | 778 | 445 | 161 | 302 | 47780 | 4464669 | 578613 | 2.37 |

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
| `units <file>` and `claims <file> <unit>` agree on a `## U` heading whose only table header is `| Requirement | ID |`: one case runs both commands on that file, `units` does not print `U`, and `claims` exits 2 with nothing on stdout ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 14 | 28 | 4367 | 413465 | 72282 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |
| `claims <file> <unit>` on a unit whose valid table rows are followed, later under the same unit, by a `| Key | Requirement |` pipe line exits 2, prints nothing on stdout, and names that later line's number on stderr ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 94 | 31 | 58 | 9268 | 842992 | 95184 | 0.42 | 261 | unknown | 1/5 | nothing-structural |  |  | full |
| `claims <file> <unit>` on a unit whose valid table rows are followed, later under the same unit, by a `| Why | ID |` pipe line exits 2, prints nothing on stdout, and names that later line's number on stderr ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 12 | 24 | 4116 | 362534 | 34255 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| `claims <file> <unit>` on a unit whose valid table rows are followed, later under the same unit, by a header without leading pipes, `Key | Value`, exits 2, prints nothing on stdout, and names that later line's number on stderr ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 71 | 25 | 48 | 7448 | 675755 | 91453 | 0.37 | 233 | unknown | 0/5 | nothing-left |  |  | full |
| `claims <file> <unit>` on a unit whose only table header is `| Why | ID |` exits 2, prints nothing on stdout, and names the header line's number on stderr, never the unit's heading line and never saying there is no table ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 24 | 48 | 6971 | 684410 | 94621 | 0.37 | 224 | unknown | 0/5 | nothing-left |  |  | full |
| `claims <file> <unit>` on a unit whose only table header is `| Key | Requirement |` exits 2, prints nothing on stdout, and names the header line's number on stderr, never the unit's heading line and never saying there is no table ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 29 | 54 | 7856 | 778681 | 92698 | 0.39 | 221 | unknown | 0/5 | nothing-left |  |  | full |
| `claims <file> <unit>` on a unit whose table header is `| ID | Requirement | Why | Extra |` (an extra column) exits 2, prints nothing on stdout, and names the header line's number on stderr ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 63 | 26 | 50 | 6240 | 706482 | 89875 | 0.36 | 216 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `claims <file> <unit>` on a unit whose table header is `| Requirement | ID |` (columns other than exactly `| ID | Requirement | Why |`) exits 2, prints nothing on stdout, and names the header's line number on stderr ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 38 | 0.09 |
| `claims <file> <unit>` on a unit whose table has no leading pipes (`ID | Requirement | Why` header and rows) exits 2, prints nothing on stdout, and names the offending line number on stderr ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 38 | 0.09 |
| `claims <file> <unit>` on a `## U` heading followed by prose and no table exits 2, prints nothing on stdout, and names the heading's line number on stderr, so a heading `units` does not list is never a silently empty unit for `claims` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| `claims <file> <unit>` on a unit holding a second `| ID | Requirement | Why |` table after its first exits 2, prints nothing on stdout, and names the second table's header line number on stderr ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.09 |
| `claims <file> <unit>` keeps an escaped `\|` inside a requirement cell: the row `| A1 | Pipes a \| b. | Why. |` prints `A1<TAB>Pipes a \| b.` (the whole requirement, not cut at the escaped pipe) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.10 |
| `claims <file> <unit>` on a unit whose valid table rows are followed, later under the same unit, by a `| Key | Requirement |` pipe line exits 2, prints nothing on stdout, and names that later line's number on stderr ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 49 | 0.12 |
| `claims <file> <unit>` on a unit whose valid table rows are followed, later under the same unit, by a header without leading pipes, `Key | Value`, exits 2, prints nothing on stdout, and names that later line's number on stderr ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 39 | 0.10 |
| `claims <file> <unit>` on a unit whose only table header is `| Why | ID |` exits 2, prints nothing on stdout, and names the header line's number on stderr, never the unit's heading line and never saying there is no table ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 46 | 0.09 |
| `claims <file> <unit>` on a unit whose only table header is `| Key | Requirement |` exits 2, prints nothing on stdout, and names the header line's number on stderr, never the unit's heading line and never saying there is no table ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 40 | 0.10 |
| `claims <file> <unit>` on a unit whose table header is `| ID | Requirement | Why | Extra |` (an extra column) exits 2, prints nothing on stdout, and names the header line's number on stderr ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 37 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 1 | 2 | 2 | 2 | 0 | 2 | 1 | 2 | 2 | 1 | 1 | 2 | 1 |
| fast | 19 | 18 | 19 | 18 | 18 | 19 | 17 | 18 | 17 | 17 | 16 | 17 | 16 | 17 | 16 | 18 | 19 | 17 | 16 | 16 | 17 | 16 | 16 | 16 | 17 | 16 | 17 | 16 | 17 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 2 | 1 | 0 | 1 | 0 | 2 | 2 | 1 | 1 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 298 | 574 | 82887 | 8125103 | 1100836 | 4.39 |
