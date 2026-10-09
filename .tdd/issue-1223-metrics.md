### 📊 Metrics — issue 1223

Wall time for the issue: 3753 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1245.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 7 | 2 | 4 | 682 | 63420 | 40466 | 0.18 |
| red | 2 | 1 | 0 | 0 | 91 | 69 | 14 | 28 | 7223 | 783971 | 106998 | 0.97 |
| green | 2 | 1 | 0 | 0 | 506 | 85 | 26 | 52 | 8299 | 1512902 | 106934 | 1.12 |
| refactor | 2 | 1 | 0 | 0 | 245 | 31 | 10 | 18 | 2998 | 393804 | 88852 | 0.66 |
| predicate | 1 | 0 | 0 | 0 | 19 | 12 | 3 | 6 | 1145 | 115070 | 41055 | 0.37 |
| structural | 1 | 0 | 0 | 0 | 29 | 19 | 5 | 10 | 1793 | 229574 | 46063 | 0.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 490 | 60 | 18 | 34 | 5860 | 744431 | 171953 | 0.90 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 415 | 163 | 42 | 84 | 16280 | 2354310 | 258415 | 2.86 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Every verifier prompt build-verify-prompt.sh produces, for every phase it accepts, states the rule the develop prompts state — signal only processes you started, by the pid you recorded, never by name or pattern (pkill, killall, kill $(pgrep …)) — and both take it from one shared partial under prompts/ that each includes, so the rule's text is spelled in exactly one prompt file ⟦criterion 1⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 216 | 58 | 114 | 21458 | 3035321 | 389902 | 3.58 | 976 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Every verifier prompt build-verify-prompt.sh produces, for every phase it accepts, states the rule the develop prompts state — signal only processes you started, by the pid you recorded, never by name or pattern (pkill, killall, kill $(pgrep …)) — and both take it from one shared partial under prompts/ that each includes, so the rule's text is spelled in exactly one prompt file ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 245 | 0.66 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 6 | 9 | 96 | 3 |
| fast | 88 | 90 | 94 | 92 |  |  |
| target | 1 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 60 | 118 | 22140 | 3098741 | 430368 | 3.76 |
