### 📊 Metrics — issue 1174

Wall time for the issue: 5200 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1220.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 10 | 3 | 6 | 921 | 114061 | 42387 | 0.20 |
| red | 4 | 2 | 0 | 0 | 252 | 194 | 43 | 86 | 16137 | 2718998 | 232549 | 2.33 |
| green | 6 | 2 | 1 | 0 | 1774 | 154 | 49 | 94 | 16064 | 2345107 | 278935 | 2.40 |
| refactor | 4 | 2 | 0 | 0 | 268 | 46 | 16 | 32 | 4396 | 686124 | 175237 | 1.27 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 1132 | 140 | 47 | 94 | 15027 | 2196927 | 350646 | 1.99 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 1178 | 264 | 64 | 124 | 22491 | 3667363 | 378462 | 4.21 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 763 | 1.58 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Every built developer prompt, through the shared develop-prompt text, tells the leaf it signals only processes it started, by the pid it recorded when it started them, never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`), and that an experiment's processes and leaf names carry the `exp-` prefix no live run uses ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 181 | 59 | 116 | 18865 | 3034067 | 392638 | 3.33 | 1138 | 1/2 | 0/5 | nothing-left |  |  | full |
| `skills/tdd/SKILL.md` tells the conductor it signals only processes it started, by the pid it recorded when it started them, never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`), and that an experiment's processes and leaf names carry the `exp-` prefix no live run uses ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 213 | 49 | 96 | 17732 | 2716162 | 294083 | 2.67 | 1394 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Every built developer prompt, through the shared develop-prompt text, tells the leaf it signals only processes it started, by the pid it recorded when it started them, never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`), and that an experiment's processes and leaf names carry the `exp-` prefix no live run uses ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 143 | 0.67 |
| `skills/tdd/SKILL.md` tells the conductor it signals only processes it started, by the pid it recorded when it started them, never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`), and that an experiment's processes and leaf names carry the `exp-` prefix no live run uses ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 125 | 0.60 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 4 | 9 | 9 | 13 | 11 | 4 | 4 | 4 | 6 | 4 | 1 | 4 | 1 | 2 | 1 | 4 | 322 | 0 |
| fast | 90 | 91 | 89 | 89 | 92 | 90 | 99 | 88 | 89 |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 111 | 218 | 37518 | 5864290 | 729108 | 6.20 |
