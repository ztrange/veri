### 📊 Metrics — issue 1846

Wall time for the issue: 2741 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1857.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $27.30 over 98 turns, in 1 sessions.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $2.45 | 98046 |
| 2 | $2.45 | 98046 |
| 3 | $0.19 | 99292 |
| 4 | $0.19 | 99292 |
| 5 | $0.21 | 101195 |
| 6 | $0.16 | 101535 |
| 7 | $0.16 | 101535 |
| 8 | $0.17 | 101957 |
| 9 | $0.16 | 102281 |
| 10 | $0.16 | 102281 |
| 11 | $0.16 | 102281 |
| 12 | $0.16 | 102577 |
| 13 | $0.17 | 103135 |
| 14 | $0.17 | 103135 |
| 15 | $0.17 | 103563 |
| 16 | $0.17 | 103931 |
| 17 | $0.17 | 104539 |
| 18 | $0.17 | 104539 |
| 19 | $0.19 | 105533 |
| 20 | $0.19 | 105533 |
| 21 | $0.21 | 107185 |
| 22 | $0.20 | 108556 |
| 23 | $0.20 | 108556 |
| 24 | $0.20 | 108556 |
| 25 | $0.19 | 109594 |
| 26 | $0.19 | 109594 |
| 27 | $0.19 | 110380 |
| 28 | $0.18 | 110691 |
| 29 | $0.19 | 111477 |
| 30 | $0.19 | 111477 |
| 31 | $0.19 | 112048 |
| 32 | $0.19 | 112904 |
| 33 | $0.19 | 112904 |
| 34 | $0.18 | 113182 |
| 35 | $0.43 | 121982 |
| 36 | $0.43 | 121982 |
| 37 | $0.43 | 121982 |
| 38 | $0.21 | 122877 |
| 39 | $0.20 | 123548 |
| 40 | $0.20 | 123548 |
| 41 | $0.20 | 123548 |
| 42 | $0.21 | 124243 |
| 43 | $0.24 | 126064 |
| 44 | $0.24 | 126064 |
| 45 | $0.24 | 126064 |
| 46 | $0.21 | 126858 |
| 47 | $0.23 | 127996 |
| 48 | $0.22 | 128862 |
| 49 | $0.22 | 129597 |
| 50 | $0.22 | 129597 |
| 51 | $0.21 | 130216 |
| 52 | $0.22 | 130908 |
| 53 | $0.43 | 138547 |
| 54 | $0.43 | 138547 |
| 55 | $0.43 | 138547 |
| 56 | $0.23 | 139319 |
| 57 | $0.23 | 139964 |
| 58 | $0.23 | 139964 |
| 59 | $0.23 | 140762 |
| 60 | $0.23 | 140762 |
| 61 | $0.23 | 140762 |
| 62 | $0.25 | 141898 |
| 63 | $0.25 | 141898 |
| 64 | $0.24 | 142631 |
| 65 | $0.22 | 142920 |
| 66 | $0.23 | 143399 |
| 67 | $0.24 | 144108 |
| 68 | $0.24 | 144108 |
| 69 | $0.29 | 146643 |
| 70 | $0.29 | 146643 |
| 71 | $0.29 | 146643 |
| 72 | $0.24 | 147397 |
| 73 | $0.24 | 148105 |
| 74 | $0.24 | 148105 |
| 75 | $0.24 | 148105 |
| 76 | $0.26 | 149301 |
| 77 | $0.25 | 150023 |
| 78 | $0.23 | 150293 |
| 79 | $0.25 | 151124 |
| 80 | $0.25 | 151124 |
| 81 | $0.24 | 151480 |
| 82 | $0.24 | 151480 |
| 83 | $0.24 | 151903 |
| 84 | $0.24 | 151903 |
| 85 | $0.24 | 152235 |
| 86 | $0.25 | 152869 |
| 87 | $0.25 | 152869 |
| 88 | $0.25 | 152869 |
| 89 | $0.27 | 154214 |
| 90 | $0.27 | 154214 |
| 91 | $0.25 | 154851 |
| 92 | $0.28 | 156419 |
| 93 | $0.25 | 157031 |
| 94 | $0.25 | 157465 |
| 95 | $0.25 | 157465 |
| 96 | $0.25 | 157933 |
| 97 | $0.25 | 157933 |
| 98 | $0.25 | 158316 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 16 | 1 | 2 | 905 | 0 | 29914 | 0.08 |
| red | 4 | 1 | 0 | 0 | 224 | 109 | 26 | 52 | 10709 | 834483 | 102600 | 0.45 |
| green | 4 | 1 | 1 | 0 | 451 | 97 | 25 | 48 | 7909 | 712693 | 73116 | 0.43 |
| refactor | 2 | 1 | 0 | 0 | 65 | 15 | 6 | 10 | 1141 | 104828 | 44081 | 0.13 |
| pin | 2 | 2 | 0 | 0 | 45 | 34 | 10 | 20 | 2768 | 271305 | 28400 | 0.13 |
| diff | 2 | 1 | 0 | 0 | 268 | 64 | 19 | 38 | 4267 | 548028 | 51529 | 0.23 |
| predicate | 1 | 0 | 0 | 0 | 24 | 20 | 4 | 8 | 764 | 85942 | 29620 | 0.09 |
| structural | 1 | 0 | 0 | 0 | 57 | 24 | 6 | 12 | 1395 | 167197 | 13730 | 0.07 |
| transform | 1 | 1 | 0 | 0 | 47 | 13 | 4 | 8 | 753 | 84243 | 29185 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 470 | 144 | 39 | 76 | 11341 | 987756 | 168700 | 0.63 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 501 | 194 | 50 | 100 | 15526 | 1498233 | 180908 | 0.76 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 229 | 54 | 12 | 22 | 3744 | 322730 | 52567 | 0.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 451 | 0.43 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When verify.py refuses a verifier leaf for modifying the repository because a stub verifier changed a tracked file's content, it writes the full git diff between the before and after trees for the changed paths to a file under .tdd/ named after the leaf, written before the tree is reset, holding the content change byte-exactly, and the refusal message names that file ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 170 | 43 | 82 | 14202 | 1200140 | 179114 | 0.81 | 779 | 1/2 | 0/5 | structural-owed |  |  | full |
| When a stub verifier changes only a tracked file's mode, the diff file verify.py writes on refusal under .tdd/ named after the leaf shows that mode change byte-exactly ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 12 | 24 | 4428 | 361458 | 34853 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| prompts/verify-green.md's probe instruction says the .orig copy sits beside the file it copies, never in a shared directory such as /tmp ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 19 | 38 | 4267 | 548028 | 51529 | 0.23 | 310 | n/a | n/a | n/a |  |  | full |
| The rendered verify-green prompt's probe instruction says the .orig copy sits beside the file it copies, never in a shared directory such as /tmp, pinned by a case on the rendered prompt ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 101 | 26 | 52 | 6809 | 699093 | 106765 | 0.41 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When verify.py refuses a verifier leaf for modifying the repository because a stub verifier changed a tracked file's content, it writes the full git diff between the before and after trees for the changed paths to a file under .tdd/ named after the leaf, written before the tree is reset, holding the content change byte-exactly, and the refusal message names that file ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 65 | 0.13 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 33 | 31 | 31 | 31 | 31 | 31 | 31 | 0 | 37 | 37 | 3 | 31 | 31 |
| fast | 12 | 13 | 14 | 12 | 13 | 13 | 13 | 12 | 12 |  |  |  |  |
| target | 1 | 31 | 0 | 1 | 2 | 0 | 0 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 101 | 198 | 30611 | 2808719 | 402175 | 1.69 |
