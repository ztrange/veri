### 📊 Metrics — issue 1244

Wall time for the issue: 5604 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1248.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 16 | 4 | 8 | 1742 | 170440 | 44192 | 0.23 |
| red | 4 | 1 | 0 | 0 | 668 | 175 | 27 | 52 | 11335 | 1410860 | 207450 | 1.99 |
| green | 2 | 1 | 0 | 0 | 243 | 40 | 13 | 24 | 3856 | 557707 | 86333 | 0.68 |
| refactor | 2 | 1 | 0 | 0 | 132 | 26 | 9 | 18 | 2282 | 398322 | 86118 | 0.64 |
| pin | 2 | 2 | 0 | 0 | 498 | 28 | 7 | 14 | 2970 | 284464 | 85344 | 0.43 |
| predicate | 1 | 0 | 0 | 0 | 18 | 11 | 3 | 6 | 1075 | 115466 | 40913 | 0.37 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 778 | 90 | 25 | 48 | 8836 | 1019933 | 257067 | 1.32 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 804 | 206 | 38 | 74 | 14424 | 1917326 | 293283 | 3.02 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| strip_session_env keeps CLAUDE_BIN and every VERI_* variable whose value contains the session id, and still removes every other variable whose value carries it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 31 | 60 | 9092 | 1359003 | 259182 | 1.98 | 551 | unknown | 0/5 | nothing-left |  |  | full |
| run-conductor.sh, given a CLAUDE_BIN whose path contains CLAUDE_CODE_SESSION_ID, runs the binary CLAUDE_BIN names and hands that CLAUDE_BIN on in its environment, so the conductor's own leaves launch it too ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 12 | 22 | 4982 | 643846 | 112397 | 0.95 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/run-conductor.test.sh — FAIL - run-conductor.sh strips any variable whose value carries the session id (#933) (VERI_FAKE_CARRIER is still in the child's environment); skills/tdd/scripts/tests/run-leaf.test.sh — FAIL - strips a variable whose value contains the session id, and the id itself (#933) (VERI_FAKE_CARRIER reached the leaf's claude) ⟦suite-repair⟧ ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 96 | 16 | 32 | 7444 | 763970 | 134579 | 1.19 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| strip_session_env keeps CLAUDE_BIN and every VERI_* variable whose value contains the session id, and still removes every other variable whose value carries it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 132 | 0.64 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 1 | 1 | 2 | 1 | 3 | 223 |
| fast | 93 | 89 | 92 |  |  |  |  |  |
| target | 0 | 1 | 2 | 227 | 220 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 63 | 122 | 23260 | 2937259 | 550350 | 4.34 |
