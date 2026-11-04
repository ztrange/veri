### 📊 Metrics — issue 2927

Wall time for the issue: 5556 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 5 planned.
Outcome: the run bailed — revise-impossible, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.78 over 61 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90173 tokens, largest 169948 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90173 |
| 2 | $0.07 | 97156 |
| 3 | $0.03 | 98742 |
| 4 | $0.03 | 100302 |
| 5 | $0.02 | 100574 |
| 6 | $0.03 | 101261 |
| 7 | $0.02 | 101587 |
| 8 | $0.02 | 101873 |
| 9 | $0.02 | 102129 |
| 10 | $0.03 | 102719 |
| 11 | $0.03 | 104138 |
| 12 | $0.04 | 106099 |
| 13 | $0.08 | 113925 |
| 14 | $0.03 | 115389 |
| 15 | $0.03 | 115733 |
| 16 | $0.03 | 116502 |
| 17 | $0.03 | 117031 |
| 18 | $0.03 | 117515 |
| 19 | $0.03 | 118019 |
| 20 | $0.03 | 118204 |
| 21 | $0.03 | 118430 |
| 22 | $0.03 | 119047 |
| 23 | $0.03 | 120383 |
| 24 | $0.03 | 120730 |
| 25 | $0.03 | 121016 |
| 26 | $0.03 | 121817 |
| 27 | $0.03 | 122665 |
| 28 | $0.04 | 124327 |
| 29 | $0.03 | 124930 |
| 30 | $0.08 | 131198 |
| 31 | $0.03 | 131535 |
| 32 | $0.03 | 132063 |
| 33 | $0.03 | 132465 |
| 34 | $0.03 | 132998 |
| 35 | $0.03 | 133627 |
| 36 | $0.04 | 135122 |
| 37 | $0.04 | 136397 |
| 38 | $0.03 | 137170 |
| 39 | $0.03 | 137706 |
| 40 | $0.03 | 138507 |
| 41 | $0.03 | 139270 |
| 42 | $0.05 | 142176 |
| 43 | $0.03 | 142961 |
| 44 | $0.03 | 143405 |
| 45 | $0.04 | 144246 |
| 46 | $0.04 | 145131 |
| 47 | $0.03 | 145615 |
| 48 | $0.04 | 146584 |
| 49 | $0.03 | 147237 |
| 50 | $0.04 | 148236 |
| 51 | $0.04 | 148965 |
| 52 | $0.04 | 149799 |
| 53 | $0.03 | 150095 |
| 54 | $0.04 | 150771 |
| 55 | $0.03 | 151073 |
| 56 | $0.03 | 151631 |
| 57 | $0.05 | 154406 |
| 58 | $0.10 | 162749 |
| 59 | $0.04 | 164027 |
| 60 | $0.04 | 165356 |
| 61 | $0.07 | 169948 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 7 | 1 | 2 | 892 | 0 | 32038 | 0.09 |
| red | 4 | 1 | 0 | 0 | 2756 | 82 | 21 | 38 | 8690 | 515582 | 151455 | 0.52 |
| green | 6 | 1 | 2 | 0 | 747 | 143 | 31 | 54 | 9241 | 801636 | 105644 | 0.44 |
| pin | 2 | 2 | 0 | 0 | 54 | 25 | 8 | 16 | 2509 | 226573 | 34308 | 0.13 |
| refactor | 2 | 0 | 0 | 0 | 62 | 53 | 8 | 16 | 4051 | 232321 | 67958 | 0.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 5 | 2 | 0 | 552 | 105 | 28 | 50 | 10162 | 667217 | 153441 | 0.55 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 3018 | 152 | 33 | 60 | 11170 | 876574 | 170004 | 0.62 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 62 | 53 | 8 | 16 | 4051 | 232321 | 67958 | 0.42 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 2756 | 0.52 |
| green | 0 | 0.00 | 747 | 0.44 |
| pin | 0 | 0.00 | 54 | 0.13 |
| refactor | 0 | 0.00 | 62 | 0.42 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf rewrote (its content changed, truncated or appended to) is byte-identical to what it held before the leaf ⟦criterion 1⟧ | 14 | 4 | 2 | 0 | 0 | 0 | 303 | 68 | 124 | 24491 | 1776112 | 359365 | 1.51 | unknown | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf rewrote (its content changed, truncated or appended to) is byte-identical to what it held before the leaf ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 1 | 62 | 0.42 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 16 | 24 | 3 | 13 | 30 | 12 | 25 | 14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 61 | 43 | 35 | 51 | 51 | 38 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 6 | 6 | 4 | 6 | 5 | 6 | 5 | 5 | 5 | 6 | 4 | 6 | 5 | 5 | 5 | 6 | 6 | 5 | 5 | 6 | 4 | 6 | 6 | 5 | 5 | 5 | 5 | 9 | 8 | 9 | 8 | 8 | 6 | 4 | 5 | 5 | 6 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 69 | 126 | 25383 | 1776112 | 391403 | 4.38 (estimate) |
