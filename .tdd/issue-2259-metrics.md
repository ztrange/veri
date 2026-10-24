### 📊 Metrics — issue 2259

Wall time for the issue: 1024 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2276.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.38 over 29 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89190 |
| 2 | $0.02 | 89561 |
| 3 | $0.03 | 91393 |
| 4 | $0.02 | 91621 |
| 5 | $0.03 | 92467 |
| 6 | $0.02 | 92782 |
| 7 | $0.02 | 93074 |
| 8 | $0.02 | 93624 |
| 9 | $0.03 | 95057 |
| 10 | $0.03 | 96638 |
| 11 | $0.03 | 97844 |
| 12 | $0.03 | 98674 |
| 13 | $0.03 | 99469 |
| 14 | $0.02 | 100032 |
| 15 | $0.02 | 100598 |
| 16 | $0.03 | 101768 |
| 17 | $0.03 | 102544 |
| 18 | $0.07 | 108279 |
| 19 | $0.03 | 108953 |
| 20 | $0.03 | 109717 |
| 21 | $0.03 | 110790 |
| 22 | $0.04 | 113313 |
| 23 | $0.03 | 114045 |
| 24 | $0.02 | 114266 |
| 25 | $0.03 | 114954 |
| 26 | $0.03 | 115299 |
| 27 | $0.03 | 115584 |
| 28 | $0.03 | 115979 |
| 29 | $0.03 | 116466 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 29 | 17 | 3 | 6 | 1998 | 47470 | 44316 | 0.14 |
| diff | 2 | 1 | 0 | 0 | 269 | 45 | 17 | 32 | 5308 | 468127 | 51413 | 0.23 |
| red | 1 | 0 | 0 | 0 | 44 | 21 | 5 | 10 | 2586 | 157302 | 21310 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 33 | 10 | 3 | 6 | 940 | 75175 | 13362 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 3 | 1 | 0 | 104 | 34 | 9 | 18 | 3828 | 197777 | 71300 | 0.24 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 271 | 59 | 19 | 36 | 7004 | 550297 | 59101 | 0.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| verify-green.md's check 4 (only code a test requires) tells the verifier to probe every branch, option, flag, parameter and guard the step's diff added before answering, not stopping at the first whose removal leaves every test green, and to name each such item in REASON:, one per line; the copy-remove-rerun-restore procedure and the restore check stay as written, build-verify-prompt.sh takes no new input, and any case pinning the old check-4 text verbatim is updated in the same commit ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 17 | 32 | 5308 | 468127 | 51413 | 0.23 | 331 | n/a | n/a | n/a |  |  | full |
| The prompt build-verify-prompt.sh renders for the green phase tells the verifier to probe every branch, option, flag, parameter and guard the step's diff added before answering, and to name in REASON: each one whose removal left every test green, not only the first — pinned by a small unit case on the rendered prompt in skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 8 | 16 | 3526 | 232477 | 34672 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 30 | 23 | 21 | 25 | 21 |
| affected | 14 | 18 | 20 | 11 | 10 |
| target | 10 | 10 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 28 | 54 | 10832 | 748074 | 130401 | 0.51 |
