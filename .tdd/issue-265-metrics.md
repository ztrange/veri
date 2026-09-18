### 📊 Metrics — issue 265

Wall time for the issue: 10071 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/309.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 291 | 162 | 36 | 68 | 14731 | 1734266 | 171102 | 1.99 |
| green | 6 | 2 | 1 | 0 | 7239 | 404 | 92 | 174 | 31559 | 4956205 | 298958 | 4.44 |
| refactor | 5 | 2 | 0 | 0 | 2317 | 267 | 61 | 122 | 21263 | 3278496 | 217814 | 2.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 5029 | 3.27 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| a VERI_NEW_SKILL=1 re-pin that runs before .tdd/wt/<n> exists writes its skill-repin event to the run worktree's .tdd/events.jsonl and never to the caller's ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 494 | 116 | 224 | 41333 | 6393466 | 387519 | 5.52 | 6425 | 1/2 | 1/5 | nothing-structural |
| SKILL.md's $S paragraph no longer says "Nothing here pins it" and states that the skill snapshot (VERI_SKILL_COMMIT, .tdd/issue-<n>-skill-commit) pins the commit a run executes under ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 339 | 73 | 140 | 26220 | 3575501 | 300355 | 3.53 | 3624 | unknown | 2/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 189 | 364 | 67553 | 9968967 | 687874 | 9.05 |
