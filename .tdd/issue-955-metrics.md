### 📊 Metrics — issue 955

Wall time for the issue: 6523 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/983.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 2 | 4 | 1617 | 63046 | 42124 | 0.38 |
| red | 9 | 3 | 1 | 0 | 454 | 384 | 84 | 162 | 38699 | 4959194 | 460026 | 5.45 |
| green | 6 | 3 | 0 | 0 | 2241 | 285 | 73 | 142 | 28783 | 3969398 | 319164 | 3.92 |
| refactor | 6 | 3 | 0 | 0 | 2185 | 176 | 49 | 98 | 17385 | 2549953 | 295034 | 3.22 |
| pin | 1 | 1 | 0 | 0 | 33 | 26 | 6 | 12 | 2770 | 284252 | 48408 | 0.50 |
| predicate | 1 | 0 | 0 | 0 | 20 | 14 | 4 | 8 | 1251 | 171778 | 43612 | 0.41 |
| structural | 1 | 0 | 0 | 0 | 39 | 25 | 6 | 12 | 2241 | 288369 | 50152 | 0.50 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 12 | 11 | 1 | 0 | 2259 | 341 | 81 | 162 | 33900 | 3961952 | 515958 | 5.60 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 2734 | 585 | 143 | 276 | 58846 | 8324038 | 742562 | 8.78 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 168 | 1.89 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| SKILL.md runs the baseline fast-tier suite inside the issue's worktree, after `issue-worktree.sh` has cut the branch and the conductor has `cd`'d into it, not in the caller's checkout — so with the caller's checkout behind `origin/<default>` the baseline proves the commit the branch is cut from ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 289 | 68 | 134 | 29970 | 4015018 | 336983 | 4.10 | 1678 | unknown | 1/5 | structural-owed |  |  | full |
| SKILL.md says a red baseline in the worktree stops the run before the plan and before any cycle with the same preflight-class report a red baseline gave before, whatever state the caller's checkout is in ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 264 | 61 | 120 | 26466 | 3182183 | 357698 | 4.03 | 1653 | 1/2 | 2/5 | nothing-structural |  |  | full |
| SKILL.md takes the full-tier measurement in that same worktree, on the same commit as the fast-tier baseline, and sizes the hard timeout (`leaf-timeout.sh … --full`) only after that measurement ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 101 | 19 | 36 | 10330 | 985523 | 106182 | 1.25 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md says that on resume of an existing branch the baseline runs on that branch's head in its existing worktree, before any cycle of the resumed run starts ⟦criterion 4⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 256 | 74 | 144 | 24363 | 4040220 | 415533 | 4.62 | 1689 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| SKILL.md runs the baseline fast-tier suite inside the issue's worktree, after `issue-worktree.sh` has cut the branch and the conductor has `cd`'d into it, not in the caller's checkout — so with the caller's checkout behind `origin/<default>` the baseline proves the commit the branch is cut from ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 752 | 1.08 |
| SKILL.md says a red baseline in the worktree stops the run before the plan and before any cycle with the same preflight-class report a red baseline gave before, whatever state the caller's checkout is in ⟦criterion 2⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 678 | 0.98 |
| SKILL.md says that on resume of an existing branch the baseline runs on that branch's head in its existing worktree, before any cycle of the resumed run starts ⟦criterion 4⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 755 | 1.16 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 0 | 0 | 223 | 0 | 274 | 303 | 327 | 1 | 0 | 0 | 230 | 0 | 305 | 290 | 277 | 0 | 0 | 1 | 0 | 0 | 226 | 327 | 304 | 0 | 316 | 11 |
| fast | 44 | 43 | 49 | 47 | 48 | 46 | 45 | 45 | 45 | 51 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 224 | 438 | 92746 | 12285990 | 1258520 | 14.38 |
