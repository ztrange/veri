### 📊 Metrics — issue 1100

Wall time for the issue: 1662 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1136.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 924 | 12001 | 30743 | 0.13 |
| red | 6 | 3 | 0 | 0 | 155 | 134 | 35 | 68 | 11859 | 1533333 | 260793 | 2.12 |
| green | 6 | 3 | 0 | 0 | 328 | 145 | 41 | 82 | 13913 | 1844971 | 243648 | 2.08 |
| refactor | 6 | 3 | 0 | 0 | 168 | 91 | 32 | 60 | 8776 | 1232098 | 239320 | 1.81 |
| predicate | 1 | 0 | 0 | 0 | 14 | 11 | 4 | 8 | 1094 | 150162 | 36445 | 0.34 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 10 | 0 | 0 | 349 | 166 | 50 | 96 | 15967 | 1934434 | 382052 | 2.07 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 325 | 222 | 63 | 124 | 20599 | 2838131 | 428897 | 4.41 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With CLAUDE_CODE_SESSION_ID set and a TMPDIR whose path contains that id, run_leaf.main launches the leaf with GIT_CONFIG_GLOBAL still set to its private copy of ~/.gitconfig (the pinning case in tests/py/test_run_leaf.py that expects it unset changes its expectation) | 6 | 3 | 0 | 0 | 0 | 0 | 114 | 33 | 66 | 9838 | 1392499 | 240338 | 1.88 | 267 | unknown | 0/5 | nothing-left |  |  | full |
| With CLAUDE_CODE_SESSION_ID set, a CLAUDE_BIN whose value contains that id is still the binary run_leaf.main launches, not plain claude (the pinning case's expectation changes with it) | 6 | 3 | 0 | 0 | 0 | 0 | 152 | 42 | 80 | 13801 | 1862378 | 260294 | 2.21 | 328 | unknown | 0/5 | structural-owed |  |  | full |
| With CLAUDE_CODE_SESSION_ID set, a VERI_LEAF_MODEL whose value contains that id still reaches the leaf as --model <value> (the pinning case's expectation changes with it) | 7 | 3 | 0 | 0 | 0 | 0 | 115 | 37 | 72 | 12003 | 1505687 | 279574 | 2.27 | 250 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With CLAUDE_CODE_SESSION_ID set and a TMPDIR whose path contains that id, run_leaf.main launches the leaf with GIT_CONFIG_GLOBAL still set to its private copy of ~/.gitconfig (the pinning case in tests/py/test_run_leaf.py that expects it unset changes its expectation) | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.61 |
| With CLAUDE_CODE_SESSION_ID set, a CLAUDE_BIN whose value contains that id is still the binary run_leaf.main launches, not plain claude (the pinning case's expectation changes with it) | 1 | 0/5 | structural-owed | PASS | 0 | 59 | 0.60 |
| With CLAUDE_CODE_SESSION_ID set, a VERI_LEAF_MODEL whose value contains that id still reaches the leaf as --model <value> (the pinning case's expectation changes with it) | 1 | 0/5 | nothing-left | PASS | 0 | 52 | 0.60 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 2 | 29 | 1 | 2 | 0 | 0 | 1 | 2 | 2 | 1 | 1 |
| fast | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 113 | 220 | 36566 | 4772565 | 810949 | 6.49 |
