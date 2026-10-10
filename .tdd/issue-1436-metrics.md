### 📊 Metrics — issue 1436

Wall time for the issue: 1620 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1452.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 847 | 12489 | 32055 | 0.14 |
| red | 5 | 2 | 0 | 0 | 157 | 121 | 30 | 60 | 12495 | 1411836 | 228231 | 1.97 |
| green | 4 | 2 | 0 | 0 | 196 | 60 | 22 | 44 | 5975 | 944921 | 159269 | 1.19 |
| refactor | 4 | 2 | 0 | 0 | 107 | 42 | 15 | 30 | 3859 | 589934 | 164383 | 1.15 |
| pin | 1 | 1 | 0 | 0 | 19 | 12 | 4 | 8 | 1375 | 156931 | 40105 | 0.19 |
| predicate | 1 | 0 | 0 | 0 | 18 | 16 | 5 | 10 | 1366 | 204656 | 37726 | 0.37 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 241 | 83 | 31 | 62 | 10128 | 1223677 | 310616 | 1.47 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 265 | 174 | 46 | 92 | 15789 | 2097090 | 351153 | 3.54 |

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
| A pairs-table row whose old bash case fails under its mutation with a FAIL line of the form `<old name> (<diagnostic>)` reads `proven` when the kept case catches the mutation, not `owed` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 105 | 31 | 62 | 9782 | 1357994 | 251989 | 1.91 | 292 | unknown | 0/5 | structural-owed |  |  | full |
| A kept bash case whose FAIL line under the mutation is `<kept name> (<diagnostic>)` counts as catching the mutation, so the row reads `proven` rather than `unproven` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 83 | 30 | 60 | 8865 | 1291208 | 248494 | 1.86 | 262 | unknown | 0/5 | nothing-structural |  |  | full |
| A FAIL line that merely starts with the old case's name but continues with anything other than end of line or ` (` — another case whose name extends it — does not count as the old case failing, so the row reads `owed` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 63 | 15 | 30 | 6423 | 659076 | 129231 | 1.10 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A pairs-table row whose old bash case fails under its mutation with a FAIL line of the form `<old name> (<diagnostic>)` reads `proven` when the kept case catches the mutation, not `owed` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 57 | 0.58 |
| A kept bash case whose FAIL line under the mutation is `<kept name> (<diagnostic>)` counts as catching the mutation, so the row reads `proven` rather than `unproven` ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 50 | 0.56 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 |
| fast | 24 | 24 | 25 | 26 | 26 | 26 |  |  |  |  |  |
| target | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 77 | 154 | 25917 | 3320767 | 661769 | 5.01 |
