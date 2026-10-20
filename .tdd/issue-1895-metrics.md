### 📊 Metrics — issue 1895

Wall time for the issue: 3256 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 6 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 998 | 17463 | 12931 | 0.04 |
| red | 12 | 5 | 2 | 0 | 387 | 221 | 65 | 126 | 22646 | 1959319 | 236317 | 1.12 |
| green | 15 | 3 | 3 | 0 | 2149 | 400 | 109 | 212 | 37927 | 3417148 | 266957 | 1.83 |
| refactor | 6 | 3 | 0 | 0 | 112 | 37 | 18 | 34 | 3160 | 430599 | 78145 | 0.27 |
| red-supersede | 1 | 0 | 0 | 0 | 63 | 57 | 11 | 22 | 7853 | 461801 | 40977 | 0.23 |
| exhausted | 1 | 0 | 0 | 0 | 111 | 15 | 4 | 8 | 1502 | 108997 | 15651 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 12 | 5 | 0 | 774 | 202 | 69 | 134 | 19288 | 1844230 | 233523 | 0.96 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 427 | 203 | 58 | 110 | 22163 | 1851924 | 186489 | 0.87 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 1632 | 333 | 81 | 160 | 32635 | 2699173 | 230966 | 1.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 154 | 0.62 |
| green | 474 | 0.65 | 1531 | 1.08 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 63 | 0.23 |
| exhausted | 0 | 0.00 | 111 | 0.13 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise.py run with its working directory a subdirectory of the repo creates and writes its run state (`.tdd/<name>.log`, `.rc`, `.exit`, `.pid`) under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 102 | 33 | 62 | 8620 | 939935 | 103124 | 0.44 | 535 | unknown | 0/5 | nothing-left |  |  | full |
| verify.py run with its working directory a subdirectory of the repo writes its verifier prompt and run state under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 131 | 49 | 96 | 13599 | 1409867 | 130634 | 0.72 | 478 | 2/2 | 0/5 | structural-owed |  |  | full |
| pin_fast_tier.py run with its working directory a subdirectory of the repo writes `verify-pin.reason` under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 75 | 29 | 52 | 7214 | 735483 | 89150 | 0.37 | 158 | unknown | 0/5 | nothing-left |  |  | full |
| parallel_conductors.py run with its working directory a subdirectory of the repo writes `parallel.exit` and its conductor logs under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 13 | 2 | 3 | 0 | 0 | 0 | 422 | 96 | 192 | 43655 | 3292579 | 315139 | 2.06 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.py run with its working directory a subdirectory of the repo creates and writes its run state (`.tdd/<name>.log`, `.rc`, `.exit`, `.pid`) under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.09 |
| verify.py run with its working directory a subdirectory of the repo writes its verifier prompt and run state under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 40 | 0.10 |
| pin_fast_tier.py run with its working directory a subdirectory of the repo writes `verify-pin.reason` under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 22 | 0.08 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 30 | 32 | 32 | 74 | 30 | 14 | 15 | 15 | 13 | 13 | 14 | 13 | 14 | 1 | 1 | 0 | 0 | 0 | 1 | 3 | 3 | 4 | 5 | 3 | 3 | 94 |
| fast | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 5 | 6 | 6 | 6 | 6 | 6 | 0 | 7 |  |  |  |  |  |  |  |  |  |  |  |
| target | 32 | 14 | 0 | 13 | 1 | 94 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 208 | 404 | 74086 | 6395327 | 650978 | 3.62 |
