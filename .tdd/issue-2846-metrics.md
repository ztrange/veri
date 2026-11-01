### 📊 Metrics — issue 2846

Wall time for the issue: 1344 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2849.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.77 over 30 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87723 tokens, largest 150084 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87723 |
| 2 | $0.07 | 94726 |
| 3 | $0.03 | 96080 |
| 4 | $0.04 | 98380 |
| 5 | $0.02 | 99008 |
| 6 | $0.03 | 99660 |
| 7 | $0.02 | 100047 |
| 8 | $0.05 | 104088 |
| 9 | $0.04 | 106752 |
| 10 | $0.04 | 109263 |
| 11 | $0.04 | 111247 |
| 12 | $0.03 | 112091 |
| 13 | $0.03 | 113643 |
| 14 | $0.03 | 114504 |
| 15 | $0.09 | 122625 |
| 16 | $0.04 | 124722 |
| 17 | $0.04 | 126259 |
| 18 | $0.05 | 128987 |
| 19 | $0.05 | 131647 |
| 20 | $0.03 | 132402 |
| 21 | $0.04 | 134706 |
| 22 | $0.05 | 137185 |
| 23 | $0.04 | 138465 |
| 24 | $0.04 | 140012 |
| 25 | $0.04 | 141070 |
| 26 | $0.06 | 144571 |
| 27 | $0.05 | 147482 |
| 28 | $0.04 | 148945 |
| 29 | $0.03 | 149229 |
| 30 | $0.04 | 150084 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 975 | 17154 | 15402 | 0.05 |
| red | 6 | 2 | 0 | 0 | 216 | 72 | 27 | 48 | 8492 | 714533 | 109000 | 0.43 |
| green | 6 | 2 | 1 | 0 | 353 | 61 | 26 | 46 | 6470 | 651558 | 103487 | 0.49 |
| refactor | 2 | 0 | 0 | 0 | 14 | 9 | 6 | 8 | 763 | 98640 | 32834 | 0.10 |
| pin | 2 | 2 | 0 | 0 | 39 | 19 | 6 | 12 | 1970 | 157329 | 30019 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 360 | 69 | 22 | 44 | 7032 | 588199 | 113706 | 0.41 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 169 | 79 | 33 | 56 | 9239 | 836227 | 125587 | 0.49 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 105 | 21 | 11 | 16 | 2399 | 214788 | 51449 | 0.28 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 240 | 0.37 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Output with a multi-line `REASON:` before `VERDICT: REJECT` and nothing after it exits 1 and prints every line of the reason, in order; free-form text before the `REASON:` line stays out of the printed reason (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 69 | 29 | 48 | 7456 | 675630 | 122650 | 0.55 | 456 | 1/2 | 0/5 | nothing-left |  |  | full |
| With `MISSING_TEST: <behaviour>` before a multi-line `REASON:` block and `VERDICT: REJECT` after it, the output holds the `MISSING_TEST:` line intact followed by the whole block (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 2940 | 233530 | 33684 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| A `FLAGS:` line between a multi-line `REASON:` block and `VERDICT: REJECT` is not printed as part of the reason, while the block's other lines still are (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 41 | 20 | 36 | 4307 | 511582 | 84163 | 0.30 | 267 | unknown | 0/5 | nothing-left |  |  | full |
| Reason text after the verdict keeps working as today: with a multi-line `REASON:` block before `VERDICT: REJECT` and reason text after it, only the text after the verdict is printed (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦added⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 8 | 14 | 2992 | 201318 | 34843 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Output with a multi-line `REASON:` before `VERDICT: REJECT` and nothing after it exits 1 and prints every line of the reason, in order; free-form text before the `REASON:` line stays out of the printed reason (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |
| A `FLAGS:` line between a multi-line `REASON:` block and `VERDICT: REJECT` is not printed as part of the reason, while the block's other lines still are (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 6 | 3 | 6 | 3 | 5 | 3 | 3 | 3 | 3 | 4 | 4 |
| fast | 31 | 37 | 37 | 42 | 36 | 36 |  |  |  |  |  |  |
| target | 3 | 4 | 3 | 3 | 4 | 4 | 4 | 3 | 3 | 3 | 3 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 66 | 116 | 18670 | 1639214 | 290742 | 2.95 (estimate) |
