### 📊 Metrics — issue 237

Wall time for the issue: unknown s, from the first event of the log to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 11 | 5 | 0 | 0 | 1066 | 511 | 90 | 168 | 46285 | 4102385 | 491231 | 5.88 |
| green | 10 | 5 | 0 | 0 | 4501 | 395 | 89 | 160 | 27475 | 3971118 | 407311 | 4.30 |
| refactor | 12 | 5 | 1 | 0 | 4475 | 700 | 125 | 250 | 53024 | 6435737 | 471163 | 6.51 |
| pin | 1 | 1 | 0 | 0 | 108 | 79 | 13 | 26 | 5935 | 764546 | 45716 | 0.40 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 2377 | 2.16 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A conductor launched by `run-conductor.sh` (stub `CLAUDE_BIN`) receives a base directory that is not the primary clone's `skills/tdd`, and whose files are the skill commit recorded for the run | 8 | 3 | 1 | 0 | 0 | 501 | 84 | 166 | 42820 | 4186523 | 328310 | 4.12 | 4264 | 1/2 | unknown | unknown |
| Changing or deleting a script in the primary clone after launch does not change what the run's leaves execute: `supervise.sh`, `run-leaf.sh` and the prompt templates a leaf is built from are read from the snapshot | 2 | 1 | 0 | 0 | 0 | 142 | 24 | 46 | 12831 | 1271411 | 98406 | 1.35 | unknown | unknown | unknown | unknown |
| A resume of that run uses the recorded commit, re-materialising the snapshot if it was removed | 6 | 3 | 0 | 0 | 0 | 298 | 59 | 110 | 23507 | 2827027 | 274974 | 3.19 | 1775 | unknown | unknown | unknown |
| A resume on which the operator explicitly asks for the new skill pins the current commit instead, and records that re-pin as an event in the run's event log | 6 | 3 | 0 | 0 | 0 | 265 | 59 | 110 | 19699 | 2837312 | 271581 | 3.08 | 1536 | unknown | unknown | unknown |
| With no resolvable commit the run proceeds unpinned and a warning is printed on stderr | 6 | 3 | 0 | 0 | 0 | 221 | 48 | 92 | 16973 | 2213968 | 239791 | 2.52 | 1591 | unknown | unknown | unknown |
| The snapshot is ignored run state: `git status --porcelain` in the worktree and in the caller's checkout stays empty | 6 | 3 | 0 | 0 | 0 | 258 | 43 | 80 | 16889 | 1937545 | 202359 | 2.83 | 1599 | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 317 | 604 | 132719 | 15273786 | 1415421 | 17.09 |
