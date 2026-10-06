### 📊 Metrics — issue 992

Wall time for the issue: 6376 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1027.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 12 | 3 | 6 | 1024 | 116421 | 42639 | 0.38 |
| red | 14 | 7 | 0 | 0 | 486 | 369 | 95 | 184 | 32069 | 4495348 | 661840 | 6.84 |
| green | 17 | 6 | 2 | 0 | 2735 | 589 | 150 | 296 | 52897 | 7733410 | 738810 | 8.52 |
| refactor | 12 | 6 | 0 | 0 | 588 | 250 | 67 | 134 | 22116 | 3124930 | 543862 | 5.42 |
| predicate | 1 | 0 | 0 | 0 | 17 | 11 | 3 | 6 | 1056 | 117367 | 43348 | 0.39 |
| structural | 1 | 0 | 0 | 0 | 87 | 35 | 7 | 14 | 3506 | 350359 | 47483 | 0.52 |
| transform | 1 | 1 | 0 | 0 | 81 | 30 | 6 | 12 | 2568 | 270281 | 42824 | 0.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 23 | 21 | 2 | 0 | 2200 | 622 | 152 | 304 | 52523 | 7310108 | 1002880 | 10.54 |
| developer | claude-opus-5-5 | 24 | 0 | 0 | 0 | 1811 | 674 | 179 | 348 | 62713 | 8898008 | 1117926 | 11.98 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1938 | 4.56 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `refactor-owed.sh append` over a report with one `CANDIDATES: out-of-scope | …` line and no structural line records it in the owed file, and `refactor-owed.sh list` over that file then exits 3 and prints nothing ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 145 | 37 | 72 | 12625 | 1708808 | 268308 | 2.74 | 397 | unknown | 1/5 | nothing-structural |  |  | full |
| `refactor-owed.sh render` over an owed file holding an out-of-scope candidate prints the transform under its own out-of-scope heading, not under a step heading of `## Refactor owed` and not under `### Test-only` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 140 | 38 | 74 | 13012 | 1783750 | 276883 | 2.83 | 368 | unknown | 1/5 | nothing-structural |  |  | full |
| `refactor-overflow.sh <n> <owed-file> 0` over an owed file holding only an out-of-scope candidate files one `Refactor owed by #<n>` issue whose body lists that transform (gh faked) ⟦criterion 3⟧ | 11 | 4 | 1 | 0 | 0 | 0 | 367 | 86 | 168 | 30779 | 4263969 | 448236 | 5.05 | 819 | red 1/2, green 1/2 | 0/5 | structural-owed |  |  | full |
| `refactor-triage.sh` over a report whose only candidate is `CANDIDATES: out-of-scope | …` exits 3 with nothing on stdout, as it does for a cosmetic-only report ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 119 | 36 | 72 | 11240 | 1686826 | 268222 | 2.71 | 339 | unknown | 0/5 | nothing-structural |  |  | full |
| `prompts/develop-refactor.md` defines the out-of-scope class beside structural, cosmetic and test-only, tells the leaf to use it instead of `structural` for a transform outside the issue's bounds or ruled out by its spec, and its `CANDIDATES:` grammar line names it, pinned as text ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 152 | 49 | 98 | 14478 | 2501349 | 278167 | 3.02 | 567 | unknown | 0/5 | nothing-structural |  |  | full |
| SKILL.md's structural pass hands an owed file's out-of-scope candidates to `refactor-overflow.sh` even when the pass skipped nothing or ran no candidate (`list` exit 3), so they are still filed as `Refactor owed by #<n>`, pinned as text | 11 | 4 | 1 | 0 | 0 | 0 | 361 | 82 | 162 | 32078 | 4146993 | 538351 | 5.78 | 1734 | 1/2 | 0/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `refactor-owed.sh append` over a report with one `CANDIDATES: out-of-scope | …` line and no structural line records it in the owed file, and `refactor-owed.sh list` over that file then exits 3 and prints nothing ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 114 | 0.93 |
| `refactor-owed.sh render` over an owed file holding an out-of-scope candidate prints the transform under its own out-of-scope heading, not under a step heading of `## Refactor owed` and not under `### Test-only` ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 102 | 0.97 |
| `refactor-overflow.sh <n> <owed-file> 0` over an owed file holding only an out-of-scope candidate files one `Refactor owed by #<n>` issue whose body lists that transform (gh faked) ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 96 | 0.94 |
| `refactor-triage.sh` over a report whose only candidate is `CANDIDATES: out-of-scope | …` exits 3 with nothing on stdout, as it does for a cosmetic-only report ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 88 | 0.87 |
| `prompts/develop-refactor.md` defines the out-of-scope class beside structural, cosmetic and test-only, tells the leaf to use it instead of `structural` for a transform outside the issue's bounds or ruled out by its spec, and its `CANDIDATES:` grammar line names it, pinned as text ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 91 | 0.84 |
| SKILL.md's structural pass hands an owed file's out-of-scope candidates to `refactor-overflow.sh` even when the pass skipped nothing or ran no candidate (`list` exit 3), so they are still filed as `Refactor owed by #<n>`, pinned as text | 1 | 0/5 | nothing-structural | PASS | 0 | 97 | 0.87 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 3 | 4 | 4 | 4 | 4 | 4 | 9 | 1 | 3 | 6 | 1 | 2 | 1 | 1 | 9 | 1 | 7 | 8 | 0 | 0 | 0 | 11 | 11 | 11 | 0 | 1 | 207 | 0 | 506 | 206 | 208 | 0 | 40 | 6 | 46 |
| fast | 40 | 40 | 40 | 40 | 40 | 40 | 39 | 40 | 40 | 40 | 41 | 39 | 40 | 39 | 40 | 40 | 40 | 41 | 39 | 40 | 40 | 40 | 40 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 3 | 3 | 1 | 7 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 331 | 652 | 115236 | 16208116 | 2120806 | 22.52 |
