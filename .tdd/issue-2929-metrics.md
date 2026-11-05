### 📊 Metrics — issue 2929

Wall time for the issue: 4096 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3078.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.03 over 40 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90492 tokens, largest 148412 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90492 |
| 2 | $0.08 | 97733 |
| 3 | $0.03 | 99595 |
| 4 | $0.02 | 100159 |
| 5 | $0.03 | 101989 |
| 6 | $0.03 | 103045 |
| 7 | $0.02 | 103477 |
| 8 | $0.02 | 103729 |
| 9 | $0.02 | 104019 |
| 10 | $0.02 | 104272 |
| 11 | $0.03 | 104881 |
| 12 | $0.06 | 110302 |
| 13 | $0.04 | 112300 |
| 14 | $0.04 | 115074 |
| 15 | $0.05 | 117919 |
| 16 | $0.03 | 119097 |
| 17 | $0.03 | 119407 |
| 18 | $0.03 | 120023 |
| 19 | $0.03 | 120564 |
| 20 | $0.05 | 123626 |
| 21 | $0.03 | 124187 |
| 22 | $0.03 | 124389 |
| 23 | $0.03 | 125653 |
| 24 | $0.03 | 126631 |
| 25 | $0.03 | 127373 |
| 26 | $0.12 | 139763 |
| 27 | $0.05 | 142880 |
| 28 | $0.03 | 143538 |
| 29 | $0.03 | 143727 |
| 30 | $0.03 | 144423 |
| 31 | $0.03 | 144873 |
| 32 | $0.03 | 145149 |
| 33 | $0.03 | 145363 |
| 34 | $0.03 | 145628 |
| 35 | $0.03 | 146278 |
| 36 | $0.04 | 147263 |
| 37 | $0.03 | 147484 |
| 38 | $0.03 | 147705 |
| 39 | $0.03 | 147990 |
| 40 | $0.03 | 148412 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 989 | 0 | 32050 | 0.09 |
| prose | 5 | 0 | 0 | 0 | 82 | 70 | 5 | 10 | 11011 | 21298 | 85130 | 0.33 |
| skill-edit | 1 | 0 | 0 | 0 | 13 | 11 | 5 | 8 | 1234 | 125026 | 43618 | 0.13 |
| red | 1 | 0 | 0 | 0 | 48 | 32 | 7 | 14 | 3635 | 210041 | 38927 | 0.15 |
| pin | 1 | 1 | 0 | 0 | 20 | 12 | 4 | 6 | 1377 | 78136 | 14844 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 30 | 20 | 5 | 8 | 2366 | 78136 | 46894 | 0.15 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 48 | 32 | 7 | 14 | 3635 | 210041 | 38927 | 0.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a unit case in skills/tdd/scripts/tests/py/unit/test_skill_revise_build_first.py pins that REVISE.md's revise loop runs `build-develop-prompt.sh revise <phase>` before it posts the `♻️ Revise` comment and writes the `event.sh revise` mark, and that it states a build exit 2 posts no comment, writes no revise mark, launches no leaf and bails as a system failure (a small case reading REVISE.md's text, no production change) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 11 | 20 | 5012 | 288177 | 53771 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 3 |  |
| target | 3 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 22 | 40 | 18246 | 434501 | 214569 | 2.79 (estimate) |
