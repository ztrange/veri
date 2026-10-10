### 📊 Metrics — issue 1448

Wall time for the issue: 1654 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1451.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 705 | 12489 | 31825 | 0.14 |
| red | 4 | 2 | 0 | 0 | 115 | 100 | 33 | 66 | 9946 | 1657750 | 188336 | 1.61 |
| green | 4 | 2 | 0 | 0 | 230 | 102 | 29 | 56 | 10761 | 1330152 | 175789 | 1.50 |
| refactor | 4 | 2 | 0 | 0 | 150 | 83 | 22 | 44 | 7870 | 991175 | 169037 | 1.34 |
| predicate | 1 | 0 | 0 | 0 | 11 | 8 | 3 | 6 | 778 | 103082 | 37403 | 0.34 |
| structural | 1 | 0 | 0 | 0 | 43 | 15 | 5 | 10 | 1302 | 205031 | 37960 | 0.37 |
| transform | 1 | 1 | 0 | 0 | 38 | 9 | 4 | 8 | 1057 | 154282 | 37727 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 236 | 85 | 34 | 68 | 10464 | 1383494 | 310752 | 1.49 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 358 | 237 | 63 | 124 | 21955 | 3070467 | 367325 | 3.99 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `build-develop-prompt.sh revise <phase> <spec> "<step>" '<test-cmd>' <reason-file> '<fast-cmd>'` exits 0 for each of expand, migrate, contract-a and contract-b, printing a revise prompt that names the phase being redone and carries the rejection reason verbatim, where it exited 2 with "unknown phase to revise" | 6 | 3 | 0 | 0 | 0 | 0 | 157 | 46 | 90 | 15919 | 2206054 | 270598 | 2.33 | 334 | unknown | 2/5 | structural-owed |  |  | full |
| The revise prompt for an interface phase states that phase's freeze rule, so the redone work passes the freeze check the conductor runs on it: test files are never modified when redoing expand, migrate or contract-b, and production files are never modified when redoing contract-a | 9 | 4 | 0 | 0 | 0 | 0 | 160 | 50 | 100 | 15795 | 2235418 | 375654 | 3.01 | 293 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `build-develop-prompt.sh revise <phase> <spec> "<step>" '<test-cmd>' <reason-file> '<fast-cmd>'` exits 0 for each of expand, migrate, contract-a and contract-b, printing a revise prompt that names the phase being redone and carries the rejection reason verbatim, where it exited 2 with "unknown phase to revise" | 1 | 2/5 | structural-owed | PASS | 0 | 98 | 0.74 |
| The revise prompt for an interface phase states that phase's freeze rule, so the redone work passes the freeze check the conductor runs on it: test files are never modified when redoing expand, migrate or contract-b, and production files are never modified when redoing contract-a | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.60 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 2 | 2 | 1 | 1 | 2 | 0 | 1 | 2 | 1 | 2 | 1 | 4 | 1 | 1 | 25 | 26 | 1 |
| fast | 24 | 24 | 24 | 25 | 25 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 192 | 32419 | 4453961 | 678077 | 5.48 |
