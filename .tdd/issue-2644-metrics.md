### 📊 Metrics — issue 2644

Wall time for the issue: 1140 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: unknown of 2 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.01 over 43 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 85316 tokens, largest 145180 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 85316 |
| 2 | $0.07 | 91954 |
| 3 | $0.03 | 93224 |
| 4 | $0.03 | 94837 |
| 5 | $0.02 | 95160 |
| 6 | $0.02 | 95840 |
| 7 | $0.02 | 96185 |
| 8 | $0.02 | 96445 |
| 9 | $0.02 | 96673 |
| 10 | $0.03 | 97511 |
| 11 | $0.02 | 97795 |
| 12 | $0.03 | 99299 |
| 13 | $0.06 | 104155 |
| 14 | $0.04 | 107112 |
| 15 | $0.03 | 108007 |
| 16 | $0.02 | 108322 |
| 17 | $0.03 | 109069 |
| 18 | $0.03 | 109622 |
| 19 | $0.03 | 110386 |
| 20 | $0.03 | 111626 |
| 21 | $0.03 | 112269 |
| 22 | $0.03 | 113243 |
| 23 | $0.03 | 114035 |
| 24 | $0.09 | 122144 |
| 25 | $0.04 | 123674 |
| 26 | $0.04 | 125968 |
| 27 | $0.03 | 127020 |
| 28 | $0.03 | 127404 |
| 29 | $0.03 | 128047 |
| 30 | $0.03 | 128729 |
| 31 | $0.03 | 129836 |
| 32 | $0.03 | 130444 |
| 33 | $0.04 | 131618 |
| 34 | $0.05 | 134361 |
| 35 | $0.03 | 134770 |
| 36 | $0.03 | 135059 |
| 37 | $0.03 | 135220 |
| 38 | $0.04 | 136494 |
| 39 | $0.04 | 137628 |
| 40 | $0.03 | 138069 |
| 41 | $0.04 | 139720 |
| 42 | $0.03 | 140388 |
| 43 | $0.07 | 145180 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 1 | 2 | 1003 | 0 | 31800 | 0.09 |
| red | 4 | 1 | 1 | 0 | 171 | 104 | 20 | 38 | 9280 | 552825 | 109039 | 0.60 |
| green | 3 | 0 | 0 | 0 | 129 | 72 | 16 | 32 | 6186 | 508783 | 77406 | 0.56 |
| exhausted | 1 | 0 | 0 | 0 | 11 | 8 | 2 | 4 | 815 | 46743 | 12500 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 2 | 1 | 0 | 90 | 40 | 8 | 14 | 3412 | 156042 | 61907 | 0.20 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 234 | 154 | 31 | 62 | 13872 | 952309 | 168838 | 1.13 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 171 | 0.60 |
| green | 0 | 0.00 | 129 | 0.56 |
| exhausted | 0 | 0.00 | 11 | 0.09 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A shared test helper in conftest.py starts supervise.sh with Popen in a session of its own and kills the supervisor's process group in a finally, so a case whose leaf outlives the case's wait (its communicate timeout raised) leaves no supervisor or leaf process alive afterwards; pinned by a medium case, process-marked, in test_supervise_process.py that makes the leaf outlive the wait and asserts the supervisor's pid is gone after the helper exits; test-only, no production change ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 1⟧ | 8 | 1 | 1 | 0 | 0 | 0 | 184 | 38 | 74 | 16281 | 1108351 | 198945 | 1.24 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 3 | 7 | 10 |
| fast | 27 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 39 | 76 | 17284 | 1108351 | 230745 | 3.33 (estimate) |
