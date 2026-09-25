### 📊 Metrics — issue 388

Wall time for the issue: 4994 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/465.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 20 | 9 | 0 | 0 | 1029 | 885 | 172 | 310 | 72298 | 7558560 | 876663 | 12.87 |
| green | 18 | 9 | 0 | 0 | 4854 | 1005 | 241 | 444 | 85071 | 11333980 | 859761 | 14.96 |
| refactor | 19 | 9 | 0 | 0 | 3305 | 1084 | 205 | 400 | 91246 | 10707766 | 925248 | 15.49 |
| pin | 1 | 1 | 0 | 0 | 34 | 27 | 6 | 12 | 2719 | 253770 | 40395 | 0.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 487 | 6.06 |
| green | 0 | 0.00 | 1752 | 7.80 |
| refactor | 0 | 0.00 | 1332 | 7.67 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md has a `## Stopping` section that settles the leaves first — waiting with `wait-leaf.sh <name>` on every `.tdd/<name>.pid` still running `supervise.sh <name> ` before it touches the tree — and reaches only for `git reset --hard HEAD`, never `git checkout` | 6 | 3 | 0 | 0 | 0 | 0 | 423 | 85 | 162 | 34845 | 4324858 | 302182 | 6.06 | 802 | unknown | 1/5 | structural-owed |
| The Stopping section resets nothing and records `at=unsettled` when `rebase-merge`, `rebase-apply` or `MERGE_HEAD` is present in the worktree | 6 | 3 | 0 | 0 | 0 | 0 | 376 | 80 | 146 | 29074 | 3809126 | 287960 | 5.51 | unknown | unknown | 2/5 | nothing-structural |
| CLAUDE.md's *Testing idiom* suite count matches the suites on disk again, so `make test` is green at the tip after this run added `skill-stopping.test.sh` | 6 | 3 | 0 | 0 | 0 | 0 | 377 | 76 | 142 | 30768 | 3970574 | 312521 | 5.88 | 986 | unknown | 1/5 | structural-owed |
| The Stopping section runs `push-branch.sh` and, on its exit 1, records `push=rejected` with the sha its stderr names, launching no reconcile leaf and bailing not at all | 6 | 3 | 0 | 0 | 0 | 0 | 442 | 79 | 146 | 36493 | 3985559 | 296323 | 5.87 | unknown | unknown | 2/5 | structural-owed |
| `no-nested-suites.test.sh` is green again: `claude-md-counts.test.sh`'s new case no longer names another suite in a shape that guard reads as launching it | 6 | 3 | 0 | 0 | 0 | 0 | 262 | 60 | 104 | 21316 | 2524009 | 276899 | 4.56 | unknown | unknown | 0/5 | nothing-left |
| The Stopping section writes exactly one `event.sh stop mode=<mode> at=<at>` mark, with `at` one of `unplanned`, `planned`, `green`, `step-done` or `unsettled`, and names `classify-bail.sh` nowhere | 6 | 3 | 0 | 0 | 0 | 0 | 399 | 77 | 136 | 31568 | 3551107 | 301719 | 5.58 | unknown | unknown | 1/5 | nothing-structural |
| The Stopping section renders `metrics.sh <n>` into a `### ⏹️ Stopped — <mode>` comment and commits no metrics file | 7 | 3 | 0 | 0 | 0 | 0 | 155 | 39 | 78 | 14346 | 1732672 | 257815 | 2.70 | 1342 | unknown | 0/5 | nothing-left |
| The Stopping section ends the run with `stop-requested.sh --clear`, opening no PR, removing no worktree and deleting no `.tdd/conductor.pid` | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 48 | 94 | 17802 | 2185453 | 264132 | 2.91 | 1593 | unknown | 0/5 | nothing-left |
| SKILL.md's script reference list has an entry for `stop-requested.sh` saying what it prints and which exit codes it answers with, so the Stopping section's two calls read their contract where every other script's is read | 9 | 4 | 0 | 0 | 0 | 0 | 367 | 80 | 158 | 35122 | 3770718 | 402516 | 4.68 | 1697 | unknown | 3/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 54 | 53 | 54 | 61 | 0 | 0 | 62 | 245 | 62 | 62 | 61 | 1 | 0 | 0 | 43 | 44 | 13 | 46 | 0 | 0 | 0 | 66 | 272 | 113 | 121 | 0 | 1 | 0 | 1 | 274 | 0 | 0 | 60 | 111 | 16 | 1 | 0 | 0 | 0 | 85 | 1 | 0 | 0 | 1 | 0 | 0 | 9 | 73 | 0 | 138 | 0 | 0 | 0 | 85 | 0 | 0 | 0 | 85 | 0 | 3 | 0 | 0 | 1 | 90 | 0 |
| fast | 3 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 3 | 324 | 326 | 321 | 321 | 322 | 323 | 324 | 322 | 324 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 624 | 1166 | 251334 | 29854076 | 2702067 | 43.74 |
