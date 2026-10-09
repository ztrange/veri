### 📊 Metrics — issue 1260

Wall time for the issue: 4436 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1293.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 6 | 1 | 2 | 870 | 12385 | 33037 | 0.14 |
| red | 6 | 3 | 0 | 0 | 209 | 172 | 40 | 78 | 17594 | 2006853 | 297347 | 2.59 |
| green | 6 | 3 | 0 | 0 | 662 | 217 | 59 | 114 | 20748 | 3106966 | 287701 | 2.78 |
| refactor | 6 | 3 | 0 | 0 | 272 | 133 | 42 | 82 | 12701 | 1886353 | 250410 | 2.11 |
| diff | 4 | 2 | 0 | 0 | 2040 | 119 | 32 | 62 | 11331 | 1573184 | 202399 | 1.78 |
| predicate | 1 | 0 | 0 | 0 | 20 | 12 | 3 | 6 | 875 | 105807 | 37537 | 0.34 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 12 | 0 | 0 | 1592 | 194 | 65 | 126 | 20417 | 2713136 | 486426 | 2.69 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 1622 | 465 | 112 | 218 | 43702 | 5978412 | 622005 | 7.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The develop-green prompt (and the develop-revise prompt redoing green) built for a step marked ⟦replaces-case⟧ that names several cases of one suite permits deleting exactly those named cases and forbids modifying or deleting any case it does not name; a step naming one case is still permitted to delete that one case and nothing else ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 231 | 56 | 108 | 22003 | 3099569 | 311433 | 3.01 | 476 | unknown | 0/5 | nothing-left |  |  | full |
| The verify-green prompt built for a step marked ⟦replaces-case⟧ that names several cases of one suite PASSes only when every named case is gone from its suite and each has a pytest case asserting its behaviour, and REJECTs a deletion or modification of any case the step does not name; a step naming one case gets the same answer it gets today ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 176 | 46 | 92 | 17243 | 2207041 | 267284 | 2.38 | 407 | unknown | 0/5 | nothing-left |  |  | full |
| SKILL.md's ⟦replaces-case⟧ planning paragraph lets one step name one suite path and a list of that suite's cases each by exact name, and tells the planner to group related cases of one suite into one step, about a dozen at most, one case remaining a valid group of one ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 115 | 39 | 74 | 11797 | 1693562 | 256741 | 2.09 | 488 | unknown | 0/5 | nothing-left |  |  | full |
| A new ADR under docs/adr/, at the next free number, records PRD 009's decision 4 (expand/migrate/contract per interface with contract split into migrate-tests and remove-proxy, per-phase green and ledger marks counting as one refactor, what each phase freezes, contract only once no product caller remains, contract REVISE_BUDGET exhaustion resetting only itself and filed as owed, empty phases skipped, mutation-parity proof and its validity conditions, dead versus redundant deletions, no valid mutation going to a human as an owed decision, the pairs table), cites Beck 2002, Test Desiderata, Tidy First?, Parallel Change and Meszaros in its Context, and records the group ⟦replaces-case⟧ step with parity carried by the pairs table until C3 ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 17 | 32 | 7051 | 877914 | 115100 | 1.03 | 902 | n/a | n/a | n/a |  |  | full |
| ADR 0026 and ADR 0027 each carry a `**Superseded in part by [ADR-00NN](…)**` line on line 3 pointing at the new ADR — 0026's deletion rule replaced by measured redundancy; 0027's "the shim resolves" floor item replaced by one test over every shim, its exit-code and bad-argument-stderr items staying per script as in-process run_cli cases rather than bash cases, and its one-case-per-step wording replaced by the group step — with no other part of either record changed ⟦diff-checked⟧ ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 65 | 18 | 36 | 5155 | 801077 | 124836 | 1.08 | 1208 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The develop-green prompt (and the develop-revise prompt redoing green) built for a step marked ⟦replaces-case⟧ that names several cases of one suite permits deleting exactly those named cases and forbids modifying or deleting any case it does not name; a step naming one case is still permitted to delete that one case and nothing else ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 107 | 0.73 |
| The verify-green prompt built for a step marked ⟦replaces-case⟧ that names several cases of one suite PASSes only when every named case is gone from its suite and each has a pytest case asserting its behaviour, and REJECTs a deletion or modification of any case the step does not name; a step naming one case gets the same answer it gets today ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 100 | 0.79 |
| SKILL.md's ⟦replaces-case⟧ planning paragraph lets one step name one suite path and a list of that suite's cases each by exact name, and tells the planner to group related cases of one suite into one step, about a dozen at most, one case remaining a valid group of one ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 65 | 0.59 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 0 | 1 | 0 | 3 | 3 | 4 | 3 | 0 | 1 | 3 | 1 | 3 | 0 | 1 | 3 | 7 | 1 | 0 | 1 | 2 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 171 | 1 | 0 | 1 | 1 | 537 | 525 | 523 |
| fast | 31 | 30 | 30 | 31 | 30 | 31 | 30 | 31 | 31 | 31 | 33 | 31 | 31 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 177 | 344 | 64119 | 8691548 | 1108431 | 9.74 |
