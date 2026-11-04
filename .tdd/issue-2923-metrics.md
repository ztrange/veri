### 📊 Metrics — issue 2923

Wall time for the issue: 3420 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 4 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.59 over 54 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90180 tokens, largest 168011 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90180 |
| 2 | $0.08 | 97429 |
| 3 | $0.04 | 99925 |
| 4 | $0.04 | 101823 |
| 5 | $0.03 | 103457 |
| 6 | $0.02 | 103761 |
| 7 | $0.02 | 104119 |
| 8 | $0.02 | 104370 |
| 9 | $0.02 | 104683 |
| 10 | $0.02 | 104936 |
| 11 | $0.02 | 105218 |
| 12 | $0.03 | 106088 |
| 13 | $0.04 | 109044 |
| 14 | $0.05 | 112947 |
| 15 | $0.04 | 115083 |
| 16 | $0.04 | 117594 |
| 17 | $0.03 | 118008 |
| 18 | $0.03 | 118907 |
| 19 | $0.03 | 119263 |
| 20 | $0.03 | 120002 |
| 21 | $0.03 | 120559 |
| 22 | $0.03 | 121078 |
| 23 | $0.03 | 121614 |
| 24 | $0.10 | 130818 |
| 25 | $0.03 | 131505 |
| 26 | $0.03 | 132194 |
| 27 | $0.03 | 132827 |
| 28 | $0.03 | 133356 |
| 29 | $0.03 | 134390 |
| 30 | $0.03 | 135311 |
| 31 | $0.03 | 135859 |
| 32 | $0.03 | 136614 |
| 33 | $0.03 | 137505 |
| 34 | $0.03 | 137992 |
| 35 | $0.04 | 139277 |
| 36 | $0.03 | 139862 |
| 37 | $0.04 | 140839 |
| 38 | $0.03 | 141268 |
| 39 | $0.03 | 141659 |
| 40 | $0.04 | 143021 |
| 41 | $0.04 | 144552 |
| 42 | $0.03 | 145254 |
| 43 | $0.04 | 146708 |
| 44 | $0.03 | 147275 |
| 45 | $0.06 | 151091 |
| 46 | $0.05 | 153228 |
| 47 | $0.04 | 154274 |
| 48 | $0.03 | 154593 |
| 49 | $0.04 | 155777 |
| 50 | $0.04 | 156924 |
| 51 | $0.06 | 159943 |
| 52 | $0.05 | 162554 |
| 53 | $0.04 | 163218 |
| 54 | $0.07 | 168011 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 1 | 2 | 1019 | 0 | 32403 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 154 | 39 | 10 | 20 | 2755 | 272863 | 49723 | 0.18 |
| red | 4 | 2 | 0 | 0 | 202 | 100 | 24 | 46 | 7492 | 686552 | 112218 | 0.42 |
| green | 4 | 0 | 0 | 0 | 301 | 116 | 35 | 60 | 10598 | 987382 | 105091 | 0.67 |
| exhausted | 1 | 0 | 0 | 0 | 42 | 9 | 3 | 6 | 835 | 78976 | 14318 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 230 | 70 | 14 | 28 | 4766 | 357890 | 99512 | 0.33 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 139 | 79 | 21 | 40 | 6500 | 601525 | 94832 | 0.36 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 343 | 125 | 38 | 66 | 11433 | 1066358 | 119409 | 0.78 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 202 | 0.42 |
| green | 0 | 0.00 | 301 | 0.67 |
| exhausted | 0 | 0.00 | 42 | 0.10 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The older cases in skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py that compare build-develop-prompt.sh's usage line verbatim take that line from the module's own USAGE rather than from a literal phase list, so the usage line may gain a phase without turning them red; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 10 | 20 | 2755 | 272863 | 49723 | 0.18 | 553 | n/a | n/a | n/a |  |  | full |
| build-develop-prompt.sh called with no arguments exits 2 and prints a usage line on stderr whose phase list names dual-stub and still names beside ⟦criterion 1⟧ | 9 | 2 | 0 | 0 | 0 | 0 | 225 | 62 | 112 | 18925 | 1752910 | 231627 | 1.20 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 32 | 29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 6 | 5 | 6 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 5 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | 3 | 4 | 5 | 5 | 5 | 6 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 4 | 8 | 4 | 5 | 3 | 3 | 3 | 4 | 3 | 4 | 4 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 73 | 134 | 22699 | 2025773 | 313753 | 4.06 (estimate) |
