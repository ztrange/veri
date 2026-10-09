### 📊 Metrics — issue 1208

Wall time for the issue: 3299 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1213.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 644 | 12385 | 29939 | 0.13 |
| diff | 4 | 1 | 1 | 0 | 2036 | 271 | 41 | 82 | 23673 | 2093690 | 181782 | 1.97 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 2 | 1 | 0 | 1399 | 65 | 13 | 26 | 6870 | 523923 | 108270 | 0.61 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 645 | 211 | 29 | 58 | 17447 | 1582152 | 103451 | 1.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 2036 | 1.97 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The #1126 SIGTERM-to-process-group case in orchestrate.test.sh records the writer's exit status before the case reads it, so under any scheduling it never reads -1, and still tells 143 (SIGTERM) from 141 (SIGPIPE) ⟦diff-checked⟧ ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 271 | 41 | 82 | 23673 | 2093690 | 181782 | 1.97 | 2098 | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 27 | 29 | 28 | 28 |
| affected | 8 | 8 | 8 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 42 | 84 | 24317 | 2106075 | 211721 | 2.10 |
