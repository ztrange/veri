### 📊 Metrics — issue 197

Wall time for the issue: 8873 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 12 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/445.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 2 | 0 | 0 | 61 | 51 | 6 | 12 | 4079 | 215436 | 76908 | 0.98 |
| red | 23 | 10 | 0 | 0 | 1571 | 1176 | 212 | 398 | 106730 | 10609930 | 1175778 | 14.49 |
| green | 34 | 9 | 8 | 0 | 5944 | 1393 | 291 | 568 | 126281 | 13740205 | 1442223 | 17.87 |
| refactor | 18 | 9 | 0 | 0 | 879 | 510 | 122 | 244 | 50970 | 5582830 | 780159 | 8.38 |
| pin | 3 | 3 | 0 | 0 | 179 | 63 | 17 | 34 | 5994 | 715696 | 119420 | 1.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 7868 | 26.46 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A branch on origin for which no PR has ever been opened is reported, naming the branch, its tip, its commit count ahead of the default branch, and the number and state of the issue its tdd slug name refers to | 14 | 4 | 3 | 0 | 0 | 0 | 1015 | 160 | 300 | 85702 | 8292821 | 683982 | 10.73 | 1625 | 2/2 | 0/5 | nothing-left |
| A branch on origin whose PR is still open is left out of the report, since invariant 2 is a branch with no PR at all | 8 | 3 | 1 | 0 | 0 | 0 | 203 | 55 | 108 | 19706 | 2396546 | 332544 | 3.53 | 632 | 1/2 | 0/5 | nothing-left |
| A branch on origin named tdd/<n>-<slug> whose issue <n> is not among the repository's issues is still reported with its tip and commits ahead, its issue state named as unknown, and the script does not die with a traceback after partial output | 6 | 3 | 0 | 0 | 0 | 0 | 213 | 48 | 96 | 20572 | 2283582 | 264766 | 2.99 | 364 | unknown | 3/5 | nothing-structural |
| A local branch absent from origin is reported, naming the branch, its tip, how many commits it holds that origin does not, and the worktree holding it when there is one | 10 | 3 | 2 | 0 | 0 | 0 | 381 | 71 | 138 | 34523 | 3284890 | 419440 | 4.70 | 1597 | 2/2 | 2/5 | structural-owed |
| A branch whose PR is merged or closed is left out of the report, and so is the default branch | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 40 | 80 | 15634 | 1771869 | 264891 | 2.79 | 347 | unknown | 0/5 | nothing-left |
| A local branch absent from origin whose PR was merged or closed (its origin branch deleted after the merge) is not reported as an invariant-1 finding | 8 | 3 | 1 | 0 | 0 | 0 | 225 | 55 | 108 | 22093 | 2439244 | 343988 | 3.68 | 812 | 1/2 | 1/5 | nothing-structural |
| The script exits 0 when it printed a finding and exits 3 with empty stdout when there is nothing to report | 8 | 3 | 1 | 0 | 0 | 0 | 255 | 59 | 118 | 23467 | 2767399 | 351577 | 3.84 | 1539 | 1/2 | 2/5 | nothing-structural |
| The script exits 2 with a diagnostic on stderr and empty stdout when the remote is unreachable or gh cannot be read | 6 | 3 | 0 | 0 | 0 | 0 | 204 | 47 | 92 | 20304 | 2213626 | 272057 | 3.03 | 481 | unknown | 1/5 | structural-owed |
| Every finding names the invariant it breaks, so a reader can tell a branch with no PR from a branch that never reached origin | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 18 | 34 | 7374 | 889898 | 97025 | 1.10 | unknown | unknown | unknown | unknown |
| The gh issue and pull request documents are read as JSON parsed with python3, under a VERI_GH_JSON fixture directory override that lets the suite drive the script with no network | 2 | 1 | 0 | 0 | 0 | 0 | 82 | 17 | 32 | 8085 | 852425 | 107045 | 1.19 | unknown | unknown | unknown | unknown |
| The script writes to no ref: it creates, moves and deletes nothing, and its suite proves the refs are byte-identical after a run | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 17 | 32 | 8857 | 883358 | 103339 | 1.18 | unknown | unknown | unknown | unknown |
| CLAUDE.md counts the new script and its suite, and the prose around those counts still describes the scripts truthfully | 6 | 3 | 0 | 0 | 0 | 0 | 239 | 55 | 106 | 23658 | 2573003 | 276926 | 3.20 | 520 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 1 | 10 | 3 | 0 | 66 | 0 | 1 | 1 | 0 | 59 | 0 | 60 | 1 | 101 | 0 | 65 | 0 | 60 | 0 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 11 | 5 | 14 | 7 | 7 | 7 | 0 | 8 | 8 | 8 | 8 | 8 | 7 | 9 | 9 | 9 | 9 | 9 | 0 | 10 | 9 | 10 | 10 | 12 | 12 | 11 | 0 | 79 | 12 | 12 | 12 | 14 | 15 | 15 | 22 | 15 | 0 | 14 | 16 | 16 | 19 | 1 | 1 | 70 | 0 | 100 | 1 | 0 | 0 |
| fast | 2 | 3 | 2 | 3 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 2 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 3 | 2 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 1 | 1 | 2 | 2 | 3 | 4 | 6 | 6 | 7 | 9 | 9 | 10 | 11 | 12 | 14 | 16 | 15 | 17 | 15 | 19 | 19 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 273 | 279 | 266 | 272 | 280 | 281 | 286 | 299 | 290 | 292 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 648 | 1256 | 294054 | 30864097 | 3594488 | 42.93 |
