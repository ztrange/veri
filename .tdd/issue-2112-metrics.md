### 📊 Metrics — issue 2112

Wall time for the issue: 2082 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2139.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.43 over 50 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 85574 |
| 2 | $0.03 | 86553 |
| 3 | $0.04 | 88737 |
| 4 | $0.03 | 89130 |
| 5 | $0.03 | 89506 |
| 6 | $0.03 | 89861 |
| 7 | $0.04 | 91638 |
| 8 | $0.03 | 92210 |
| 9 | $0.55 | 85572 |
| 10 | $0.02 | 86468 |
| 11 | $0.03 | 88504 |
| 12 | $0.02 | 88872 |
| 13 | $0.02 | 89274 |
| 14 | $0.02 | 89610 |
| 15 | $0.02 | 90081 |
| 16 | $0.02 | 90488 |
| 17 | $0.02 | 91218 |
| 18 | $0.02 | 91982 |
| 19 | $0.02 | 92714 |
| 20 | $0.04 | 94875 |
| 21 | $0.03 | 96097 |
| 22 | $0.02 | 96742 |
| 23 | $0.02 | 97431 |
| 24 | $0.02 | 97780 |
| 25 | $0.02 | 98449 |
| 26 | $0.02 | 98979 |
| 27 | $0.03 | 99782 |
| 28 | $0.03 | 101020 |
| 29 | $0.02 | 101418 |
| 30 | $0.04 | 103467 |
| 31 | $0.03 | 104580 |
| 32 | $0.03 | 105288 |
| 33 | $0.03 | 106024 |
| 34 | $0.02 | 106310 |
| 35 | $0.03 | 106952 |
| 36 | $0.03 | 107923 |
| 37 | $0.03 | 108761 |
| 38 | $0.03 | 109626 |
| 39 | $0.03 | 110347 |
| 40 | $0.03 | 110713 |
| 41 | $0.03 | 111424 |
| 42 | $0.03 | 112108 |
| 43 | $0.03 | 112921 |
| 44 | $0.03 | 113276 |
| 45 | $0.03 | 113609 |
| 46 | $0.03 | 114177 |
| 47 | $0.03 | 114629 |
| 48 | $0.03 | 115239 |
| 49 | $0.03 | 115556 |
| 50 | $0.03 | 115898 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 11 | 3 | 6 | 875 | 60014 | 30645 | 0.09 |
| red | 2 | 1 | 0 | 0 | 60 | 35 | 8 | 16 | 4116 | 206542 | 51979 | 0.19 |
| green | 2 | 1 | 0 | 0 | 184 | 29 | 9 | 18 | 2576 | 241754 | 27412 | 0.12 |
| refactor | 2 | 1 | 0 | 0 | 48 | 15 | 6 | 12 | 1072 | 149722 | 26481 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 130 | 49 | 13 | 26 | 4055 | 311351 | 71256 | 0.25 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 176 | 41 | 13 | 26 | 4584 | 346681 | 65261 | 0.24 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| BAIL.md's `no-verdict` entry names the script of every site in SKILL.md and SKILL-EDIT.md that bails with cause `no-verdict` (among them `verify.sh` exit 2, the Draft PR regrade's `grade-prose.sh` exit 2 and the skill-edit runner `skill-edit-step.sh`'s exit 2), and the entry still classifies the cause a **system** failure; pinned by a small unit-tier pytest case that collects every `no-verdict` bail site in SKILL.md and SKILL-EDIT.md and fails naming each site whose script BAIL.md's `no-verdict` entry does not name ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 23 | 46 | 7764 | 598018 | 105872 | 0.40 | 425 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| BAIL.md's `no-verdict` entry names the script of every site in SKILL.md and SKILL-EDIT.md that bails with cause `no-verdict` (among them `verify.sh` exit 2, the Draft PR regrade's `grade-prose.sh` exit 2 and the skill-edit runner `skill-edit-step.sh`'s exit 2), and the entry still classifies the cause a **system** failure; pinned by a small unit-tier pytest case that collects every `no-verdict` bail site in SKILL.md and SKILL-EDIT.md and fails naming each site whose script BAIL.md's `no-verdict` entry does not name ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 48 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 7 | 0 | 73 | 8 | 7 |
| fast | 30 | 17 | 16 |  |  |  |
| target | 7 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 26 | 52 | 8639 | 658032 | 136517 | 0.49 |
