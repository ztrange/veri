### 📊 Metrics — issue 1031

Wall time for the issue: 1977 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1044.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1033 | 11866 | 30355 | 0.13 |
| red | 8 | 4 | 0 | 0 | 226 | 185 | 46 | 90 | 17145 | 1952273 | 334170 | 2.72 |
| green | 8 | 4 | 0 | 0 | 339 | 171 | 49 | 98 | 15020 | 2089318 | 312970 | 2.54 |
| refactor | 8 | 4 | 0 | 0 | 197 | 108 | 36 | 68 | 10548 | 1322293 | 311685 | 2.30 |
| diff | 2 | 1 | 0 | 0 | 93 | 38 | 11 | 20 | 3246 | 416291 | 80811 | 0.63 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 14 | 0 | 0 | 427 | 204 | 68 | 132 | 21340 | 2611627 | 528480 | 2.85 |
| developer | claude-opus-5-5 | 13 | 0 | 0 | 0 | 440 | 307 | 75 | 146 | 25652 | 3180414 | 541511 | 5.48 |

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
| With a ledger whose step 1 text contains the digit `2` and which has a step 2, a digits-only step argument `2` is read as a ledger index and writes the ref under `refs/veri/attempts/<issue>/2/` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 35 | 70 | 10632 | 1488480 | 240719 | 1.93 | 270 | unknown | 0/5 | nothing-left |  |  | full |
| A step argument equal to step N's full text writes under index N even when an earlier step's text contains that argument as a substring ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 32 | 62 | 10791 | 1281562 | 237494 | 1.87 | 268 | unknown | 0/5 | nothing-left |  |  | full |
| A step argument equal to step N's text with its trailing marks removed — ` ⟦criterion k⟧` and ` ⟂ refactor pending`, the way `next-pending-refactor.sh` prints a step and `supervise.sh` passes it on through `VERI_STEP` — still writes under index N | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 35 | 68 | 11771 | 1455043 | 242421 | 1.96 | 295 | unknown | 0/5 | nothing-left |  |  | full |
| A step argument that is only a substring of ledger steps' text, equal to none of them by index or full text, keeps today's fallback, the sanitised argument itself: the two-matches scenario of `test_main_names_the_ref_by_the_first_matching_step_and_keeps_the_argument_when_the_ledger_gives_none` changes from index 2 to `abcd` ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 105 | 29 | 56 | 9519 | 1138799 | 238191 | 1.82 | 265 | unknown | 0/5 | nothing-left |  |  | full |
| The existing contract cases in `tests/preserve-attempt.test.sh` and `tests/py/test_preserve_attempt.py` are unchanged except the first-match-substring scenario, which changes to the new rule ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 11 | 20 | 3246 | 416291 | 80811 | 0.63 | 118 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With a ledger whose step 1 text contains the digit `2` and which has a step 2, a digits-only step argument `2` is read as a ledger index and writes the ref under `refs/veri/attempts/<issue>/2/` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 45 | 0.56 |
| A step argument equal to step N's full text writes under index N even when an earlier step's text contains that argument as a substring ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 57 | 0.60 |
| A step argument equal to step N's text with its trailing marks removed — ` ⟦criterion k⟧` and ` ⟂ refactor pending`, the way `next-pending-refactor.sh` prints a step and `supervise.sh` passes it on through `VERI_STEP` — still writes under index N | 1 | 0/5 | nothing-left | PASS | 0 | 53 | 0.60 |
| A step argument that is only a substring of ledger steps' text, equal to none of them by index or full text, keeps today's fallback, the sanitised argument itself: the two-matches scenario of `test_main_names_the_ref_by_the_first_matching_step_and_keeps_the_argument_when_the_ledger_gives_none` changes from index 2 to `abcd` ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 42 | 0.54 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 2 | 2 | 0 | 1 | 0 | 2 | 2 | 2 | 0 | 0 | 2 | 1 | 0 | 1 | 0 | 15 | 2 | 0 | 1 | 0 | 2 | 2 |
| fast | 14 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 14 | 15 | 14 | 15 |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 143 | 278 | 46992 | 5792041 | 1069991 | 8.33 |
