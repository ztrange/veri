### 📊 Metrics — issue 1081

Wall time for the issue: 2286 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1085.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 2 | 4 | 1290 | 57070 | 40530 | 0.36 |
| red | 2 | 0 | 0 | 0 | 103 | 62 | 15 | 28 | 6670 | 697470 | 96326 | 1.04 |
| pin | 2 | 2 | 0 | 0 | 79 | 41 | 12 | 24 | 4236 | 543266 | 87835 | 0.90 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 3 | 3 | 0 | 0 | 96 | 55 | 14 | 28 | 5526 | 600336 | 128365 | 1.26 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 103 | 62 | 15 | 28 | 6670 | 697470 | 96326 | 1.04 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The "no verifier prompt carries the prediction" case in build-verify-prompt.test.sh builds each phase (red, green, refactor, pin) with VERI_PREDICTED_FAILURE set and only that phase's normal arguments, and asserts for each phase that the builder exits 0, prints a non-empty prompt, and that the prompt carries neither the prediction text nor a request for a prediction ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 16 | 30 | 6658 | 736314 | 94395 | 1.04 | unknown | unknown | unknown | unknown |  |  | pin |
| A separate case in build-verify-prompt.test.sh pins that build-verify-prompt.sh refuses a fifth positional argument: exit 2 and nothing on stdout ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 11 | 22 | 4248 | 504422 | 89766 | 0.90 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 6 | 9 |  |  |
| target | 7 | 6 | 7 | 8 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 29 | 56 | 12196 | 1297806 | 224691 | 2.30 |
