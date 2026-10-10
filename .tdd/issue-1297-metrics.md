### 📊 Metrics — issue 1297

Wall time for the issue: 11566 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1400.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 1089 | 12193 | 41864 | 0.18 |
| red | 12 | 6 | 0 | 0 | 470 | 381 | 82 | 162 | 36637 | 4351666 | 620156 | 5.30 |
| green | 14 | 6 | 1 | 0 | 5870 | 317 | 105 | 194 | 29812 | 4921915 | 666090 | 5.31 |
| refactor | 12 | 6 | 0 | 0 | 1459 | 281 | 78 | 156 | 26160 | 4095690 | 578586 | 4.69 |
| diff | 2 | 1 | 0 | 0 | 495 | 36 | 13 | 26 | 3423 | 620463 | 87810 | 0.66 |
| predicate | 1 | 0 | 0 | 0 | 16 | 11 | 3 | 6 | 1000 | 119617 | 43783 | 0.39 |
| structural | 1 | 0 | 0 | 0 | 36 | 11 | 3 | 6 | 965 | 119793 | 43058 | 0.39 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 21 | 20 | 1 | 0 | 5041 | 313 | 104 | 202 | 32343 | 4660156 | 940886 | 4.55 |
| developer | claude-opus-5-5 | 22 | 0 | 0 | 0 | 3317 | 732 | 181 | 350 | 66743 | 9581181 | 1140461 | 12.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1943 | 0.91 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| SKILL.md says a resumed run — one whose worktree and ledger already exist — runs `rebase-onto-default.sh` before its preflight baseline, so the baseline runs on the rebased tip, and that a new branch's run does not rebase there ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 170 | 47 | 92 | 16849 | 2424331 | 301959 | 2.54 | 1656 | unknown | 1/5 | nothing-structural |  |  | full |
| SKILL.md says the resume rebase's exit 3 goes on unchanged, its exit 1 goes on from the old base and leaves the conflict to the Draft PR step, and its exit 2 bails as the Draft PR step's does (`no-verdict`) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 142 | 38 | 74 | 13312 | 1875524 | 288014 | 2.32 | 1195 | unknown | 1/5 | nothing-left |  |  | full |
| The Draft PR step's rebase text in SKILL.md is unchanged by this branch ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 13 | 26 | 3423 | 620463 | 87810 | 0.66 | 512 | n/a | n/a | n/a |  |  | full |
| SKILL.md says a resume rebase that moved the branch is published, once the baseline is green, with `push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, never a bare force ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 197 | 51 | 102 | 19625 | 2870879 | 309529 | 2.80 | 752 | unknown | 2/5 | structural-owed |  |  | full |
| SKILL.md says a red baseline on the resume-rebased tip resets to `<pre-rebase-sha>` before the run bails ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 133 | 38 | 70 | 12645 | 1752017 | 289078 | 2.29 | 703 | unknown | 1/5 | nothing-structural |  |  | full |
| SKILL.md says a resume rebase that moved the branch is marked in the run log as its own event carrying the pre-rebase and rebased shas, under a name distinct from anything the Draft PR step's rebase records ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 196 | 48 | 92 | 16166 | 2480352 | 306535 | 2.59 | 1585 | unknown | 1/5 | nothing-left |  |  | full |
| fix the full-suite failure: no-sigpipe-pipelines.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF (skill-preflight-launchable.test.sh:434 ends its pipeline in head -n 1) ⟦suite-repair⟧ ⟦criterion 3⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 144 | 44 | 84 | 14161 | 1963012 | 409148 | 3.08 | 2290 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md says a resumed run — one whose worktree and ledger already exist — runs `rebase-onto-default.sh` before its preflight baseline, so the baseline runs on the rebased tip, and that a new branch's run does not rebase there ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 531 | 0.80 |
| SKILL.md says the resume rebase's exit 3 goes on unchanged, its exit 1 goes on from the old base and leaves the conflict to the Draft PR step, and its exit 2 bails as the Draft PR step's does (`no-verdict`) ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 138 | 0.82 |
| SKILL.md says a resume rebase that moved the branch is published, once the baseline is green, with `push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, never a bare force ⟦criterion 2⟧ | 1 | 2/5 | structural-owed | PASS | 0 | 145 | 0.97 |
| SKILL.md says a red baseline on the resume-rebased tip resets to `<pre-rebase-sha>` before the run bails ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 120 | 0.76 |
| SKILL.md says a resume rebase that moved the branch is marked in the run log as its own event carrying the pre-rebase and rebased shas, under a name distinct from anything the Draft PR step's rebase records ⟦criterion 3⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 436 | 0.78 |
| fix the full-suite failure: no-sigpipe-pipelines.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF (skill-preflight-launchable.test.sh:434 ends its pipeline in head -n 1) ⟦suite-repair⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 89 | 0.56 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 259 | 309 | 0 | 1 | 256 | 1 | 0 | 33 | 1 | 2 | 2 | 0 | 2 | 3 | 2 | 164 | 1 | 1 | 0 | 1 | 0 | 0 | 7 | 1 | 0 | 43 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 20 | 7 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 4 | 1 | 0 | 0 | 13 | 1 | 1 | 1 | 243 | 1 | 1 | 1 | 1 | 267 | 0 | 1 | 1 | 1 | 254 | 319 | 0 | 1 | 10 | 0 | 9 | 10 | 1 | 11 | 1 | 19 |
| fast | 56 | 57 | 57 | 58 | 61 | 61 | 61 | 59 | 56 | 56 | 59 | 59 | 58 | 58 | 56 | 60 | 62 | 58 | 60 | 57 | 59 | 58 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 | 9 | 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 285 | 552 | 99086 | 14241337 | 2081347 | 16.93 |
