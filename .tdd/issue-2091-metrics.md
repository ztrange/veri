### 📊 Metrics — issue 2091

Wall time for the issue: 3121 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2102.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.62 over 52 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86041 |
| 2 | $0.04 | 87421 |
| 3 | $0.04 | 89346 |
| 4 | $0.02 | 89693 |
| 5 | $0.03 | 90130 |
| 6 | $0.03 | 90427 |
| 7 | $0.03 | 90803 |
| 8 | $0.03 | 91229 |
| 9 | $0.02 | 91602 |
| 10 | $0.03 | 92137 |
| 11 | $0.04 | 92810 |
| 12 | $0.03 | 93753 |
| 13 | $0.04 | 95180 |
| 14 | $0.03 | 95921 |
| 15 | $0.55 | 86040 |
| 16 | $0.03 | 87417 |
| 17 | $0.03 | 89337 |
| 18 | $0.02 | 89681 |
| 19 | $0.02 | 90226 |
| 20 | $0.02 | 90625 |
| 21 | $0.02 | 91394 |
| 22 | $0.02 | 91864 |
| 23 | $0.03 | 92694 |
| 24 | $0.02 | 93263 |
| 25 | $0.02 | 93654 |
| 26 | $0.02 | 94012 |
| 27 | $0.04 | 96112 |
| 28 | $0.02 | 96707 |
| 29 | $0.02 | 97354 |
| 30 | $0.04 | 99592 |
| 31 | $0.03 | 100478 |
| 32 | $0.03 | 101171 |
| 33 | $0.07 | 106798 |
| 34 | $0.03 | 107872 |
| 35 | $0.03 | 108608 |
| 36 | $0.03 | 109235 |
| 37 | $0.03 | 110031 |
| 38 | $0.03 | 110574 |
| 39 | $0.03 | 111854 |
| 40 | $0.03 | 112811 |
| 41 | $0.03 | 113627 |
| 42 | $0.07 | 118929 |
| 43 | $0.03 | 119397 |
| 44 | $0.03 | 120077 |
| 45 | $0.03 | 120937 |
| 46 | $0.03 | 121335 |
| 47 | $0.03 | 121663 |
| 48 | $0.03 | 122083 |
| 49 | $0.03 | 122753 |
| 50 | $0.03 | 123455 |
| 51 | $0.03 | 124058 |
| 52 | $0.03 | 124618 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 2 | 4 | 804 | 30202 | 30768 | 0.09 |
| prose | 4 | 0 | 0 | 0 | 59 | 45 | 4 | 8 | 6357 | 4434 | 44394 | 0.18 |
| skill-edit | 1 | 0 | 0 | 0 | 10 | 7 | 3 | 6 | 705 | 75490 | 11743 | 0.04 |
| diff | 2 | 1 | 0 | 0 | 1159 | 39 | 18 | 36 | 3801 | 482094 | 65861 | 0.25 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 289 | 26 | 10 | 20 | 2421 | 240198 | 64174 | 0.21 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 881 | 20 | 10 | 20 | 2184 | 272098 | 32455 | 0.13 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `specs/utility-skills.md`'s principles table (section `## P: principles every operator skill obeys`) gains a P14 row directly after its P13 row, byte-identical to the P14 row of `operator/REQUIREMENTS.md`, and nothing else in the file changes; `make unit` stays green; this step adds no test ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 18 | 36 | 3801 | 482094 | 65861 | 0.25 | 1220 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| fast | 18 |  |
| affected | 197 | 183 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 27 | 54 | 11667 | 592220 | 152766 | 0.56 |
