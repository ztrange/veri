### 📊 Metrics — issue 412

Wall time for the issue: 3246 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/456.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 17 | 2 | 4 | 1688 | 56244 | 35866 | 0.33 |
| red | 11 | 4 | 0 | 0 | 543 | 471 | 97 | 190 | 43326 | 4746377 | 512248 | 5.91 |
| green | 8 | 4 | 0 | 0 | 1517 | 320 | 78 | 156 | 27281 | 3567898 | 334816 | 3.94 |
| refactor | 8 | 4 | 0 | 0 | 340 | 274 | 62 | 122 | 25818 | 2804445 | 336243 | 3.77 |
| pin | 3 | 3 | 0 | 0 | 117 | 97 | 16 | 32 | 8919 | 653735 | 120193 | 1.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| skills/solve-issue/ and skills/solve-issues/ are absent from the tree, and skill-identity.test.sh holds no case that reads a stub's frontmatter or requires a stub to exist ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 216 | 55 | 110 | 19435 | 2553599 | 251813 | 2.91 | 359 | unknown | 1/5 | structural-owed |
| skill-identity.test.sh's exempt no longer answers true for the two stub paths, and its old-home and old-command sweeps still fail a repository whose tracked file at one of those paths names the old home or invokes an old name ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 239 | 53 | 104 | 21929 | 2475951 | 265172 | 3.06 | 367 | unknown | 2/5 | structural-owed |
| a file under .tdd/ that names the old home as a path or invokes an old name as a command still passes both skill-identity sweeps ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 14 | 26 | 6484 | 616149 | 91903 | 0.99 | unknown | unknown | unknown | unknown |
| both skill-identity sweeps pass with docs/adr/0013-issue-branch-in-its-own-worktree.md line 18 naming ~/.claude/skills/solve-issue as a path, unedited ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 121 | 18 | 36 | 12754 | 893004 | 97867 | 1.22 | unknown | unknown | unknown | unknown |
| README.md's install step symlinks skills/tdd alone and no longer tells a new clone to symlink the two old names ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 262 | 57 | 112 | 22537 | 2724542 | 265244 | 3.12 | 684 | unknown | 2/5 | nothing-structural |
| CLAUDE.md's opening paragraph names skills/tdd/ as the product rather than skills/solve-issue/ ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 174 | 42 | 84 | 15500 | 1830823 | 243709 | 2.63 | 1139 | unknown | 0/5 | nothing-left |
| claude-md-counts.test.sh passes with CLAUDE.md's stated script and suite counts unchanged once the stubs are gone ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 14 | 28 | 6705 | 678387 | 87792 | 0.97 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 286 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 56 | 1 | 1 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 255 | 504 | 107032 | 11828699 | 1339366 | 15.22 |
