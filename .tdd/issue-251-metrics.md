### 📊 Metrics — issue 251

Wall time for the issue: 1566 s, from the first event of the log to the mark that ended the run.
Steps done: 2 of 7 planned.
Outcome: the run bailed — no-verdict, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 2 | 0 | 0 | 691 | 223 | 40 | 76 | 19512 | 1782861 | 207532 | 2.57 |
| green | 4 | 1 | 0 | 0 | 1842 | 185 | 24 | 48 | 5355 | 1142088 | 110229 | 1.79 |
| refactor | 4 | 1 | 0 | 0 | 781 | 190 | 38 | 76 | 15579 | 1891767 | 156468 | 1.81 |
| pin | 1 | 1 | 0 | 0 | 93 | 41 | 12 | 24 | 3098 | 657439 | 42670 | 0.34 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 154 | 0.91 |
| green | 0 | 0.00 | 608 | 0.71 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A run launched by `run-conductor.sh` while the skill's clone is behind `origin/<default>` executes the skill at `origin/<default>`'s tip: a script changed only on the remote is the version in the base directory the conductor is handed | 8 | 3 | 0 | 0 | 0 | 420 | 60 | 120 | 25946 | 2942160 | 282544 | 3.82 | 3022 | unknown | 1/5 | nothing-left |
| Launching a run leaves the skill clone's `HEAD`, branch and working tree unchanged — no pull, no checkout | 2 | 1 | 0 | 0 | 0 | 84 | 21 | 40 | 7302 | 1010716 | 87054 | 1.06 | unknown | unknown | unknown | unknown |
| A failed fetch of `origin` exits 2 before any conductor is launched, with a stderr diagnostic naming the fetch | 4 | 1 | 0 | 0 | 0 | 135 | 33 | 64 | 10296 | 1521279 | 147301 | 1.62 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 114 | 224 | 43544 | 5474155 | 516899 | 6.51 |
