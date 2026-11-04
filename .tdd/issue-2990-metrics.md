### 📊 Metrics — issue 2990

Wall time for the issue: 8241 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3018.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.85 over 46 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89732 tokens, largest 122917 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89732 |
| 2 | $0.07 | 96676 |
| 3 | $0.03 | 98371 |
| 4 | $0.04 | 100378 |
| 5 | $0.02 | 100835 |
| 6 | $0.02 | 101150 |
| 7 | $0.02 | 101444 |
| 8 | $0.02 | 101793 |
| 9 | $0.02 | 102049 |
| 10 | $0.02 | 102524 |
| 11 | $0.02 | 102956 |
| 12 | $0.02 | 103327 |
| 13 | $0.02 | 103609 |
| 14 | $0.03 | 104346 |
| 15 | $0.03 | 105292 |
| 16 | $0.03 | 107019 |
| 17 | $0.03 | 107576 |
| 18 | $0.04 | 109380 |
| 19 | $0.02 | 109668 |
| 20 | $0.02 | 109962 |
| 21 | $0.03 | 110645 |
| 22 | $0.02 | 110977 |
| 23 | $0.03 | 111586 |
| 24 | $0.03 | 112138 |
| 25 | $0.03 | 112517 |
| 26 | $0.03 | 112918 |
| 27 | $0.03 | 113367 |
| 28 | $0.03 | 114133 |
| 29 | $0.03 | 114735 |
| 30 | $0.03 | 115522 |
| 31 | $0.03 | 116540 |
| 32 | $0.03 | 117496 |
| 33 | $0.03 | 117789 |
| 34 | $0.03 | 118011 |
| 35 | $0.03 | 118310 |
| 36 | $0.03 | 118613 |
| 37 | $0.03 | 118884 |
| 38 | $0.03 | 119217 |
| 39 | $0.03 | 119588 |
| 40 | $0.03 | 120305 |
| 41 | $0.03 | 121241 |
| 42 | $0.03 | 121535 |
| 43 | $0.03 | 121812 |
| 44 | $0.03 | 122109 |
| 45 | $0.03 | 122396 |
| 46 | $0.03 | 122917 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 1 | 2 | 1218 | 0 | 31229 | 0.09 |
| prose | 10 | 0 | 0 | 0 | 148 | 105 | 10 | 20 | 14462 | 33015 | 87772 | 0.37 |
| skill-edit | 2 | 0 | 0 | 0 | 44 | 37 | 7 | 12 | 2328 | 137630 | 45272 | 0.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 15 | 11 | 1 | 2 | 1218 | 0 | 31229 | 0.09 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/vdev/SKILL.md` states requirement rows D23 (each review finding is a blocking branch fix or a PR-body line, never an issue) and D24 (a PR adding or renaming a phase, subcommand, flag or event blocks on doc drift in the usage string, SCRIPTS.md, REVISE.md, REQUIREMENTS.md rows and prompt templates), and grade-prose.sh passes the unit ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 54 | 7 | 14 | 6443 | 76370 | 66315 | 0.24 | 105 | unknown | unknown | unknown |  |  | full |
| `skills/vfile/SKILL.md` states requirement rows F16 (one foreign-repo run's veri defects filed as one bug+candidate issue, never opted in) and F17 (a bug in a module an open PRD rebuilds is added to that PRD as a case, no issue filed, the PRD url reported), and grade-prose.sh passes the unit ⟦skill-edit⟧ ⟦criterion 2⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 59 | 8 | 14 | 5373 | 92110 | 43526 | 0.17 | 105 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 18 | 34 | 18008 | 170645 | 164273 | 2.46 (estimate) |
