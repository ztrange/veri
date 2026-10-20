### 📊 Metrics — issue 1911

Wall time for the issue: 3138 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1923.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.48 over 64 turns, in 1 sessions.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84836 |
| 2 | $0.02 | 85430 |
| 3 | $0.03 | 86555 |
| 4 | $0.03 | 88457 |
| 5 | $0.02 | 88773 |
| 6 | $0.02 | 89246 |
| 7 | $0.02 | 89598 |
| 8 | $0.02 | 89915 |
| 9 | $0.02 | 90500 |
| 10 | $0.02 | 91054 |
| 11 | $0.04 | 93638 |
| 12 | $0.05 | 98014 |
| 13 | $0.04 | 101126 |
| 14 | $0.04 | 103019 |
| 15 | $0.02 | 103348 |
| 16 | $0.03 | 104258 |
| 17 | $0.03 | 105333 |
| 18 | $0.03 | 106680 |
| 19 | $0.03 | 107705 |
| 20 | $0.03 | 108534 |
| 21 | $0.03 | 109302 |
| 22 | $0.03 | 110179 |
| 23 | $0.03 | 111403 |
| 24 | $0.03 | 112053 |
| 25 | $0.04 | 113728 |
| 26 | $0.03 | 114425 |
| 27 | $0.03 | 114988 |
| 28 | $0.03 | 115719 |
| 29 | $0.02 | 115914 |
| 30 | $0.03 | 117220 |
| 31 | $0.03 | 118417 |
| 32 | $0.04 | 120864 |
| 33 | $0.03 | 121579 |
| 34 | $0.03 | 121833 |
| 35 | $0.03 | 122559 |
| 36 | $0.03 | 123086 |
| 37 | $0.03 | 123888 |
| 38 | $0.04 | 125468 |
| 39 | $0.03 | 126209 |
| 40 | $0.03 | 126874 |
| 41 | $0.03 | 127111 |
| 42 | $0.03 | 127732 |
| 43 | $0.03 | 128496 |
| 44 | $0.03 | 129460 |
| 45 | $0.03 | 129994 |
| 46 | $0.03 | 130377 |
| 47 | $0.04 | 131703 |
| 48 | $0.03 | 132079 |
| 49 | $0.03 | 132714 |
| 50 | $0.03 | 132937 |
| 51 | $0.03 | 133600 |
| 52 | $0.03 | 133985 |
| 53 | $0.04 | 135599 |
| 54 | $0.03 | 135942 |
| 55 | $0.03 | 136740 |
| 56 | $0.03 | 136985 |
| 57 | $0.03 | 137360 |
| 58 | $0.03 | 137582 |
| 59 | $0.03 | 137830 |
| 60 | $0.03 | 138050 |
| 61 | $0.03 | 138432 |
| 62 | $0.04 | 139601 |
| 63 | $0.03 | 139833 |
| 64 | $0.03 | 140178 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 3 | 6 | 1228 | 77800 | 15367 | 0.06 |
| red | 10 | 4 | 0 | 0 | 403 | 227 | 49 | 96 | 16361 | 1432281 | 179871 | 0.76 |
| green | 8 | 4 | 0 | 0 | 816 | 151 | 40 | 78 | 11591 | 1101821 | 121439 | 0.53 |
| refactor | 8 | 4 | 0 | 0 | 234 | 68 | 28 | 54 | 4948 | 714223 | 103652 | 0.38 |
| pin | 2 | 2 | 0 | 0 | 46 | 33 | 8 | 16 | 1997 | 211316 | 26879 | 0.11 |
| predicate | 1 | 0 | 0 | 0 | 15 | 12 | 4 | 8 | 720 | 103049 | 12621 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 15 | 0 | 0 | 1013 | 221 | 59 | 116 | 15008 | 1544751 | 207116 | 0.82 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 518 | 284 | 73 | 142 | 21837 | 2095739 | 252713 | 1.06 |

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
| prose-owed.sh, given a repo-root REQUIREMENTS.md whose unit's table repeats an ID, exits 2 and its stderr names that list's path and the duplicate-ID defect, never exit 0 — a heading with no table at all stays unprinted with exit 0, as today (small unit-tier case, run in-process with run_cli) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 83 | 23 | 44 | 6332 | 594883 | 87192 | 0.34 | 359 | unknown | 0/5 | nothing-structural |  |  | full |
| prose-owed.sh, given a requirements table whose header lacks a column, exits 2 and its stderr names the list's path and the header defect (small unit-tier case, run in-process with run_cli) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 10 | 20 | 3098 | 286802 | 31526 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| prose-owed.sh reads a nested unit's signature from skills/<skill>/GRADED: a unit at skills/demo/prompts/x.md whose current signature is recorded in skills/demo/GRADED is not printed and the exit is 0 (small unit-tier case, run in-process with run_cli) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 27 | 52 | 6729 | 719818 | 85901 | 0.35 | 428 | unknown | 0/5 | nothing-structural |  |  | full |
| A grade-prose.sh PASS on a nested unit skills/demo/prompts/x.md records its signature line in skills/demo/GRADED and writes no skills/demo/prompts/GRADED (small unit-tier case, run in-process, the grader leaf launch replaced by an in-process fake) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 9 | 18 | 3534 | 283891 | 42714 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| prose-owed.sh reads a REQUIREMENTS.md kept beside a unit: a unit listed only in skills/demo/REQUIREMENTS.md (its heading the unit's repo-relative path, as the repo-root list heads it), with no GRADED line, is printed and the exit is 1, with no repo-root REQUIREMENTS.md present (small unit-tier case, run in-process with run_cli) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 100 | 24 | 46 | 6181 | 633057 | 86080 | 0.34 | 319 | unknown | 0/5 | nothing-structural |  |  | full |
| grade-prose.sh --owed grades a unit listed only in the skills/demo/REQUIREMENTS.md beside it, with no current signature: it launches the grader for that unit with that list's requirements (small unit-tier case, run in-process, the grader leaf launch replaced by an in-process fake) ⟦criterion 3⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 127 | 36 | 72 | 9743 | 1044239 | 111049 | 0.48 | 532 | unknown | 1/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| prose-owed.sh, given a repo-root REQUIREMENTS.md whose unit's table repeats an ID, exits 2 and its stderr names that list's path and the duplicate-ID defect, never exit 0 — a heading with no table at all stays unprinted with exit 0, as today (small unit-tier case, run in-process with run_cli) ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 42 | 0.09 |
| prose-owed.sh reads a nested unit's signature from skills/<skill>/GRADED: a unit at skills/demo/prompts/x.md whose current signature is recorded in skills/demo/GRADED is not printed and the exit is 0 (small unit-tier case, run in-process with run_cli) ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 38 | 0.08 |
| prose-owed.sh reads a REQUIREMENTS.md kept beside a unit: a unit listed only in skills/demo/REQUIREMENTS.md (its heading the unit's repo-relative path, as the repo-root list heads it), with no GRADED line, is printed and the exit is 1, with no repo-root REQUIREMENTS.md present (small unit-tier case, run in-process with run_cli) ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 39 | 0.08 |
| grade-prose.sh --owed grades a unit listed only in the skills/demo/REQUIREMENTS.md beside it, with no current signature: it launches the grader for that unit with that list's requirements (small unit-tier case, run in-process, the grader leaf launch replaced by an in-process fake) ⟦criterion 3⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 115 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 0 | 84 | 2 | 2 | 2 | 2 | 2 | 0 | 69 | 2 | 3 | 2 | 2 | 1 | 70 | 2 | 1 | 2 | 2 | 67 | 67 | 2 |
| fast | 19 | 17 | 19 | 20 | 20 | 16 | 14 | 15 | 18 | 16 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 132 | 258 | 36845 | 3640490 | 459829 | 1.88 |
