### 📊 Metrics — issue 1733

Wall time for the issue: 676 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 9 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 12 | 1 | 2 | 1464 | 17463 | 15199 | 0.05 |
| red | 4 | 2 | 0 | 0 | 424 | 107 | 25 | 50 | 9299 | 847943 | 105405 | 0.63 |
| green | 3 | 0 | 0 | 0 | 93 | 53 | 17 | 32 | 5412 | 496924 | 51308 | 0.36 |
| exhausted | 1 | 0 | 0 | 0 | 16 | 13 | 3 | 6 | 1251 | 78244 | 13462 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 39 | 28 | 7 | 14 | 2923 | 179854 | 49284 | 0.17 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 509 | 157 | 39 | 76 | 14503 | 1260720 | 136090 | 0.98 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 424 | 0.63 |
| green | 0 | 0.00 | 93 | 0.36 |
| exhausted | 0 | 0.00 | 16 | 0.11 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On a step neither repair-marked nor `⟦replaces-case⟧`, `tests-frozen.sh check --step` exits 1 and prints the path of a tracked test file (under a `tests/` directory or named `*.test.*`, `transform-touches-tests.sh`'s rule) that the step's record does not hold and that is modified against `HEAD` (a case in a real git repo under `tmp_path` may run git, marked as a process case) ⟦criterion 1⟧ | 8 | 2 | 0 | 0 | 0 | 0 | 173 | 45 | 88 | 15962 | 1423111 | 170175 | 1.10 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 |
| fast | 10 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 46 | 90 | 17426 | 1440574 | 185374 | 1.15 |
