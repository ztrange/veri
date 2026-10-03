### 📊 Metrics — issue 705

Wall time for the issue: 6076 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 14 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/742.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 40 | 30 | 4 | 8 | 2787 | 121389 | 81255 | 0.73 |
| red | 10 | 5 | 0 | 0 | 610 | 434 | 81 | 156 | 42403 | 4166599 | 509441 | 5.76 |
| green | 14 | 5 | 2 | 0 | 1629 | 583 | 125 | 246 | 52417 | 6123760 | 590152 | 7.00 |
| refactor | 14 | 5 | 2 | 0 | 903 | 388 | 83 | 164 | 31125 | 3774550 | 583233 | 6.04 |
| diff | 14 | 7 | 0 | 0 | 791 | 529 | 86 | 168 | 53705 | 4392352 | 706335 | 7.60 |
| predicate | 1 | 0 | 0 | 0 | 19 | 14 | 3 | 6 | 1368 | 114249 | 42683 | 0.39 |
| structural | 1 | 0 | 0 | 0 | 54 | 33 | 9 | 16 | 3686 | 400780 | 47285 | 0.53 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 28 | 23 | 5 | 0 | 1903 | 833 | 176 | 350 | 71408 | 8139388 | 1145927 | 12.22 |
| developer | claude-opus-5-5 | 28 | 0 | 0 | 0 | 2143 | 1178 | 215 | 414 | 116083 | 10954291 | 1414457 | 15.83 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1038 | 4.01 | 0 | 0.00 |
| refactor | 782 | 3.85 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A sourced library under skills/tdd/scripts/tests/lib/ makes the planted scratch tree — the guard copy, the harness lib beside it and the companions the sourcing suite names — runs that guard copy over a given document recording its exit code and output, and reads the failure count off the guard's count line ('<none>' when it has none); a unit suite pins each over a stub guard ⟦criterion 1⟧ | 12 | 3 | 3 | 0 | 0 | 0 | 492 | 102 | 196 | 44001 | 4867461 | 491768 | 5.79 | 1215 | green 1/2, refactor 2/2 | 1/5 | nothing-left |  |  | full |
| The shared guard-plant library defines the guard-is-there probe (missing or non-executable guard), the guard-is-red probe and the green-unplanted probe, each adding a problem naming the guard and the document the sourcing suite names; the unit suite pins each over a stub guard ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 317 | 62 | 124 | 26963 | 3177010 | 343818 | 3.93 | 966 | 1/2 | 0/5 | structural-owed |  |  | full |
| The shared guard-plant library defines the plant-is-what-it-claims checks — the committed document carries the text the plant removes, the planted one no longer carries it and does carry what it was replaced with, and the plant changed exactly the carrier lines and no other — parameterised by the texts the sourcing suite names; the unit suite pins each ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 220 | 43 | 86 | 21074 | 2179052 | 289327 | 3.17 | 384 | unknown | 1/5 | nothing-structural |  |  | full |
| The shared guard-plant library defines the sequence itself — guard-is-there, then plant, then plant-is-what-it-claims, then green-unplanted, then the sourcing suite's own probes, stopping where a probe says the criterion cannot be asked — and the unit suite pins the order and the stops ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 199 | 38 | 76 | 19067 | 1831097 | 282045 | 3.00 | 462 | unknown | 0/5 | nothing-left |  |  | full |
| beyond-spec-narration-guard.test.sh sources the shared guard-plant library, runs its cases through the library's sequence, and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 58 | 13 | 26 | 5911 | 610475 | 91079 | 0.97 | 148 | unknown | unknown | unknown |  |  | full |
| flag-class-amendment-guard.test.sh sources the shared guard-plant library, runs its cases through the library's sequence, and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 11 | 20 | 4237 | 456685 | 93411 | 0.92 | 90 | unknown | unknown | unknown |  |  | full |
| verifier-launch-guard.test.sh sources the shared guard-plant library, runs its cases through the library's sequence, and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 93 | 14 | 28 | 10502 | 749332 | 109010 | 1.23 | 137 | unknown | unknown | unknown |  |  | full |
| docs-read-guard.test.sh sources the shared guard-plant library, runs its cases through the library's sequence, and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 149 | 18 | 36 | 15343 | 1155938 | 125790 | 1.54 | 202 | unknown | unknown | unknown |  |  | full |
| The shared guard-plant library's make_plant_tree records a problem naming the companion and returns 1 when a companion the sourcing suite names cannot be copied, so the sequence never passes a case it did not ask (the four suites' own plants did) ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 177 | 44 | 84 | 14840 | 2010289 | 275868 | 2.91 | 395 | unknown | 0/5 | nothing-left |  |  | full |
| verifier-launch-guard.test.sh's planted-run case calls probe_guard_is_red instead of repeating its own exit-status pair check (formerly :246-256) ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 10 | 18 | 3530 | 386055 | 87357 | 0.85 | 66 | unknown | unknown | unknown |  |  | full |
| Across the four suites every case name, every expectation and every suite-specific probe (probe_guard_names_the_narration_case, probe_guard_names_the_routing_case and the like) is left unchanged by the branch ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 134 | 14 | 28 | 12316 | 818084 | 125284 | 1.41 | 203 | unknown | unknown | unknown |  |  | full |
| no-nested-suites.test.sh's exemption entry for docs-read-guard.test.sh is left naming that suite with its reason, unchanged by the branch ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 6 | 12 | 1866 | 215783 | 74404 | 0.68 | 46 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A sourced library under skills/tdd/scripts/tests/lib/ makes the planted scratch tree — the guard copy, the harness lib beside it and the companions the sourcing suite names — runs that guard copy over a given document recording its exit code and output, and reads the failure count off the guard's count line ('<none>' when it has none); a unit suite pins each over a stub guard ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 2 | 554 | 2.46 |
| The shared guard-plant library defines the guard-is-there probe (missing or non-executable guard), the guard-is-red probe and the green-unplanted probe, each adding a problem naming the guard and the document the sourcing suite names; the unit suite pins each over a stub guard ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 91 | 0.82 |
| The shared guard-plant library defines the plant-is-what-it-claims checks — the committed document carries the text the plant removes, the planted one no longer carries it and does carry what it was replaced with, and the plant changed exactly the carrier lines and no other — parameterised by the texts the sourcing suite names; the unit suite pins each ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 103 | 1.00 |
| The shared guard-plant library defines the sequence itself — guard-is-there, then plant, then plant-is-what-it-claims, then green-unplanted, then the sourcing suite's own probes, stopping where a probe says the criterion cannot be asked — and the unit suite pins the order and the stops ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 82 | 0.91 |
| The shared guard-plant library's make_plant_tree records a problem naming the companion and returns 1 when a companion the sourcing suite names cannot be copied, so the sequence never passes a case it did not ask (the four suites' own plants did) ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 73 | 0.86 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 2 | 0 | 0 | 0 | 0 | 57 | 2 | 0 | 0 | 0 | 1 | 8 | 2 | 30 | 0 | 0 | 1 | 4 | 0 | 2 | 2 | 89 | 0 | 101 | 0 | 106 | 101 | 2 | 0 | 86 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 104 | 0 | 0 | 0 | 12 | 16 | 5 | 19 | 0 | 0 | 0 | 32 | 33 | 0 | 14 | 0 | 14 |
| fast | 26 | 27 | 25 | 26 | 26 | 26 | 26 | 25 | 26 | 27 | 27 | 28 | 27 | 26 | 28 | 27 | 27 | 28 | 28 | 26 | 26 | 27 | 26 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 1 | 0 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 391 | 764 | 187491 | 19093679 | 2560384 | 28.05 |
