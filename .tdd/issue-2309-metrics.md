### 📊 Metrics — issue 2309

Wall time for the issue: 1931 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2333.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.05 over 50 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90270 |
| 2 | $0.03 | 91265 |
| 3 | $0.03 | 93202 |
| 4 | $0.02 | 93579 |
| 5 | $0.02 | 94017 |
| 6 | $0.02 | 94262 |
| 7 | $0.02 | 94555 |
| 8 | $0.02 | 94915 |
| 9 | $0.02 | 95531 |
| 10 | $0.03 | 96530 |
| 11 | $0.04 | 99237 |
| 12 | $0.02 | 99819 |
| 13 | $0.02 | 100121 |
| 14 | $0.02 | 100705 |
| 15 | $0.02 | 101231 |
| 16 | $0.02 | 101725 |
| 17 | $0.02 | 102182 |
| 18 | $0.03 | 103607 |
| 19 | $0.03 | 104416 |
| 20 | $0.02 | 104874 |
| 21 | $0.03 | 105575 |
| 22 | $0.03 | 106425 |
| 23 | $0.02 | 106857 |
| 24 | $0.04 | 108686 |
| 25 | $0.03 | 109133 |
| 26 | $0.03 | 109919 |
| 27 | $0.08 | 117340 |
| 28 | $0.03 | 118162 |
| 29 | $0.03 | 119179 |
| 30 | $0.03 | 120062 |
| 31 | $0.03 | 120784 |
| 32 | $0.03 | 121526 |
| 33 | $0.03 | 122107 |
| 34 | $0.03 | 122770 |
| 35 | $0.03 | 123386 |
| 36 | $0.03 | 123801 |
| 37 | $0.03 | 124393 |
| 38 | $0.03 | 125284 |
| 39 | $0.04 | 126590 |
| 40 | $0.04 | 129000 |
| 41 | $0.03 | 129803 |
| 42 | $0.03 | 130093 |
| 43 | $0.03 | 130913 |
| 44 | $0.03 | 131199 |
| 45 | $0.03 | 131446 |
| 46 | $0.03 | 131774 |
| 47 | $0.03 | 132285 |
| 48 | $0.03 | 132607 |
| 49 | $0.03 | 133022 |
| 50 | $0.03 | 133382 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 558 | 0 | 30447 | 0.08 |
| red | 3 | 1 | 0 | 0 | 80 | 56 | 20 | 40 | 6305 | 629511 | 80287 | 0.33 |
| green | 4 | 1 | 1 | 0 | 241 | 68 | 21 | 40 | 6626 | 564581 | 68470 | 0.39 |
| refactor | 2 | 1 | 0 | 0 | 54 | 15 | 8 | 16 | 1506 | 219494 | 28320 | 0.11 |
| pin | 1 | 1 | 0 | 0 | 21 | 12 | 5 | 10 | 1119 | 134636 | 14120 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 229 | 68 | 23 | 46 | 6830 | 607497 | 91807 | 0.36 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 76 | 53 | 21 | 42 | 6148 | 667445 | 80414 | 0.33 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 99 | 35 | 11 | 20 | 3136 | 273280 | 49423 | 0.28 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 241 | 0.39 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| metrics.sh <n> prints, in the Conductor own spending section, one line per conductor session, `Conductor context: first turn <a> tokens, largest <b> tokens`, where <a> and <b> are the first and the largest context the per-turn table shows for that session; pinned by an in-process unit case over a conductor log of two sessions (each closed by a result record) with known per-turn usage ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 117 | 43 | 84 | 12133 | 1223591 | 155883 | 0.73 | 535 | 1/2 | 1/5 | nothing-structural |  |  | full |
| a run whose log holds no conductor usage prints no `Conductor context:` line and the report still exits 0; pinned by an in-process unit case ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 22 | 3423 | 324631 | 35314 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| metrics.sh <n> prints, in the Conductor own spending section, one line per conductor session, `Conductor context: first turn <a> tokens, largest <b> tokens`, where <a> and <b> are the first and the largest context the per-turn table shows for that session; pinned by an in-process unit case over a conductor log of two sessions (each closed by a result record) with known per-turn usage ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 54 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 4 | 4 | 3 | 2 | 3 | 2 | 4 | 2 |
| fast | 23 | 23 | 23 | 26 | 26 |  |  |  |  |
| target | 4 | 4 | 3 | 4 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 55 | 108 | 16114 | 1548222 | 221644 | 0.97 |
