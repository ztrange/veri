### 📊 Metrics — issue 2835

Wall time for the issue: 2310 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2873.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.30 over 20 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87081 tokens, largest 127013 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87081 |
| 2 | $0.07 | 94137 |
| 3 | $0.03 | 95582 |
| 4 | $0.04 | 97784 |
| 5 | $0.05 | 101770 |
| 6 | $0.02 | 102243 |
| 7 | $0.02 | 102577 |
| 8 | $0.02 | 102878 |
| 9 | $0.04 | 104772 |
| 10 | $0.09 | 112876 |
| 11 | $0.04 | 115467 |
| 12 | $0.04 | 117435 |
| 13 | $0.03 | 118056 |
| 14 | $0.06 | 122343 |
| 15 | $0.03 | 123611 |
| 16 | $0.03 | 124203 |
| 17 | $0.03 | 124604 |
| 18 | $0.03 | 125467 |
| 19 | $0.03 | 126344 |
| 20 | $0.03 | 127013 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 661 | 0 | 30537 | 0.08 |
| prose | 7 | 0 | 0 | 0 | 295 | 267 | 7 | 14 | 41379 | 146879 | 468805 | 1.60 |
| skill-edit | 1 | 0 | 0 | 0 | 17 | 11 | 4 | 8 | 1109 | 385326 | 129514 | 0.37 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 661 | 0 | 30537 | 0.08 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SKILL.md`: rows PL62 (an issue holding more than one deliverable parks at Scope & plan with `$S/park-issue.sh`, before the plan is committed; step count alone never triggers it) and the amended RF40 (the run-budget park lists splitting the issue first, then raising `VERI_RUN_BUDGET`) are applied to its requirements list as the issue states them, the prose is brought up to them and regraded ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 178 | 8 | 16 | 27559 | 459489 | 418706 | 1.37 | 231 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 12 | 24 | 43149 | 532205 | 628856 | 3.36 (estimate) |
