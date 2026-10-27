### 📊 Metrics — issue 2443

Wall time for the issue: 1116 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2574.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.22 over 58 turns, in 2 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88680 tokens, largest 120735 tokens
Conductor context: first turn 88715 tokens, largest 132514 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88680 |
| 2 | $0.05 | 90657 |
| 3 | $0.04 | 92604 |
| 4 | $0.03 | 92939 |
| 5 | $0.04 | 93310 |
| 6 | $0.03 | 93883 |
| 7 | $0.04 | 94231 |
| 8 | $0.03 | 94798 |
| 9 | $0.04 | 96610 |
| 10 | $0.04 | 97629 |
| 11 | $0.07 | 101478 |
| 12 | $0.05 | 104046 |
| 13 | $0.04 | 105227 |
| 14 | $0.04 | 106402 |
| 15 | $0.06 | 109146 |
| 16 | $0.04 | 109955 |
| 17 | $0.04 | 111202 |
| 18 | $0.05 | 112749 |
| 19 | $0.07 | 117851 |
| 20 | $0.05 | 119372 |
| 21 | $0.04 | 120735 |
| 22 | $0.57 | 88715 |
| 23 | $0.04 | 91032 |
| 24 | $0.03 | 92970 |
| 25 | $0.02 | 93583 |
| 26 | $0.02 | 94025 |
| 27 | $0.02 | 94727 |
| 28 | $0.02 | 95347 |
| 29 | $0.05 | 99515 |
| 30 | $0.03 | 101009 |
| 31 | $0.03 | 101794 |
| 32 | $0.02 | 102004 |
| 33 | $0.03 | 102632 |
| 34 | $0.05 | 106018 |
| 35 | $0.03 | 107530 |
| 36 | $0.03 | 108247 |
| 37 | $0.03 | 108808 |
| 38 | $0.04 | 110514 |
| 39 | $0.03 | 111155 |
| 40 | $0.03 | 111690 |
| 41 | $0.07 | 117875 |
| 42 | $0.03 | 118658 |
| 43 | $0.03 | 119397 |
| 44 | $0.03 | 120509 |
| 45 | $0.05 | 123498 |
| 46 | $0.03 | 124226 |
| 47 | $0.03 | 124462 |
| 48 | $0.03 | 125018 |
| 49 | $0.03 | 125726 |
| 50 | $0.03 | 126652 |
| 51 | $0.03 | 127551 |
| 52 | $0.04 | 129545 |
| 53 | $0.03 | 130376 |
| 54 | $0.03 | 131113 |
| 55 | $0.03 | 131367 |
| 56 | $0.03 | 131579 |
| 57 | $0.03 | 132095 |
| 58 | $0.03 | 132514 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 28 | 5 | 10 | 2786 | 122710 | 53859 | 0.17 |
| diff | 4 | 2 | 0 | 0 | 161 | 60 | 18 | 34 | 4484 | 468680 | 79603 | 0.29 |
| red | 2 | 0 | 0 | 0 | 43 | 33 | 8 | 16 | 3636 | 255261 | 44213 | 0.17 |
| pin | 2 | 2 | 0 | 0 | 62 | 22 | 6 | 12 | 1695 | 161776 | 31769 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 180 | 76 | 18 | 36 | 6187 | 475113 | 115716 | 0.40 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 118 | 67 | 19 | 36 | 6414 | 533314 | 93728 | 0.35 |

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
| GRADER_INSTRUCTIONS in skills/tdd/scripts/veri/grade_prose.py gains one rule: a requirement row naming a concrete artefact — a file, a section heading or an identifier — is FAIL when the prose does not name that artefact, substance alone not discharging a named reference; no other change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 10 | 18 | 2372 | 241562 | 48557 | 0.17 | 132 | n/a | n/a | n/a |  |  | full |
| The prompt grade_prose renders for a unit (grade_prose.prompt) states that a requirement row naming a file, a section heading or an identifier is FAIL when the prose does not name it, pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py asserting that rule in the rendered prompt ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 7 | 14 | 2676 | 208857 | 38421 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| GRADER_INSTRUCTIONS in skills/tdd/scripts/veri/grade_prose.py states that a requirement row naming no artefact passes on its meaning alone, in any wording, so a unit wording such a row differently keeps PASS and the artefact rule is not substring matching; no other change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 8 | 16 | 2112 | 227118 | 31046 | 0.12 | 111 | n/a | n/a | n/a |  |  | full |
| The prompt grade_prose renders for a unit states that a requirement row naming no artefact passes on its meaning alone, in any wording, pinned by a small in-process case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py asserting that text in the rendered prompt ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 7 | 14 | 2655 | 208180 | 37561 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 17 | 17 |  |  |
| affected | 1 | 2 | 1 | 2 |
| target | 1 | 1 | 17 | 16 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 37 | 72 | 12601 | 1008427 | 209444 | 0.75 |
