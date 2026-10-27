### 📊 Metrics — issue 2473

Wall time for the issue: 1200 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2538.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.66 over 42 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88948 tokens, largest 117033 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88948 |
| 2 | $0.02 | 89327 |
| 3 | $0.03 | 90406 |
| 4 | $0.03 | 92293 |
| 5 | $0.02 | 92620 |
| 6 | $0.02 | 92949 |
| 7 | $0.02 | 93642 |
| 8 | $0.02 | 93933 |
| 9 | $0.02 | 94188 |
| 10 | $0.02 | 94793 |
| 11 | $0.03 | 95800 |
| 12 | $0.03 | 96852 |
| 13 | $0.02 | 97170 |
| 14 | $0.03 | 97892 |
| 15 | $0.02 | 98390 |
| 16 | $0.03 | 99218 |
| 17 | $0.03 | 100560 |
| 18 | $0.02 | 101116 |
| 19 | $0.02 | 101554 |
| 20 | $0.03 | 102199 |
| 21 | $0.03 | 102879 |
| 22 | $0.03 | 103505 |
| 23 | $0.03 | 104116 |
| 24 | $0.03 | 105108 |
| 25 | $0.03 | 105969 |
| 26 | $0.03 | 106793 |
| 27 | $0.03 | 107462 |
| 28 | $0.02 | 107791 |
| 29 | $0.03 | 108652 |
| 30 | $0.03 | 109154 |
| 31 | $0.03 | 109577 |
| 32 | $0.03 | 110825 |
| 33 | $0.04 | 113242 |
| 34 | $0.03 | 113966 |
| 35 | $0.03 | 114253 |
| 36 | $0.03 | 114824 |
| 37 | $0.03 | 115263 |
| 38 | $0.02 | 115499 |
| 39 | $0.03 | 115767 |
| 40 | $0.03 | 116255 |
| 41 | $0.03 | 116534 |
| 42 | $0.03 | 117033 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 645 | 0 | 31851 | 0.09 |
| red | 3 | 1 | 0 | 0 | 74 | 60 | 13 | 26 | 5743 | 385629 | 77429 | 0.29 |
| green | 2 | 1 | 0 | 0 | 91 | 31 | 11 | 18 | 2564 | 256409 | 31035 | 0.13 |
| refactor | 1 | 0 | 0 | 0 | 8 | 6 | 2 | 4 | 144 | 49042 | 14289 | 0.04 |
| pin | 1 | 1 | 0 | 0 | 27 | 21 | 3 | 6 | 946 | 77681 | 14491 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 101 | 50 | 11 | 22 | 3541 | 267180 | 77139 | 0.26 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 106 | 73 | 19 | 34 | 6501 | 501581 | 91956 | 0.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill_edit_step.main with `--change`, on a unit that grades PASS and at least one pin file, whose author edits only the pin file and leaves the unit byte-identical, fails the attempt with `FAIL: the author left the prose unchanged` (exit 1, no commit) instead of exiting 0 ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 61 | 21 | 38 | 5595 | 525589 | 99472 | 0.36 | 274 | unknown | 0/5 | nothing-left |  |  | full |
| skill_edit_step.main with `--change`, whose author changes the unit and leaves every pin file untouched, still succeeds (exit 0, the step committed), so the unit-only comparison does not count a real prose change as no change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 8 | 16 | 3802 | 243172 | 37772 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| skill_edit_step.main with `--change`, on a unit that grades PASS and at least one pin file, whose author edits only the pin file and leaves the unit byte-identical, fails the attempt with `FAIL: the author left the prose unchanged` (exit 1, no commit) instead of exiting 0 ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 17 | 1 |
| fast | 17 | 16 |  |  |  |
| target | 1 | 2 | 1 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 30 | 56 | 10042 | 768761 | 169095 | 2.26 (estimate) |
