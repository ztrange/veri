### 📊 Metrics — issue 173

Wall time for the issue: 10651 s, from the first event of the log to the mark that ended the run.
Steps done: 6 of 8 planned.
Outcome: the run bailed — no-verdict, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 12 | 5 | 0 | 0 | 1967 | 503 | 83 | 164 | 40018 | 4072064 | 483864 | 5.66 |
| green | 10 | 4 | 0 | 0 | 5604 | 302 | 76 | 148 | 21695 | 3512642 | 343395 | 3.90 |
| refactor | 8 | 4 | 0 | 0 | 2485 | 394 | 46 | 92 | 16233 | 2373242 | 245512 | 3.67 |
| pin | 2 | 2 | 0 | 0 | 237 | 106 | 28 | 46 | 8462 | 1207026 | 72750 | 0.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 447 | 0.97 |
| green | 0 | 0.00 | 2133 | 0.65 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| wait-leaf.sh exits 2, well before max-seconds, with a diagnostic on stderr naming the leaf and the dead pid, when no completion file exists and the pid file names a process that has exited | 6 | 3 | 0 | 0 | 0 | 197 | 27 | 52 | 9856 | 1116372 | 169420 | 2.22 | 1807 | unknown | 1/5 | triage |
| wait-leaf.sh treats a recorded pid that is alive but is not a supervise.sh for that name (pid reuse) as a dead supervisor | 6 | 3 | 0 | 0 | 0 | 209 | 43 | 84 | 16277 | 2056426 | 234420 | 2.52 | 1659 | unknown | 1/5 | triage |
| wait-leaf.sh still exits 3 while the recorded supervise.sh for that name is alive, and a missing pid file is not dead | 2 | 1 | 0 | 0 | 0 | 79 | 18 | 34 | 7629 | 835961 | 75299 | 0.87 | unknown | unknown | unknown | unknown |
| wait-leaf.sh returns the recorded code when the completion file lands just before the supervisor exits | 2 | 1 | 0 | 0 | 0 | 88 | 19 | 30 | 6978 | 724935 | 76746 | 0.88 | unknown | unknown | unknown | unknown |
| supervise.sh records its own pid in .tdd/<name>.pid before it launches the leaf | 6 | 3 | 0 | 0 | 0 | 324 | 64 | 128 | 22251 | 3462597 | 262196 | 2.99 | 2414 | unknown | 0/5 | nothing-left |
| supervise.sh sent TERM, INT or HUP writes 2 to its completion file, exits 2 and leaves no leaf process behind | 6 | 3 | 0 | 0 | 0 | 274 | 35 | 68 | 13148 | 1715908 | 205129 | 2.73 | 1743 | unknown | 0/5 | nothing-left |
| A pid file left by an earlier leaf of the same name cannot end a later wait early: SKILL.md's launch lines clear .tdd/<name>.pid together with .tdd/<name>.exit | 4 | 1 | 0 | 0 | 0 | 134 | 27 | 54 | 10269 | 1252775 | 122311 | 1.63 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 233 | 450 | 86408 | 11164974 | 1145521 | 13.84 |
