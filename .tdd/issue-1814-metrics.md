### 📊 Metrics — issue 1814

Wall time for the issue: 1046 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1845.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 770 | 0 | 29925 | 0.08 |
| diff | 4 | 2 | 0 | 0 | 148 | 89 | 34 | 68 | 7700 | 994397 | 80242 | 0.38 |
| red | 1 | 0 | 0 | 0 | 37 | 32 | 8 | 16 | 2957 | 268322 | 21691 | 0.11 |
| pin | 1 | 1 | 0 | 0 | 16 | 13 | 5 | 10 | 1243 | 138054 | 14286 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 84 | 56 | 19 | 38 | 5259 | 499728 | 72406 | 0.28 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 126 | 84 | 29 | 58 | 7411 | 901045 | 73738 | 0.35 |

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
| The verify-red and verify-pin prompts carry a check that every test case the step's text names (a "separate case", a second behaviour it asks to be pinned) is added by Red's change, and REJECT naming the missing case when Red's change adds no case for it; the prompt text and every verbatim or checksum pin it moves land in one commit ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 19 | 38 | 4638 | 571270 | 53036 | 0.24 | 136 | n/a | n/a | n/a |  |  | full |
| That check's REJECT is conditioned only on a named case being absent: a Red whose change adds a case for every case the step's text names, or a step whose text names no separate case, is judged by the verify-red and verify-pin checks exactly as today ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 15 | 30 | 3062 | 423127 | 27206 | 0.14 | 101 | n/a | n/a | n/a |  |  | full |
| A case in tests/py/unit/test_build_verify_prompt.py builds the verify-red prompt, and the verify-pin prompt, for a step whose text demands two behaviours (one of them as a separate case) and asserts the rendered prompt instructs the verifier to REJECT, naming the missing case, a Red that pins only one of them; a small unmarked pytest case, no process ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 13 | 26 | 4200 | 406376 | 35977 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 5 | 5 | 5 |  |  |  |
| affected | 3 | 0 | 3 | 0 | 3 | 1 |
| target | 0 | 0 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 48 | 96 | 12670 | 1400773 | 146144 | 0.63 |
