### 📊 Metrics — issue 2897

Wall time for the issue: 5537 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3106.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.16 over 75 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90615 tokens, largest 169656 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90615 |
| 2 | $0.08 | 97958 |
| 3 | $0.03 | 98768 |
| 4 | $0.03 | 100463 |
| 5 | $0.03 | 101097 |
| 6 | $0.02 | 101505 |
| 7 | $0.02 | 101804 |
| 8 | $0.02 | 102164 |
| 9 | $0.02 | 102426 |
| 10 | $0.03 | 103346 |
| 11 | $0.03 | 104036 |
| 12 | $0.04 | 106451 |
| 13 | $0.03 | 107447 |
| 14 | $0.03 | 108500 |
| 15 | $0.02 | 108812 |
| 16 | $0.03 | 109487 |
| 17 | $0.03 | 110012 |
| 18 | $0.03 | 110549 |
| 19 | $0.03 | 111106 |
| 20 | $0.03 | 112422 |
| 21 | $0.03 | 113236 |
| 22 | $0.04 | 114965 |
| 23 | $0.03 | 115627 |
| 24 | $0.03 | 116330 |
| 25 | $0.03 | 116584 |
| 26 | $0.03 | 117425 |
| 27 | $0.03 | 118037 |
| 28 | $0.03 | 119097 |
| 29 | $0.03 | 119851 |
| 30 | $0.03 | 120379 |
| 31 | $0.03 | 120797 |
| 32 | $0.03 | 121455 |
| 33 | $0.03 | 121728 |
| 34 | $0.03 | 122320 |
| 35 | $0.03 | 123044 |
| 36 | $0.03 | 123559 |
| 37 | $0.03 | 124009 |
| 38 | $0.03 | 124667 |
| 39 | $0.03 | 125510 |
| 40 | $0.03 | 126202 |
| 41 | $0.03 | 127229 |
| 42 | $0.04 | 128423 |
| 43 | $0.03 | 129299 |
| 44 | $0.09 | 137666 |
| 45 | $0.03 | 138584 |
| 46 | $0.03 | 139439 |
| 47 | $0.03 | 140243 |
| 48 | $0.03 | 140987 |
| 49 | $0.04 | 141875 |
| 50 | $0.03 | 142260 |
| 51 | $0.04 | 143198 |
| 52 | $0.03 | 143516 |
| 53 | $0.04 | 144533 |
| 54 | $0.03 | 144797 |
| 55 | $0.04 | 145733 |
| 56 | $0.03 | 146461 |
| 57 | $0.05 | 149508 |
| 58 | $0.04 | 150205 |
| 59 | $0.03 | 150819 |
| 60 | $0.04 | 152165 |
| 61 | $0.04 | 153105 |
| 62 | $0.03 | 153569 |
| 63 | $0.03 | 153824 |
| 64 | $0.03 | 154113 |
| 65 | $0.04 | 154868 |
| 66 | $0.03 | 155090 |
| 67 | $0.03 | 155419 |
| 68 | $0.06 | 158451 |
| 69 | $0.04 | 159596 |
| 70 | $0.08 | 165357 |
| 71 | $0.04 | 166336 |
| 72 | $0.04 | 167164 |
| 73 | $0.04 | 168548 |
| 74 | $0.04 | 168995 |
| 75 | $0.04 | 169656 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 6 | 1 | 2 | 645 | 0 | 30369 | 0.08 |
| red | 5 | 2 | 0 | 0 | 400 | 106 | 27 | 52 | 11415 | 777496 | 116900 | 0.48 |
| green | 6 | 2 | 1 | 0 | 944 | 110 | 30 | 56 | 8089 | 788613 | 100114 | 0.51 |
| refactor | 2 | 0 | 0 | 0 | 24 | 17 | 4 | 8 | 499 | 76822 | 42872 | 0.12 |
| pin | 1 | 0 | 1 | 0 | 32 | 13 | 3 | 6 | 1250 | 58404 | 30730 | 0.10 |
| predicate | 1 | 0 | 0 | 0 | 18 | 15 | 3 | 6 | 627 | 56012 | 28697 | 0.08 |
| cover | 1 | 0 | 0 | 0 | 74 | 20 | 5 | 10 | 1516 | 133900 | 12749 | 0.06 |
| structural | 1 | 0 | 0 | 0 | 34 | 11 | 4 | 8 | 1035 | 106259 | 13222 | 0.05 |
| transform | 1 | 1 | 0 | 0 | 46 | 12 | 5 | 10 | 966 | 113248 | 29085 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 6 | 2 | 0 | 861 | 111 | 31 | 60 | 9001 | 754368 | 152071 | 0.55 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 523 | 171 | 42 | 82 | 14577 | 1148415 | 203129 | 0.77 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 198 | 28 | 9 | 16 | 2464 | 207971 | 49538 | 0.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 92 | 0.13 |
| green | 636 | 0.37 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 32 | 0.10 |
| predicate | 0 | 0.00 | 18 | 0.08 |
| cover | 0 | 0.00 | 74 | 0.06 |
| structural | 0 | 0.00 | 34 | 0.05 |
| transform | 0 | 0.00 | 46 | 0.09 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The diff verifier's deleted-case guard refuses a step that deletes a `func TestX` in a `_test.go` file which an earlier step of the branch added, with the existing refusal text unchanged (`step deleted pytest cases an earlier step added: …`) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 84 | 22 | 40 | 6720 | 546162 | 100365 | 0.37 | 645 | unknown | 0/5 | nothing-left |  |  | full |
| The diff verifier's deleted-case guard refuses a step that deletes an `it("x", …)` case in a `.test.js` file which an earlier step of the branch added, with the existing refusal text unchanged ⟦criterion 2⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 121 | 30 | 58 | 9562 | 791212 | 133057 | 0.61 | 1093 | 1/2 | 0/5 | structural-owed |  |  | full |
| The diff verifier's deleted-case guard does not refuse a step that renames a `func TestX` in a `_test.go` file, added by an earlier step, with its body unchanged ⟦criterion 3⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 41 | 12 | 24 | 4971 | 363961 | 57194 | 0.23 | unknown | unknown | unknown | unknown |  |  | full |
| The diff verifier's deleted-case guard does not refuse a step that renames a `func TestX` in a `_test.go` file, added by an earlier step, with its body unchanged ⟦criterion 3⟧ ⟂ retired unpinnable | 4 | 1 | 0 | 0 | 0 | 0 | 58 | 17 | 34 | 4144 | 409419 | 83753 | 0.29 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The diff verifier's deleted-case guard refuses a step that deletes a `func TestX` in a `_test.go` file which an earlier step of the branch added, with the existing refusal text unchanged (`step deleted pytest cases an earlier step added: …`) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |
| The diff verifier's deleted-case guard refuses a step that deletes an `it("x", …)` case in a `.test.js` file which an earlier step of the branch added, with the existing refusal text unchanged ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 16 | 0.08 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 39 | 7 | 31 | 41 | 21 | 22 | 26 | 27 | 24 | 32 | 45 | 50 | 26 | 23 | 20 | 4 | 27 |  |  |  |  |  |  |  |  |  |  |
| fast | 44 | 40 | 33 | 32 | 40 | 52 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 4 | 4 | 4 | 4 | 5 | 3 | 4 | 5 | 4 | 4 | 3 | 4 | 5 | 10 | 9 | 6 | 6 | 8 | 10 | 10 | 8 | 6 | 6 | 9 | 6 | 9 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 82 | 158 | 26042 | 2110754 | 404738 | 4.74 (estimate) |
