### 📊 Metrics — issue 991

Wall time for the issue: 2583 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1036.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 27 | 19 | 4 | 8 | 1549 | 169915 | 42846 | 0.41 |
| red | 2 | 1 | 0 | 0 | 56 | 42 | 11 | 22 | 3187 | 512439 | 91071 | 0.89 |
| green | 2 | 1 | 0 | 0 | 158 | 45 | 10 | 20 | 3793 | 443089 | 85635 | 0.85 |
| refactor | 2 | 1 | 0 | 0 | 86 | 30 | 9 | 18 | 2284 | 393471 | 85749 | 0.81 |
| diff | 2 | 1 | 0 | 0 | 186 | 46 | 11 | 22 | 3727 | 492643 | 84821 | 0.85 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 5 | 5 | 0 | 0 | 324 | 106 | 27 | 54 | 8922 | 1206532 | 213559 | 2.13 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 189 | 76 | 18 | 36 | 5618 | 805025 | 176563 | 1.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-suite-runs.test.sh's `doc_text`, given a `from` regex `^5\. ` over a section holding the lines `5x y` and `5. y`, starts its output at `5. y`, not at `5x y` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 117 | 30 | 60 | 9264 | 1348999 | 262455 | 2.55 | 404 | unknown | 0/5 | nothing-left |  |  | full |
| skill-suite-runs.test.sh hands no `from` regex to awk through `-v`, so no backslash escape in it is processed by awk and gawk has no "escape sequence" warning to print on stderr ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 11 | 22 | 3727 | 492643 | 84821 | 0.85 | 216 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| skill-suite-runs.test.sh's `doc_text`, given a `from` regex `^5\. ` over a section holding the lines `5x y` and `5. y`, starts its output at `5. y`, not at `5x y` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 86 | 0.81 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 4 | 3 | 4 | 3 | 3 | 3 |
| fast | 41 | 41 | 40 | 40 | 41 | 41 |  |
| target | 4 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 45 | 90 | 14540 | 2011557 | 390122 | 3.81 |
