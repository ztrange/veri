### 📊 Metrics — issue 1895

Wall time for the issue: 1255 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 6 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 998 | 17463 | 12931 | 0.04 |
| red | 16 | 7 | 2 | 0 | 517 | 293 | 87 | 170 | 30810 | 2664376 | 319847 | 1.49 |
| green | 19 | 5 | 3 | 0 | 2412 | 458 | 135 | 262 | 43948 | 4158004 | 329503 | 2.12 |
| refactor | 10 | 5 | 0 | 0 | 207 | 63 | 31 | 60 | 5563 | 774982 | 130927 | 0.46 |
| red-supersede | 1 | 0 | 0 | 0 | 63 | 57 | 11 | 22 | 7853 | 461801 | 40977 | 0.23 |
| exhausted | 2 | 0 | 0 | 0 | 463 | 29 | 7 | 14 | 2674 | 170650 | 42370 | 0.30 |
| diff | 6 | 0 | 3 | 0 | 127 | 82 | 23 | 44 | 8571 | 604307 | 56267 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 26 | 18 | 8 | 0 | 1027 | 292 | 99 | 194 | 28487 | 2649671 | 331416 | 1.38 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 1941 | 521 | 149 | 290 | 55159 | 4910637 | 441083 | 2.43 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 832 | 177 | 47 | 90 | 16771 | 1291275 | 160323 | 1.24 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 408 | 1.62 | 0 | 0.00 |
| green | 1906 | 1.57 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 352 | 0.17 |
| diff | 0 | 0.00 | 127 | 0.42 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise.py run with its working directory a subdirectory of the repo creates and writes its run state (`.tdd/<name>.log`, `.rc`, `.exit`, `.pid`) under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 102 | 33 | 62 | 8620 | 939935 | 103124 | 0.44 | 535 | unknown | 0/5 | nothing-left |  |  | full |
| verify.py run with its working directory a subdirectory of the repo writes its verifier prompt and run state under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 131 | 49 | 96 | 13599 | 1409867 | 130634 | 0.72 | 478 | 2/2 | 0/5 | structural-owed |  |  | full |
| pin_fast_tier.py run with its working directory a subdirectory of the repo writes `verify-pin.reason` under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 75 | 29 | 52 | 7214 | 735483 | 89150 | 0.37 | 158 | unknown | 0/5 | nothing-left |  |  | full |
| parallel_conductors.py run with its working directory a subdirectory of the repo writes `parallel.exit` and its conductor logs under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 19 | 5 | 3 | 0 | 0 | 0 | 496 | 123 | 246 | 51897 | 4087207 | 413064 | 2.46 | 222 | red 1/2, green 2/2 | 0/5 | nothing-left |  |  | full |
| run_conductor.py run with its working directory a subdirectory of the repo creates `.tdd/` and its seeded `.tdd/.gitignore` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 82 | 34 | 66 | 8346 | 995668 | 100933 | 0.44 | 436 | unknown | 1/5 | nothing-structural |  |  | full |
| The skills-are-skills audit in test_skills_are_skills.py does not report an empty `.tdd/` directly under skills/, nor a directory under skills/ holding only an empty `.tdd/`, as a skill missing its SKILL.md, while a real skill directory without SKILL.md still is reported; cases over a tmp_path skills tree pin both halves; test-only, no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 7 | 0 | 3 | 0 | 0 | 0 | 96 | 26 | 50 | 9743 | 665960 | 82986 | 0.58 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.py run with its working directory a subdirectory of the repo creates and writes its run state (`.tdd/<name>.log`, `.rc`, `.exit`, `.pid`) under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.09 |
| verify.py run with its working directory a subdirectory of the repo writes its verifier prompt and run state under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 40 | 0.10 |
| pin_fast_tier.py run with its working directory a subdirectory of the repo writes `verify-pin.reason` under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 22 | 0.08 |
| parallel_conductors.py run with its working directory a subdirectory of the repo writes `parallel.exit` and its conductor logs under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 24 | 0.08 |
| run_conductor.py run with its working directory a subdirectory of the repo creates `.tdd/` and its seeded `.tdd/.gitignore` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 71 | 0.11 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 30 | 32 | 32 | 74 | 30 | 14 | 15 | 15 | 13 | 13 | 14 | 13 | 14 | 1 | 1 | 0 | 0 | 0 | 1 | 3 | 3 | 4 | 5 | 3 | 3 | 94 | 3 | 3 | 3 | 4 | 4 | 22 | 22 | 21 | 22 | 22 | 22 | 1 | 0 | 0 | 1 |
| fast | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 5 | 6 | 6 | 6 | 6 | 6 | 0 | 7 | 6 | 7 | 6 | 7 | 7 | 6 | 6 | 6 | 7 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 32 | 14 | 0 | 13 | 1 | 94 | 3 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 295 | 574 | 100417 | 8851583 | 932822 | 5.05 |
