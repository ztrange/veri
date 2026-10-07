### 📊 Metrics — issue 1018

Wall time for the issue: 1174 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1098.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 946 | 12001 | 31147 | 0.14 |
| red | 5 | 2 | 0 | 0 | 129 | 113 | 31 | 58 | 11008 | 1326000 | 216964 | 1.89 |
| green | 4 | 2 | 0 | 0 | 191 | 108 | 30 | 60 | 10926 | 1355696 | 164085 | 1.43 |
| refactor | 4 | 2 | 0 | 0 | 123 | 79 | 24 | 48 | 6998 | 1043841 | 161661 | 1.30 |
| pin | 1 | 1 | 0 | 0 | 13 | 10 | 3 | 6 | 976 | 103804 | 38221 | 0.18 |
| diff | 2 | 1 | 0 | 0 | 80 | 27 | 9 | 18 | 2478 | 349032 | 73002 | 0.54 |
| predicate | 1 | 0 | 0 | 0 | 12 | 9 | 4 | 8 | 781 | 149128 | 36826 | 0.34 |
| structural | 1 | 0 | 0 | 0 | 31 | 12 | 4 | 8 | 942 | 152465 | 37053 | 0.35 |
| transform | 1 | 1 | 0 | 0 | 33 | 13 | 6 | 12 | 1158 | 246221 | 36917 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 299 | 152 | 47 | 94 | 14885 | 1885596 | 377626 | 2.04 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 324 | 227 | 65 | 126 | 21328 | 2852592 | 418250 | 4.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| For an owed file whose every step entry was applied or is test-only, refactor-owed.sh render prints `## Refactor owed`, one blank line, then the first `###` subsection, with no second blank line between them ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 126 | 36 | 72 | 11373 | 1579120 | 247043 | 2.00 | 265 | unknown | 0/5 | structural-owed |  |  | full |
| For an owed file with no step entries, no test-only transforms and no applied transforms, including one whose step headings all had their entries applied, refactor-owed.sh render prints nothing and exits 0 ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 40 | 78 | 13580 | 1732728 | 245005 | 2.06 | 264 | unknown | 1/5 | nothing-left |  |  | full |
| For an owed file with at least one step entry left, refactor-owed.sh render prints the same bytes as before this change ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 12 | 22 | 4955 | 517493 | 88883 | 0.75 | unknown | unknown | unknown | unknown |  |  | pin |
| refactor_owed.py reads `out = ` with a space before `=` ⟦diff-checked⟧ ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 61 | 23 | 46 | 5359 | 896846 | 183798 | 1.44 | 95 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| For an owed file whose every step entry was applied or is test-only, refactor-owed.sh render prints `## Refactor owed`, one blank line, then the first `###` subsection, with no second blank line between them ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 55 | 0.61 |
| For an owed file with no step entries, no test-only transforms and no applied transforms, including one whose step headings all had their entries applied, refactor-owed.sh render prints nothing and exits 0 ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 68 | 0.69 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 15 | 16 | 17 |
| fast | 15 | 16 | 16 | 16 | 16 | 16 | 15 | 16 |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 112 | 220 | 36213 | 4738188 | 795876 | 6.38 |
