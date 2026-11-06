### 📊 Metrics — issue 3123

Wall time for the issue: 3008 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3127.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.51 over 32 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 91837 tokens, largest 120011 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 91837 |
| 2 | $0.08 | 99173 |
| 3 | $0.03 | 100349 |
| 4 | $0.04 | 102254 |
| 5 | $0.04 | 104402 |
| 6 | $0.02 | 104720 |
| 7 | $0.02 | 105083 |
| 8 | $0.02 | 105346 |
| 9 | $0.02 | 105591 |
| 10 | $0.03 | 106091 |
| 11 | $0.02 | 106358 |
| 12 | $0.03 | 107017 |
| 13 | $0.03 | 108620 |
| 14 | $0.03 | 109552 |
| 15 | $0.03 | 110006 |
| 16 | $0.03 | 110824 |
| 17 | $0.02 | 111173 |
| 18 | $0.03 | 111758 |
| 19 | $0.03 | 112293 |
| 20 | $0.03 | 113444 |
| 21 | $0.03 | 114258 |
| 22 | $0.03 | 115165 |
| 23 | $0.03 | 115814 |
| 24 | $0.03 | 116475 |
| 25 | $0.03 | 116977 |
| 26 | $0.03 | 117240 |
| 27 | $0.03 | 117503 |
| 28 | $0.03 | 117773 |
| 29 | $0.03 | 118338 |
| 30 | $0.03 | 119151 |
| 31 | $0.03 | 119721 |
| 32 | $0.03 | 120011 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 2 | 4 | 845 | 30807 | 32351 | 0.09 |
| prose | 5 | 0 | 0 | 0 | 60 | 41 | 5 | 10 | 6285 | 15332 | 42001 | 0.17 |
| skill-edit | 1 | 0 | 0 | 0 | 15 | 10 | 5 | 8 | 1330 | 100240 | 37208 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 11 | 7 | 2 | 4 | 845 | 30807 | 32351 | 0.09 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/tdd/scripts/prompts/develop-revise.md: a rendered revise prompt for a frozen-test phase gives the exact command `tests-frozen.sh check-earlier .tdd/issue-<n>.md --step <next-unchecked step>` naming the run's own ledger, never `.tdd/plan-ledger.md` (DV8) ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 40 | 9 | 16 | 5872 | 114923 | 68057 | 0.24 | 100 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 12 | 22 | 8460 | 146379 | 111560 | 1.89 (estimate) |
