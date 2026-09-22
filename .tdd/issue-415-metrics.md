### 📊 Metrics — issue 415

Wall time for the issue: 7267 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/419.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 11 | 4 | 0 | 0 | 2221 | 1882 | 224 | 388 | 134004 | 14289669 | 832921 | 18.83 |
| green | 8 | 4 | 0 | 0 | 2456 | 1037 | 167 | 298 | 71703 | 9293778 | 499764 | 11.44 |
| refactor | 8 | 4 | 0 | 0 | 1404 | 972 | 132 | 254 | 65638 | 8012413 | 461048 | 10.26 |
| pin | 3 | 3 | 0 | 0 | 317 | 183 | 35 | 58 | 12134 | 1558025 | 155267 | 2.64 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A suite fails when a verifier launch line in SKILL.md reaches verify.sh without supervise.sh on the same line, and every verifier launch in SKILL.md carries it the way the developer launches do ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 577 | 91 | 166 | 39780 | 4922042 | 351758 | 6.97 | 955 | unknown | 1/5 | nothing-structural |
| A wait on a verifier whose supervisor died ends with exit 2 instead of polling to its deadline, and SKILL.md reports that verifier the way it reports a killed developer leaf ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 611 | 90 | 158 | 39484 | 4643227 | 343360 | 6.74 | 1125 | unknown | 2/5 | structural-owed |
| A supervised verifier launch passes verify.sh only the phase, the spec file, the test path and the test id — or the base sha for refactor — so nothing the supervisor adds can carry the developer's rationale ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 178 | 29 | 52 | 14475 | 1599584 | 113456 | 2.30 | unknown | unknown | unknown | unknown |
| A supervised verification still writes only the verdict text to .tdd/verify-<phase>.reason, and a malformed verdict still reaches the conductor as 2 while a REJECT reaches it as 1 ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 1182 | 152 | 272 | 83156 | 9645573 | 423189 | 11.13 | 2253 | unknown | 2/5 | structural-owed |
| The launch guard is known to go red: a planted verifier launch line missing supervise.sh makes the suite fail and name that line, so the contradiction cannot return as prose ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 547 | 43 | 78 | 39363 | 3171860 | 172405 | 4.29 | unknown | unknown | unknown | unknown |
| A verifier killed before it answered leaves no verdict event in the run's event log while one that answered does, so a stalled wait is never read as a verdict ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 227 | 40 | 68 | 16663 | 2572289 | 158575 | 3.29 | unknown | unknown | unknown | unknown |
| A verification whose leaf is working while the launch wrapper around it stays silent is not killed for that silence, so supervising the wrapper adds no second heartbeat window | 6 | 3 | 0 | 0 | 0 | 0 | 752 | 113 | 204 | 50558 | 6599310 | 386257 | 8.43 | 1273 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 62 | 0 | 62 | 0 | 0 | 1 | 1 | 61 | 256 | 1 | 1 | 1 | 33 | 1 | 0 | 0 | 42 | 35 | 56 | 232 | 56 | 55 | 38 | 56 | 54 | 12 | 39 | 34 | 17 | 17 | 16 | 237 | 18 | 17 |
| fast | 3 | 2 | 2 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 | 40 | 0 | 1 | 41 | 49 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 558 | 998 | 283479 | 33153885 | 1949000 | 43.16 |
