### 📊 Metrics — issue 663

Wall time for the issue: 3709 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/672.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 8 | 2 | 4 | 746 | 59332 | 37367 | 0.33 |
| red | 13 | 5 | 0 | 0 | 556 | 453 | 108 | 212 | 41481 | 5337334 | 596156 | 6.67 |
| green | 14 | 5 | 2 | 0 | 1204 | 544 | 132 | 258 | 44965 | 6292332 | 551963 | 6.57 |
| refactor | 10 | 5 | 0 | 0 | 453 | 205 | 53 | 106 | 18237 | 2324188 | 420402 | 4.19 |
| pin | 3 | 3 | 0 | 0 | 74 | 50 | 15 | 28 | 4744 | 577628 | 122426 | 1.19 |
| structural | 2 | 0 | 0 | 0 | 54 | 39 | 10 | 20 | 3716 | 417450 | 77225 | 0.78 |
| transform | 1 | 1 | 0 | 0 | 33 | 23 | 5 | 10 | 2033 | 205688 | 39212 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 22 | 20 | 2 | 0 | 1115 | 516 | 135 | 266 | 45381 | 5880047 | 841159 | 8.81 |
| developer | claude-opus-5-5 | 22 | 0 | 0 | 0 | 1273 | 806 | 190 | 372 | 70541 | 9333905 | 1003592 | 11.31 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 774 | 3.86 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| the develop-refactor prompt template defines a third candidate class: a candidate whose transform would change only files under a tests/ directory is reported on a `CANDIDATES: test-only | <transform>` line, never on a `CANDIDATES: structural` line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 234 | 59 | 116 | 20146 | 2913680 | 270874 | 3.15 | 559 | unknown | 0/5 | nothing-left |  |  | full |
| `refactor-owed.sh append` keeps a `CANDIDATES: test-only` candidate in the owed file under its step's heading ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 171 | 45 | 88 | 13710 | 2041855 | 254741 | 2.72 | 370 | unknown | 0/5 | structural-owed |  |  | full |
| `refactor-owed.sh list` never prints a test-only candidate, and an owed file holding only test-only candidates makes `list` exit 3 with nothing on stdout ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 170 | 42 | 84 | 14717 | 1912982 | 251575 | 2.69 | 337 | unknown | 1/5 | structural-owed |  |  | full |
| `refactor-owed.sh list` on an owed file holding both structural and test-only candidates prints the structural candidates exactly as it does for a file holding them alone ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 14 | 28 | 5401 | 672639 | 86810 | 0.94 | unknown | unknown | unknown | unknown |  |  | pin |
| `refactor-owed.sh render` prints the test-only candidates under a heading of their own inside `## Refactor owed`, saying the structural pass does not work them ⟦criterion 4⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 336 | 74 | 144 | 28684 | 3429587 | 379642 | 4.30 | 715 | 2/2 | 1/5 | structural-owed |  |  | full |
| `refactor-triage.sh` treats a `CANDIDATES: test-only | …` line as no reason to launch another refactor leaf: a report whose only candidates are test-only exits 3, and one mixing structural and test-only prints only the structural transforms ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 129 | 38 | 74 | 12145 | 1663531 | 253558 | 2.60 | 324 | unknown | 0/5 | malformed |  |  | full |
| `refactor-overflow.sh` never files a test-only candidate: an owed file whose unreached candidates are all test-only files nothing and exits 3 ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 14 | 26 | 5087 | 609981 | 89031 | 0.94 | unknown | unknown | unknown | unknown |  |  | pin |
| a refactor report with only `structural` and `cosmetic` candidate lines is handled by `refactor-owed.sh append`/`list`/`render`, `refactor-triage.sh` and `refactor-overflow.sh` exactly as before ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 94 | 22 | 44 | 9537 | 1287227 | 104716 | 1.29 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| the develop-refactor prompt template defines a third candidate class: a candidate whose transform would change only files under a tests/ directory is reported on a `CANDIDATES: test-only | <transform>` line, never on a `CANDIDATES: structural` line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 67 | 0.77 |
| `refactor-owed.sh append` keeps a `CANDIDATES: test-only` candidate in the owed file under its step's heading ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 100 | 0.81 |
| `refactor-owed.sh list` never prints a test-only candidate, and an owed file holding only test-only candidates makes `list` exit 3 with nothing on stdout ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 96 | 0.90 |
| `refactor-owed.sh render` prints the test-only candidates under a heading of their own inside `## Refactor owed`, saying the structural pass does not work them ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 94 | 0.91 |
| `refactor-triage.sh` treats a `CANDIDATES: test-only | …` line as no reason to launch another refactor leaf: a report whose only candidates are test-only exits 3, and one mixing structural and test-only prints only the structural transforms ⟦criterion 5⟧ | 1 | 0/5 | malformed | PASS | 0 | 96 | 0.81 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 5 | 5 | 0 | 0 | 0 | 2 | 0 | 0 | 7 | 7 | 6 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 12 | 14 | 10 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 5 | 2 | 0 | 0 | 2 | 3 | 2 | 2 |
| fast | 26 | 25 | 26 | 25 | 25 | 25 | 25 | 25 | 26 | 25 | 25 | 25 | 25 | 25 | 25 | 24 | 25 | 26 | 24 | 25 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 4 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 325 | 638 | 115922 | 15213952 | 1844751 | 20.12 |
