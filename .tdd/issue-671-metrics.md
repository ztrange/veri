### 📊 Metrics — issue 671

Wall time for the issue: 9581 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/673.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 11 | 2 | 4 | 1099 | 59928 | 39954 | 0.35 |
| red | 21 | 7 | 1 | 0 | 1113 | 889 | 191 | 376 | 78672 | 10149022 | 996147 | 11.57 |
| green | 16 | 7 | 1 | 0 | 3321 | 596 | 153 | 304 | 55077 | 7604068 | 661059 | 8.45 |
| refactor | 14 | 7 | 0 | 0 | 758 | 255 | 75 | 148 | 22246 | 3237158 | 597225 | 5.87 |
| pin | 4 | 4 | 0 | 0 | 157 | 100 | 25 | 50 | 9892 | 1105380 | 169615 | 1.78 |
| rebase | 2 | 1 | 0 | 0 | 1190 | 36 | 11 | 22 | 3429 | 477431 | 81407 | 0.82 |
| structural | 4 | 0 | 0 | 0 | 162 | 75 | 19 | 38 | 6194 | 799714 | 159341 | 1.56 |
| transform | 3 | 2 | 1 | 0 | 111 | 52 | 14 | 28 | 4581 | 567320 | 114935 | 1.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 32 | 29 | 3 | 0 | 4109 | 866 | 215 | 428 | 77585 | 9769758 | 1240721 | 13.97 |
| developer | claude-opus-5-5 | 33 | 0 | 0 | 0 | 2720 | 1148 | 275 | 542 | 103605 | 14230263 | 1578962 | 17.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 158 | 1.54 | 0 | 0.00 |
| green | 438 | 1.92 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| for a step whose step text carries `⟦replaces-case⟧`, the develop-green prompt `build-develop-prompt.sh green` builds permits deleting the one bash case the step names, and still forbids modifying or deleting any other case ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 180 | 42 | 84 | 16703 | 2155566 | 281852 | 3.02 | 462 | unknown | 0/5 | nothing-left |  |  | full |
| for a step whose step text does not carry `⟦replaces-case⟧`, the develop-green prompt `build-develop-prompt.sh green` builds is byte-identical to the one it builds today ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 85 | 21 | 40 | 8261 | 1169302 | 109926 | 1.28 | unknown | unknown | unknown | unknown |  |  | pin |
| for a step whose step text carries `⟦replaces-case⟧`, the revise prompt `build-develop-prompt.sh revise green` builds permits deleting the one bash case the step names, and still forbids modifying or deleting any other case, while without the mark it is byte-identical to today's | 6 | 3 | 0 | 0 | 0 | 0 | 187 | 47 | 94 | 15626 | 2394670 | 280695 | 3.04 | 415 | unknown | 0/5 | nothing-structural |  |  | full |
| for a `--step` carrying `⟦replaces-case⟧`, the verify-green prompt `build-verify-prompt.sh green` builds tells the verifier to PASS only when the named bash case is gone and a pytest case asserting the same behaviour was added, and to REJECT a deletion or modification of any other case ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 286 | 67 | 132 | 27633 | 3286298 | 328532 | 3.84 | 700 | 1/2 | 0/5 | structural-owed |  |  | full |
| for a `--step` without `⟦replaces-case⟧`, or no `--step` at all, the verify-green prompt `build-verify-prompt.sh green` builds is byte-identical to the one it builds today ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 89 | 21 | 42 | 9063 | 1098128 | 95024 | 1.16 | unknown | unknown | unknown | unknown |  |  | pin |
| `build-verify-prompt.sh` takes the same arguments as today, and a green call with an extra positional argument beyond the target test id still exits 2 with nothing on stdout ⟦criterion 5⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 248 | 61 | 118 | 22910 | 2784069 | 355210 | 3.86 | 718 | 2/2 | 0/5 | nothing-structural |  |  | full |
| `ledger-steps.sh` prints an open `⟦replaces-case⟧ ⟦criterion k⟧` step with kind `step`, added `0` and criterion `k`, and `next-unchecked.sh` prints it as the next step like any other ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 59 | 16 | 32 | 5821 | 792043 | 91852 | 1.01 | unknown | unknown | unknown | unknown |  |  | pin |
| `add-ledger-step.sh` does not count a `⟦replaces-case⟧` step against `VERI_STEP_GROWTH` unless that step is also marked `⟦added⟧` ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 14 | 28 | 7020 | 674471 | 91093 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's *Scope & plan* section says a criterion replacing an implementation case under ADR 0027 is planned as one step marked `⟦replaces-case⟧` naming the suite path and the case's exact name, and that such a step's Red is the pytest case failing against the code before the change ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 237 | 58 | 116 | 22104 | 3057777 | 292827 | 3.40 | 1020 | unknown | 0/5 | structural-owed |  |  | full |
| CONTEXT.md defines *contract case*, *implementation case* and the `⟦replaces-case⟧` mark ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 242 | 59 | 114 | 18735 | 2837451 | 275189 | 3.14 | 1153 | unknown | 0/5 | nothing-structural |  |  | full |
| fix the full-suite failure: no-nested-suites.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here: ledger-steps.test.sh:22 names status.test.sh outside a comment, in a shape this file treats as launching it ⟦suite-repair⟧ ⟦criterion 8⟧ | 7 | 4 | 0 | 0 | 0 | 0 | 173 | 43 | 88 | 13784 | 2054963 | 261594 | 3.32 | 917 | unknown | 0/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| for a step whose step text carries `⟦replaces-case⟧`, the develop-green prompt `build-develop-prompt.sh green` builds permits deleting the one bash case the step names, and still forbids modifying or deleting any other case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 96 | 0.81 |
| for a step whose step text carries `⟦replaces-case⟧`, the revise prompt `build-develop-prompt.sh revise green` builds permits deleting the one bash case the step names, and still forbids modifying or deleting any other case, while without the mark it is byte-identical to today's | 1 | 0/5 | nothing-structural | PASS | 0 | 67 | 0.78 |
| for a `--step` carrying `⟦replaces-case⟧`, the verify-green prompt `build-verify-prompt.sh green` builds tells the verifier to PASS only when the named bash case is gone and a pytest case asserting the same behaviour was added, and to REJECT a deletion or modification of any other case ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 80 | 0.87 |
| `build-verify-prompt.sh` takes the same arguments as today, and a green call with an extra positional argument beyond the target test id still exits 2 with nothing on stdout ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 74 | 0.82 |
| SKILL.md's *Scope & plan* section says a criterion replacing an implementation case under ADR 0027 is planned as one step marked `⟦replaces-case⟧` naming the suite path and the case's exact name, and that such a step's Red is the pytest case failing against the code before the change ⟦criterion 7⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 301 | 0.93 |
| CONTEXT.md defines *contract case*, *implementation case* and the `⟦replaces-case⟧` mark ⟦criterion 8⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 78 | 0.88 |
| fix the full-suite failure: no-nested-suites.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here: ledger-steps.test.sh:22 names status.test.sh outside a comment, in a shape this file treats as launching it ⟦suite-repair⟧ ⟦criterion 8⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 62 | 0.78 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 5 | 5 | 23 | 20 | 20 | 5 | 5 | 6 | 5 | 8 | 5 | 5 | 5 | 5 | 5 | 94 | 5 | 5 | 4 | 4 | 5 | 5 | 0 | 5 | 5 | 5 | 103 | 102 | 4 | 0 | 0 | 1 | 0 | 0 | 2 | 200 | 203 | 0 | 0 | 210 | 0 | 1 | 1 | 82 | 665 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 26 | 4 | 12 | 8 | 8 | 0 | 4 | 23 |
| fast | 29 | 27 | 26 | 27 | 27 | 26 | 26 | 26 | 24 | 25 | 26 | 25 | 24 | 26 | 25 | 27 | 27 | 28 | 27 | 26 | 28 | 628 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 1 | 0 | 1 | 1 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 566 | 571 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 490 | 970 | 181190 | 24000021 | 2819683 | 31.52 |
