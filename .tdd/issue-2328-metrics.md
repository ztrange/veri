### 📊 Metrics — issue 2328

Wall time for the issue: 1232 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2394.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.94 over 49 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87646 tokens, largest 128674 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87646 |
| 2 | $0.02 | 87984 |
| 3 | $0.02 | 88848 |
| 4 | $0.03 | 90761 |
| 5 | $0.02 | 91057 |
| 6 | $0.02 | 91469 |
| 7 | $0.02 | 91885 |
| 8 | $0.02 | 92262 |
| 9 | $0.02 | 93063 |
| 10 | $0.04 | 96234 |
| 11 | $0.03 | 97425 |
| 12 | $0.02 | 98060 |
| 13 | $0.02 | 98412 |
| 14 | $0.03 | 99123 |
| 15 | $0.02 | 99671 |
| 16 | $0.03 | 100338 |
| 17 | $0.02 | 100823 |
| 18 | $0.03 | 102174 |
| 19 | $0.03 | 103141 |
| 20 | $0.03 | 103928 |
| 21 | $0.03 | 104683 |
| 22 | $0.02 | 105173 |
| 23 | $0.03 | 105904 |
| 24 | $0.03 | 106875 |
| 25 | $0.03 | 107935 |
| 26 | $0.03 | 108810 |
| 27 | $0.03 | 109687 |
| 28 | $0.03 | 110443 |
| 29 | $0.03 | 111121 |
| 30 | $0.03 | 112124 |
| 31 | $0.03 | 112963 |
| 32 | $0.03 | 114162 |
| 33 | $0.04 | 116599 |
| 34 | $0.03 | 117399 |
| 35 | $0.03 | 117704 |
| 36 | $0.03 | 118214 |
| 37 | $0.03 | 118734 |
| 38 | $0.03 | 119029 |
| 39 | $0.03 | 119402 |
| 40 | $0.03 | 119913 |
| 41 | $0.03 | 120329 |
| 42 | $0.05 | 123389 |
| 43 | $0.03 | 124367 |
| 44 | $0.03 | 125145 |
| 45 | $0.04 | 126423 |
| 46 | $0.03 | 127134 |
| 47 | $0.03 | 127646 |
| 48 | $0.03 | 128132 |
| 49 | $0.03 | 128674 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 7 | 1 | 2 | 733 | 0 | 31003 | 0.08 |
| red | 3 | 1 | 0 | 0 | 50 | 38 | 12 | 22 | 5084 | 306777 | 76194 | 0.27 |
| green | 2 | 1 | 0 | 0 | 63 | 19 | 9 | 14 | 2143 | 191502 | 30961 | 0.12 |
| refactor | 1 | 0 | 0 | 0 | 7 | 5 | 3 | 4 | 517 | 48194 | 14975 | 0.05 |
| pin | 1 | 1 | 0 | 0 | 12 | 8 | 3 | 6 | 889 | 76510 | 14149 | 0.05 |
| cover | 1 | 0 | 0 | 0 | 13 | 8 | 4 | 6 | 714 | 59169 | 31007 | 0.09 |
| predicate | 1 | 0 | 0 | 0 | 7 | 5 | 3 | 6 | 426 | 75870 | 12074 | 0.04 |
| structural | 1 | 0 | 0 | 0 | 13 | 10 | 5 | 8 | 1081 | 106942 | 13230 | 0.05 |
| transform | 1 | 1 | 0 | 0 | 11 | 9 | 3 | 6 | 887 | 57049 | 29384 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 76 | 41 | 13 | 26 | 4239 | 289124 | 105149 | 0.33 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 109 | 68 | 30 | 48 | 8235 | 632889 | 147828 | 0.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When the taken:<lane> lookup answers 404 and gh label create fails with "already exists", the claim (unlabel-issue.sh) adds taken:<lane> to the issue and exits 0 — a small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py faking gh at the github.py boundary ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 47 | 20 | 32 | 5479 | 428361 | 102286 | 0.35 | 213 | unknown | 0/5 | structural-owed |  |  | full |
| When the taken:<lane> lookup answers 404 and gh label create fails with anything other than "already exists", the claim still exits 2 and adds no label to the issue — a small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py faking gh at the github.py boundary ⟦criterion 1⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 55 | 22 | 40 | 6262 | 493652 | 119688 | 0.41 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the taken:<lane> lookup answers 404 and gh label create fails with "already exists", the claim (unlabel-issue.sh) adds taken:<lane> to the issue and exits 0 — a small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py faking gh at the github.py boundary ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 7 | 0.05 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 0 |
| fast | 17 | 17 |  |  |  |  |  |  |
| target | 1 | 1 | 1 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 74 | 12474 | 922013 | 252977 | 0.85 |
