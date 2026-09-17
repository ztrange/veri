### 📊 Metrics — issue 251

Wall time for the issue: 8568 s, from the first event of the log to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/257.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 13 | 5 | 0 | 0 | 1224 | 455 | 92 | 172 | 42326 | 3823595 | 539734 | 7.51 |
| green | 12 | 4 | 1 | 0 | 8097 | 409 | 87 | 166 | 24663 | 3440752 | 385856 | 6.20 |
| refactor | 10 | 4 | 0 | 0 | 2082 | 291 | 66 | 130 | 24376 | 2845126 | 352061 | 4.48 |
| pin | 3 | 3 | 0 | 0 | 261 | 70 | 21 | 42 | 5821 | 956605 | 104306 | 1.18 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3668 | 2.35 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A run launched by `run-conductor.sh` while the skill's clone is behind `origin/<default>` executes the skill at `origin/<default>`'s tip: a script changed only on the remote is the version in the base directory the conductor is handed | 8 | 3 | 0 | 0 | 0 | 420 | 60 | 120 | 25946 | 2942160 | 282544 | 3.82 | 3022 | unknown | 1/5 | nothing-left |
| Launching a run leaves the skill clone's `HEAD`, branch and working tree unchanged — no pull, no checkout | 2 | 1 | 0 | 0 | 0 | 84 | 21 | 40 | 7302 | 1010716 | 87054 | 1.06 | unknown | unknown | unknown | unknown |
| A failed fetch of `origin` exits 2 before any conductor is launched, with a stderr diagnostic naming the fetch | 10 | 4 | 0 | 0 | 0 | 239 | 64 | 124 | 19107 | 2629572 | 355451 | 4.49 | 2288 | unknown | 1/5 | nothing-left |
| The pinned skill commit reaches the run: every event a launched run writes carries it as `skill_commit`, and the conductor's prompt names it for the plan comment, equal to `origin/<default>`'s commit at launch | 6 | 3 | 0 | 0 | 0 | 147 | 39 | 74 | 13868 | 1545819 | 223586 | 3.37 | 1587 | unknown | 0/5 | nothing-left |
| A resumed run keeps its recorded pin even when `origin/<default>` has moved since the first launch | 2 | 1 | 0 | 0 | 0 | 55 | 16 | 28 | 5404 | 584898 | 80803 | 1.24 | unknown | unknown | unknown | unknown |
| A resume on which the operator explicitly asks for the new skill (`VERI_NEW_SKILL=1`) re-pins to `origin/<default>` as just fetched, not to the clone's `HEAD` | 2 | 1 | 0 | 0 | 0 | 48 | 11 | 20 | 5257 | 387982 | 78305 | 1.11 | unknown | unknown | unknown | unknown |
| `SKILL.md` no longer says pulling the primary clone changes the scripts under a live run | 8 | 3 | 1 | 0 | 0 | 232 | 55 | 104 | 20302 | 1964931 | 274214 | 4.25 | 4243 | 1/2 | 1/5 | nothing-left |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 266 | 510 | 97186 | 11066078 | 1381957 | 19.36 |
