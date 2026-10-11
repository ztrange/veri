### 📊 Metrics — issue 1354

Wall time for the issue: 3575 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1474.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 2 | 0 | 0 | 173 | 103 | 28 | 56 | 11968 | 1450127 | 258504 | 1.54 |
| green | 8 | 2 | 2 | 0 | 929 | 353 | 93 | 182 | 36059 | 5472554 | 371433 | 3.21 |
| refactor | 4 | 2 | 0 | 0 | 238 | 72 | 26 | 50 | 8207 | 1289020 | 193917 | 0.99 |
| predicate | 3 | 0 | 0 | 0 | 35 | 25 | 9 | 18 | 1940 | 358134 | 128955 | 0.57 |
| structural | 2 | 0 | 0 | 0 | 168 | 29 | 11 | 22 | 3204 | 542070 | 92979 | 0.46 |
| transform | 2 | 1 | 1 | 0 | 101 | 29 | 7 | 14 | 2235 | 296235 | 87989 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 435 | 163 | 59 | 114 | 18412 | 3024955 | 438868 | 2.24 |
| verifier | claude-sonnet-5-5 | 10 | 7 | 3 | 0 | 739 | 192 | 58 | 114 | 20011 | 2870474 | 400222 | 2.09 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 470 | 256 | 57 | 114 | 25190 | 3512711 | 294687 | 2.85 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 173 | 1.54 |
| green | 0 | 0.00 | 929 | 3.21 |
| refactor | 0 | 0.00 | 238 | 0.99 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 101 | 0.40 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| orchestrate gives its full answer — exit code, stdout, stderr, files and events — when starting solvable-issues.sh as a process is refused, by calling solvable_issues.solvable in-process (orchestrate.py:28) ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 153 | 53 | 100 | 17989 | 2778624 | 311856 | 1.71 | unknown | unknown | 1/5 | nothing-structural |  |  | full |
| parallel_conductors gives its full answer — exit code, stdout, stderr, files and events — when starting solvable-issues.sh as a process is refused, by calling solvable_issues.solvable in-process (parallel_conductors.py:200) ⟦added⟧ ⟦criterion 2⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 375 | 94 | 188 | 38245 | 5433077 | 511998 | 4.04 | unknown | red 1/2, green 2/2 | 0/5 | structural-owed |  |  | full |
| No test of orchestrate, parallel_conductors or status fakes solvable-issues.sh at the process boundary any longer, each such test rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 7 | 1 | 1 | 0 | 0 | 0 | 83 | 27 | 54 | 7379 | 1196439 | 309923 | 1.43 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| orchestrate gives its full answer — exit code, stdout, stderr, files and events — when starting solvable-issues.sh as a process is refused, by calling solvable_issues.solvable in-process (orchestrate.py:28) ⟦added⟧ ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 144 | 0.54 |
| parallel_conductors gives its full answer — exit code, stdout, stderr, files and events — when starting solvable-issues.sh as a process is refused, by calling solvable_issues.solvable in-process (parallel_conductors.py:200) ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 94 | 0.44 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 14 | 13 | 7 | 7 | 7 | 2 | 8 | 16 | 21 | 1 | 1 | 4 | 5 | 0 | 5 | 5 | 0 | 57 | 61 | 60 |
| fast | 53 | 54 | 54 | 54 | 54 | 60 | 55 | 56 | 55 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 174 | 342 | 63613 | 9408140 | 1133777 | 7.18 |
