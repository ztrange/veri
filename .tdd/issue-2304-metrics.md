### 📊 Metrics — issue 2304

Wall time for the issue: 546 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2385.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.32 over 35 turns, in 2 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 93168 tokens, largest 103711 tokens
Conductor context: first turn 93170 tokens, largest 124962 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 93168 |
| 2 | $0.03 | 94822 |
| 3 | $0.03 | 96638 |
| 4 | $0.02 | 96966 |
| 5 | $0.02 | 97401 |
| 6 | $0.02 | 97996 |
| 7 | $0.02 | 98664 |
| 8 | $0.05 | 102372 |
| 9 | $0.03 | 103103 |
| 10 | $0.03 | 103711 |
| 11 | unpriced | 0 |
| 12 | $0.61 | 93170 |
| 13 | $0.03 | 94206 |
| 14 | $0.03 | 96087 |
| 15 | $0.03 | 96827 |
| 16 | $0.06 | 102031 |
| 17 | $0.02 | 102448 |
| 18 | $0.02 | 102754 |
| 19 | $0.02 | 103031 |
| 20 | $0.03 | 103808 |
| 21 | $0.03 | 104507 |
| 22 | $0.02 | 105017 |
| 23 | $0.13 | 118154 |
| 24 | $0.04 | 120665 |
| 25 | $0.03 | 121230 |
| 26 | $0.03 | 121642 |
| 27 | $0.03 | 121867 |
| 28 | $0.03 | 122380 |
| 29 | $0.03 | 123040 |
| 30 | $0.03 | 123597 |
| 31 | $0.03 | 123865 |
| 32 | $0.03 | 124111 |
| 33 | $0.03 | 124559 |
| 34 | $0.03 | 124962 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 661 | 0 | 31324 | 0.08 |
| red | 1 | 0 | 0 | 0 | 41 | 35 | 8 | 16 | 5018 | 273842 | 44739 | 0.19 |
| pin | 1 | 1 | 0 | 0 | 15 | 12 | 4 | 8 | 1327 | 94591 | 34792 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 22 | 17 | 5 | 10 | 1988 | 94591 | 66116 | 0.19 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 41 | 35 | 8 | 16 | 5018 | 273842 | 44739 | 0.19 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With VERI_NO_VERDICT_RETRIES=3, a grader stub returning a well-formed GRADES block that grades one requirement FAIL is launched exactly once, and grade-prose.sh exits 1 naming that requirement; pinned by a small in-process case in tests/py/unit/test_grade_prose.py (no production change expected; the case must go red if keeps_protocol rejects a FAIL) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 12 | 24 | 6345 | 368433 | 79531 | 0.30 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| affected | 1 | 1 |
| target | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 13 | 26 | 7006 | 368433 | 110855 | 0.38 |
