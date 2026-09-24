### 📊 Metrics — issue 271

Wall time for the issue: 8648 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 21 of 21 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/459.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 50 | 41 | 5 | 10 | 4232 | 161383 | 76726 | 0.73 |
| red | 40 | 18 | 0 | 0 | 1603 | 1243 | 297 | 570 | 117413 | 13532138 | 1772752 | 19.24 |
| green | 48 | 17 | 7 | 0 | 5264 | 1599 | 389 | 774 | 154863 | 17910951 | 1861420 | 21.57 |
| refactor | 34 | 17 | 0 | 0 | 2417 | 984 | 242 | 484 | 93256 | 11296698 | 1475788 | 15.93 |
| pin | 4 | 4 | 0 | 0 | 116 | 68 | 15 | 30 | 6333 | 565414 | 154447 | 1.48 |
| exhausted | 1 | 0 | 0 | 0 | 32 | 29 | 6 | 12 | 2611 | 265678 | 47412 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 4026 | 16.07 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `workqueue.sh assign <worker> <issue>...` appends one `<worker>	<issue>	queued	` line per issue to `.tdd/workqueue`, in the order given ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 186 | 43 | 86 | 18188 | 1948941 | 256183 | 2.80 | 479 | unknown | 0/5 | nothing-left |
| `workqueue.sh <unknown-subcommand> …` (e.g. `workqueue.sh frobnicate alpha 12`) exits 2 and leaves `.tdd/workqueue` byte-identical (absent if it was absent) ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 39 | 78 | 13555 | 1665127 | 234585 | 2.48 | 235 | unknown | 0/5 | structural-owed |
| `workqueue.sh frobnicate alpha 12` in a repo with no `.tdd/workqueue` exits 2 and leaves `.tdd/workqueue` absent ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 12 | 24 | 4628 | 507815 | 77523 | 0.81 | unknown | unknown | unknown | unknown |
| `workqueue.sh assign` refuses with exit 2, leaving the file byte-identical, an issue already `queued` or `running` for any worker ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 216 | 51 | 102 | 20468 | 2202883 | 320915 | 3.42 | 634 | 1/2 | 1/5 | nothing-structural |
| `workqueue.sh next <worker>` prints that worker's first `queued` issue whose `## Blocked by` names no open issue, skipping a blocked one, read from `VERI_GH_JSON` fixtures ⟦criterion 2⟧ | 15 | 4 | 3 | 0 | 0 | 0 | 548 | 123 | 244 | 52698 | 5918870 | 610962 | 7.13 | 717 | 2/2 | 0/5 | structural-owed |
| `workqueue.sh next <worker>` does not treat a `## Blocked by` entry that is a full GitHub URL to an open issue in another repository as a blocker of this repository's issue: it passes this repository's owner/name to `blocked_by.blockers` the way solvable-issues.sh does, instead of an empty string ⟦added⟧ ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 324 | 77 | 152 | 30942 | 3767905 | 332259 | 4.03 | 797 | 1/2 | 3/5 | nothing-structural |
| `workqueue.sh next <worker>` exits 3 with empty stdout when none of that worker's `queued` items is launchable ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 159 | 41 | 82 | 15512 | 1857580 | 258387 | 2.75 | 288 | unknown | 1/5 | nothing-structural |
| `workqueue.sh start <worker> <issue>` moves that worker's `queued` item to `running` ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 243 | 57 | 110 | 24351 | 2536395 | 300644 | 3.40 | 704 | 1/2 | 1/5 | structural-owed |
| `workqueue.sh done <worker> <issue> <sha>` moves that worker's `running` item to `merged`, recording the sha as its detail ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 153 | 40 | 80 | 14740 | 1815608 | 259425 | 2.73 | 289 | unknown | 0/5 | nothing-left |
| `workqueue.sh park <worker> <issue> <reason>` moves that worker's `running` item to `parked`, recording the reason as its detail ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 144 | 41 | 80 | 13731 | 1794345 | 251597 | 2.65 | 282 | unknown | 0/5 | nothing-left |
| `start`, `done` or `park` naming an item another worker owns exits 1 and leaves the file byte-identical ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 49 | 96 | 18677 | 2320188 | 269706 | 3.00 | 345 | unknown | 2/5 | structural-owed |
| `start` on an item not `queued`, or `done`/`park` on an item not `running`, exits 1 and leaves the file byte-identical ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 13 | 26 | 5857 | 605864 | 86923 | 0.93 | unknown | unknown | unknown | unknown |
| After any sequence of `assign`, `start`, `done`, `park` and refused calls, every issue ever assigned is still a line in the file ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 15 | 30 | 6116 | 739583 | 90163 | 0.99 | unknown | unknown | unknown | unknown |
| N `assign`/`start` calls run in parallel leave a well-formed file containing every write ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 277 | 66 | 130 | 26417 | 3188757 | 328980 | 3.80 | 868 | 1/2 | 1/5 | nothing-structural |
| A write that cannot take the lock exits 2 without touching the file ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 248 | 51 | 100 | 22378 | 2438063 | 276347 | 3.15 | 465 | unknown | 1/5 | nothing-structural |
| `workqueue.sh show` prints every item grouped by worker, each with its issue and state | 6 | 3 | 0 | 0 | 0 | 0 | 157 | 38 | 72 | 14598 | 1608556 | 255945 | 2.66 | 300 | unknown | 0/5 | nothing-left |
| `workqueue.sh show <worker>` prints only that worker's items | 6 | 3 | 0 | 0 | 0 | 0 | 161 | 40 | 80 | 14534 | 1789690 | 246086 | 2.62 | 327 | unknown | 1/5 | nothing-structural |
| Called from a linked worktree, `workqueue.sh` reads and writes `.tdd/workqueue` under the repository's main working tree, not the worktree's own | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 13 | 24 | 6154 | 583889 | 94099 | 0.99 | unknown | unknown | unknown | unknown |
| The worker loop is documented in a `WORKER.md` beside `SKILL.md`, naming each `workqueue.sh` call (`next`, `start`, `done`, `park`) ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 50 | 98 | 16488 | 2297549 | 259100 | 2.86 | 1387 | unknown | 1/5 | nothing-structural |
| `SKILL.md` tells a session born as a worker to `Read` `WORKER.md`, the way it points a scope at `SCOPE-LOOP.md` ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 209 | 51 | 100 | 20655 | 2326791 | 255310 | 2.92 | 616 | unknown | 1/5 | nothing-structural |
| `CONTEXT.md` defines **worker** and **work queue** ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 143 | 39 | 76 | 13789 | 1656480 | 246680 | 2.58 | 607 | unknown | 0/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 1 | 0 | 106 | 0 | 65 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 2 | 6 | 297 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 0 | 2 | 3 | 3 | 2 | 2 | 2 | 0 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 3 | 2 | 3 | 3 | 3 | 3 | 1 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 4 | 4 | 0 | 0 | 5 | 5 | 6 | 0 | 6 | 5 | 8 | 8 | 0 | 6 | 6 | 6 | 6 | 5 | 5 | 6 | 5 | 7 | 5 | 6 | 6 | 6 | 6 | 5 | 1 | 0 | 6 | 6 | 6 | 6 | 6 | 302 | 21 | 71 | 301 | 307 | 6 | 6 | 0 | 86 | 0 | 87 | 86 | 6 | 6 | 6 | 6 | 308 | 14 | 0 | 6 |
| fast | 2 | 3 | 3 | 2 | 3 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 2 | 3 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 3 | 2 | 3 | 2 | 2 | 3 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 3 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 3 | 0 | 3 | 3 | 3 | 4 | 3 | 5 | 5 | 5 | 6 | 5 | 6 | 6 | 0 | 6 | 6 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 292 | 296 | 297 | 289 | 291 | 299 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 954 | 1880 | 378708 | 43732262 | 5388545 | 59.44 |
