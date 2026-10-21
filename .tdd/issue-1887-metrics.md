### 📊 Metrics — issue 1887

Wall time for the issue: 1806 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1946.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.06 over 51 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84677 |
| 2 | $0.02 | 84999 |
| 3 | $0.02 | 85774 |
| 4 | $0.03 | 87729 |
| 5 | $0.02 | 88042 |
| 6 | $0.02 | 88456 |
| 7 | $0.02 | 88817 |
| 8 | $0.02 | 89143 |
| 9 | $0.02 | 89761 |
| 10 | $0.02 | 90592 |
| 11 | $0.04 | 92725 |
| 12 | $0.02 | 93476 |
| 13 | $0.02 | 94046 |
| 14 | $0.04 | 96278 |
| 15 | $0.07 | 102492 |
| 16 | $0.03 | 103975 |
| 17 | $0.02 | 104280 |
| 18 | $0.03 | 105244 |
| 19 | $0.03 | 105836 |
| 20 | $0.03 | 106378 |
| 21 | $0.03 | 106957 |
| 22 | $0.03 | 108056 |
| 23 | $0.03 | 108848 |
| 24 | $0.04 | 111294 |
| 25 | $0.03 | 111988 |
| 26 | $0.02 | 112290 |
| 27 | $0.03 | 113056 |
| 28 | $0.03 | 114249 |
| 29 | $0.03 | 114603 |
| 30 | $0.03 | 115332 |
| 31 | $0.03 | 116604 |
| 32 | $0.03 | 118018 |
| 33 | $0.03 | 118903 |
| 34 | $0.03 | 119690 |
| 35 | $0.03 | 120620 |
| 36 | $0.05 | 123428 |
| 37 | $0.03 | 124074 |
| 38 | $0.03 | 124955 |
| 39 | $0.04 | 126352 |
| 40 | $0.03 | 127207 |
| 41 | $0.03 | 128263 |
| 42 | $0.03 | 128879 |
| 43 | $0.03 | 129374 |
| 44 | $0.03 | 129667 |
| 45 | $0.03 | 130154 |
| 46 | $0.03 | 130710 |
| 47 | $0.03 | 131722 |
| 48 | $0.03 | 132055 |
| 49 | $0.03 | 133050 |
| 50 | $0.03 | 133509 |
| 51 | $0.03 | 133922 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 18 | 5 | 10 | 1773 | 141258 | 17175 | 0.07 |
| red | 4 | 1 | 0 | 0 | 163 | 71 | 23 | 46 | 7250 | 709477 | 71361 | 0.32 |
| pin | 2 | 2 | 0 | 0 | 37 | 21 | 7 | 14 | 1906 | 177912 | 25017 | 0.10 |
| green | 2 | 1 | 0 | 0 | 84 | 29 | 10 | 20 | 2163 | 278513 | 27623 | 0.12 |
| refactor | 2 | 1 | 0 | 0 | 35 | 13 | 5 | 10 | 884 | 121966 | 25608 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 126 | 62 | 21 | 42 | 5706 | 543974 | 81469 | 0.32 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 215 | 90 | 29 | 58 | 8270 | 885152 | 85315 | 0.38 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `leaf-role.sh grade-prose` prints the role line `VERI_ACTOR=grader VERI_PHASE=prose VERI_ATTEMPT=1` and exits 0, nothing on stderr, a grader role distinct from developer and verifier (small in-process case; the unknown-leading-word diagnostic text stays exactly as it is) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 9 | 18 | 3234 | 258366 | 31745 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| `harvest-usage.sh` recognises the grader leaf's name `grade-prose`: the usage event it appends for that leaf carries actor `grader` and phase `prose`, and it prints nothing about leaf roles on stderr (small in-process case; the unknown-leading-word diagnostic text stays exactly as it is) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 64 | 24 | 48 | 5198 | 657830 | 83863 | 0.33 | 247 | unknown | 0/5 | nothing-left |  |  | full |
| A graded run of `grade-prose.sh` with a stub claude, launched through `supervise.sh`, exits 0 and prints nothing about leaf roles (no `leaf-role:` line) on stderr (process case) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 12 | 24 | 3771 | 371672 | 34001 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `harvest-usage.sh` recognises the grader leaf's name `grade-prose`: the usage event it appends for that leaf carries actor `grader` and phase `prose`, and it prints nothing about leaf roles on stderr (small in-process case; the unknown-leading-word diagnostic text stays exactly as it is) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 2 | 2 | 1 | 1 | 2 | 65 |
| target | 1 | 2 | 2 | 3 | 3 |  |  |  |
| fast | 15 | 14 | 15 | 15 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 100 | 13976 | 1429126 | 166784 | 0.70 |
