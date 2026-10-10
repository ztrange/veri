### 📊 Metrics — issue 1311

Wall time for the issue: 4385 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1390.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 1 | 2 | 1471 | 12489 | 31998 | 0.14 |
| red | 17 | 6 | 0 | 0 | 724 | 609 | 117 | 226 | 60142 | 5456809 | 781820 | 7.40 |
| green | 14 | 6 | 1 | 0 | 1463 | 421 | 106 | 206 | 39676 | 5000852 | 581615 | 5.13 |
| refactor | 12 | 6 | 0 | 0 | 397 | 163 | 52 | 96 | 14474 | 1921137 | 489521 | 3.52 |
| pin | 5 | 5 | 0 | 0 | 146 | 102 | 34 | 68 | 11941 | 1494906 | 203776 | 1.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 25 | 24 | 1 | 0 | 1360 | 399 | 126 | 244 | 43554 | 5106551 | 955303 | 4.77 |
| developer | claude-opus-5-5 | 24 | 0 | 0 | 0 | 1383 | 907 | 184 | 354 | 84150 | 8779642 | 1133427 | 12.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 789 | 1.27 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Given a pairs table with one row naming an old bash case, a kept bash case of the same suite it is redundant with, and a mutation patch to a production file, the pairs check (`mutation-parity.sh <pairs-table>`) applies the mutation, runs both cases, and — when the old case goes red, another case of its suite stays green and the kept case goes red — prints a report row naming the old case, the kept case, the mutation and the result `proven`, and exits 0 ⟦criterion 1⟧ | 7 | 3 | 1 | 0 | 0 | 0 | 236 | 52 | 102 | 22483 | 2567526 | 288185 | 2.56 | 1113 | 1/2 | 0/5 | nothing-left |  |  | full |
| A row whose valid mutation leaves its kept case green is reported `unproven`, the report naming that kept case, and the pairs check exits 1 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 116 | 32 | 60 | 10616 | 1273345 | 243767 | 1.85 | 295 | unknown | 0/5 | nothing-left |  |  | full |
| A row whose mutation leaves its old case green is reported `owed` (the mutation is not valid), and the pairs check exits 1 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 102 | 32 | 60 | 9884 | 1283518 | 245887 | 1.87 | 251 | unknown | 0/5 | nothing-left |  |  | full |
| A row whose mutation turns its old case red but leaves no other case of that suite green (the suite's count line says 0 passed, as a syntax error would) is reported `owed`, not proven or unproven, and the pairs check exits 1 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 22 | 3922 | 473347 | 84219 | 0.64 | unknown | unknown | unknown | unknown |  |  | pin |
| A row whose old case is replaced by a named pytest case (a node id) runs that pytest case under the mutation: proven when it goes red, unproven naming it when it stays green ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 33 | 66 | 13155 | 1490407 | 256329 | 2.05 | 281 | unknown | 0/5 | nothing-left |  |  | full |
| A row whose old case is itself a pytest node id judges validity against the other cases of that pytest file: valid when the node goes red and another case of the file stays green, owed otherwise ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 159 | 41 | 76 | 14718 | 1750042 | 258799 | 2.12 | 321 | unknown | 1/5 | nothing-left |  |  | full |
| Given a pairs table of several rows, the pairs check reports every row, restores the tree before applying the next row's mutation (so a later row's case runs without an earlier row's mutation in place), and exits 0 only when every row is proven and 1 when any row is unproven or owed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 14 | 28 | 7876 | 668324 | 92678 | 0.83 | unknown | unknown | unknown | unknown |  |  | pin |
| The pairs check exits 2 when a row's mutation does not apply to the tree ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 16 | 32 | 5428 | 768521 | 87475 | 0.75 | unknown | unknown | unknown | unknown |  |  | pin |
| The pairs check exits 2 when a row's case cannot be run: its suite path does not exist, its bash suite never reaches its count line, or its pytest node id is not collected ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 121 | 33 | 64 | 11378 | 1430474 | 258032 | 2.02 | 281 | unknown | 0/5 | nothing-left |  |  | full |
| After the pairs check exits 0 or 1, the working tree and the index are byte-identical to what they were before it, including a staged change, an unstaged change to a file a mutation patches, and an untracked file present beforehand ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 90 | 15 | 28 | 9263 | 679739 | 93074 | 0.86 | unknown | unknown | unknown | unknown |  |  | pin |
| After the pairs check exits 2 — a mutation that does not apply, or a case that cannot be run while a mutation is in place — the working tree and the index are byte-identical to what they were before it ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 123 | 20 | 40 | 13209 | 1025770 | 99878 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Given a pairs table with one row naming an old bash case, a kept bash case of the same suite it is redundant with, and a mutation patch to a production file, the pairs check (`mutation-parity.sh <pairs-table>`) applies the mutation, runs both cases, and — when the old case goes red, another case of its suite stays green and the kept case goes red — prints a report row naming the old case, the kept case, the mutation and the result `proven`, and exits 0 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 58 | 0.55 |
| A row whose valid mutation leaves its kept case green is reported `unproven`, the report naming that kept case, and the pairs check exits 1 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 63 | 0.56 |
| A row whose mutation leaves its old case green is reported `owed` (the mutation is not valid), and the pairs check exits 1 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 62 | 0.57 |
| A row whose old case is replaced by a named pytest case (a node id) runs that pytest case under the mutation: proven when it goes red, unproven naming it when it stays green ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 60 | 0.56 |
| A row whose old case is itself a pytest node id judges validity against the other cases of that pytest file: valid when the node goes red and another case of the file stays green, owed otherwise ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 94 | 0.70 |
| The pairs check exits 2 when a row's case cannot be run: its suite path does not exist, its bash suite never reaches its count line, or its pytest node id is not collected ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 60 | 0.58 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 0 | 32 | 424 | 23 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 3 | 2 | 2 | 3 |
| fast | 28 | 27 | 27 | 28 | 28 | 31 | 29 | 29 | 29 | 29 | 29 | 28 | 28 | 28 | 29 | 28 | 29 | 28 | 29 | 27 | 29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 4 | 1 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 310 | 598 | 127704 | 13886193 | 2088730 | 17.28 |
