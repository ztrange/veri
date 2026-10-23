### 📊 Metrics — issue 2208

Wall time for the issue: 499 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 5 planned.
Outcome: the run bailed — report-missing, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.50 over 34 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88336 |
| 2 | $0.02 | 88782 |
| 3 | $0.03 | 90654 |
| 4 | $0.02 | 91027 |
| 5 | $0.03 | 91946 |
| 6 | $0.02 | 92258 |
| 7 | $0.02 | 92559 |
| 8 | $0.02 | 93136 |
| 9 | $0.02 | 93785 |
| 10 | $0.03 | 95637 |
| 11 | $0.02 | 96059 |
| 12 | $0.03 | 97459 |
| 13 | $0.03 | 98643 |
| 14 | $0.02 | 99046 |
| 15 | $0.03 | 99857 |
| 16 | $0.02 | 100439 |
| 17 | $0.03 | 101319 |
| 18 | $0.03 | 102719 |
| 19 | $0.03 | 103563 |
| 20 | $0.02 | 103909 |
| 21 | $0.03 | 104771 |
| 22 | $0.03 | 105878 |
| 23 | $0.03 | 106807 |
| 24 | $0.03 | 107263 |
| 25 | $0.03 | 108000 |
| 26 | $0.03 | 108921 |
| 27 | $0.03 | 109844 |
| 28 | $0.03 | 110771 |
| 29 | $0.03 | 111609 |
| 30 | $0.03 | 112673 |
| 31 | $0.03 | 113847 |
| 32 | $0.03 | 114897 |
| 33 | $0.06 | 119030 |
| 34 | $0.03 | 119416 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 16 | 2 | 4 | 1031 | 30370 | 32105 | 0.09 |
| red | 3 | 2 | 0 | 0 | 126 | 60 | 13 | 26 | 4765 | 376082 | 61514 | 0.24 |
| green | 2 | 0 | 0 | 0 | 155 | 45 | 17 | 30 | 3413 | 463824 | 23696 | 0.14 |
| red-repair | 2 | 0 | 0 | 1 | 51 | 23 | 5 | 8 | 1605 | 110909 | 15046 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 92 | 40 | 8 | 16 | 2771 | 192638 | 50762 | 0.17 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 1 | 262 | 104 | 29 | 52 | 8043 | 788547 | 81599 | 0.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 126 | 0.24 |
| green | 0 | 0.00 | 155 | 0.14 |
| red-repair | 0 | 0.00 | 51 | 0.06 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| grade-prose reads a GRADES block naming every requirement ID exactly once but with two rows swapped out of file order, all PASS, as a PASS verdict: exit 0, a grading event with verdict=PASS, the unit's signature recorded in GRADED, as the same rows in file order would give ⟦criterion 1⟧ | 7 | 2 | 0 | 1 | 0 | 0 | 128 | 35 | 64 | 9783 | 950815 | 100256 | 0.44 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 24 | 20 | 23 | 13 |
| fast | 16 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 37 | 68 | 10814 | 981185 | 132361 | 0.54 |
