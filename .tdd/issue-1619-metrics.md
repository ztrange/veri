### 📊 Metrics — issue 1619

Wall time for the issue: 3452 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1698.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 11 | 4 | 8 | 1162 | 148563 | 35145 | 0.17 |
| red | 6 | 2 | 0 | 0 | 182 | 142 | 40 | 80 | 15616 | 1756287 | 240479 | 1.50 |
| green | 6 | 2 | 1 | 0 | 318 | 128 | 41 | 78 | 13577 | 1666220 | 188607 | 1.24 |
| refactor | 4 | 2 | 0 | 0 | 98 | 46 | 20 | 38 | 4492 | 736887 | 144381 | 0.70 |
| pin | 1 | 1 | 0 | 0 | 31 | 23 | 8 | 16 | 2875 | 336331 | 37566 | 0.21 |
| rebase | 2 | 1 | 0 | 0 | 1241 | 30 | 13 | 24 | 2681 | 482625 | 70858 | 0.36 |
| predicate | 1 | 0 | 0 | 0 | 11 | 6 | 3 | 6 | 501 | 100756 | 32409 | 0.14 |
| structural | 1 | 0 | 0 | 0 | 8 | 4 | 2 | 4 | 282 | 56711 | 33369 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 936 | 177 | 60 | 114 | 18623 | 2318512 | 326649 | 1.72 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 768 | 105 | 43 | 86 | 11621 | 1791099 | 297574 | 1.49 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 201 | 108 | 28 | 54 | 10942 | 1174769 | 158591 | 1.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 232 | 0.84 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When .tdd/events.jsonl holds a line that is not valid JSON and the ledger already has a ⟦suite-repair⟧ step, add-ledger-step.sh inserting another ⟦suite-repair⟧ step exits 2 (never 1), its stderr names the log's path and the line it could not read, and the ledger is left byte-identical — pinned by a case with a malformed line ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 155 | 50 | 94 | 15334 | 1998074 | 265859 | 1.60 | 458 | 1/2 | 0/5 | structural-owed |  |  | full |
| When .tdd/events.jsonl holds a line that is not valid UTF-8 and the ledger already has a ⟦suite-repair⟧ step, add-ledger-step.sh inserting another ⟦suite-repair⟧ step exits 2 (no traceback), its stderr names the log path and the unreadable line, and the ledger is left byte-identical ⟦added⟧ ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 135 | 42 | 84 | 14727 | 1744929 | 266260 | 1.60 | 328 | 1/2 | 0/5 | nothing-structural |  |  | full |
| Run as a process through its add-ledger-step.sh entry point, with .tdd/events.jsonl holding a line that is not valid UTF-8 and the ledger already holding a ⟦suite-repair⟧ step, inserting another ⟦suite-repair⟧ step exits 2 with no traceback, stderr naming the log path, and the ledger byte-identical — pinned in the entry-point contract suite ⟦added⟧ ⟦criterion 1⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 89 | 35 | 68 | 9963 | 1392814 | 215550 | 1.10 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When .tdd/events.jsonl holds a line that is not valid JSON and the ledger already has a ⟦suite-repair⟧ step, add-ledger-step.sh inserting another ⟦suite-repair⟧ step exits 2 (never 1), its stderr names the log's path and the line it could not read, and the ledger is left byte-identical — pinned by a case with a malformed line ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 44 | 0.33 |
| When .tdd/events.jsonl holds a line that is not valid UTF-8 and the ledger already has a ⟦suite-repair⟧ step, add-ledger-step.sh inserting another ⟦suite-repair⟧ step exits 2 (no traceback), its stderr names the log path and the unreadable line, and the ledger is left byte-identical ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 54 | 0.37 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 0 | 16 | 1 | 2 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 |
| fast | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 |  |  |  |  |  |  |
| target | 16 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 |  |  |  |  |
| all | 600 | 607 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 131 | 254 | 41186 | 5284380 | 782814 | 4.46 |
