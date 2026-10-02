### 📊 Metrics — issue 618

Wall time for the issue: 5307 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/662.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 2 | 4 | 1181 | 59392 | 38836 | 0.35 |
| red | 8 | 2 | 0 | 0 | 1040 | 365 | 79 | 154 | 33669 | 4122265 | 393365 | 4.65 |
| pin | 4 | 4 | 0 | 0 | 503 | 83 | 20 | 40 | 8022 | 840833 | 162860 | 1.63 |
| green | 6 | 2 | 1 | 0 | 1153 | 156 | 45 | 86 | 15080 | 1993181 | 212427 | 2.40 |
| refactor | 4 | 2 | 0 | 0 | 507 | 144 | 31 | 62 | 10890 | 1520526 | 182135 | 1.98 |
| structural | 4 | 0 | 0 | 0 | 205 | 45 | 14 | 26 | 3925 | 483690 | 148881 | 1.37 |
| transform | 1 | 1 | 0 | 0 | 120 | 20 | 6 | 12 | 1871 | 253286 | 38439 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 13 | 12 | 1 | 0 | 1901 | 343 | 76 | 150 | 29001 | 3303083 | 496782 | 5.22 |
| developer | claude-opus-5-5 | 15 | 0 | 0 | 0 | 1643 | 482 | 121 | 234 | 45637 | 5970090 | 680161 | 7.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 770 | 1.51 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| a launch refused because a leaf of the same name is alive writes no `.exit` for that name: `wait-leaf.sh <name>` keeps answering 3 while the live leaf runs, and the live leaf's own exit code is what lands in `.tdd/<name>.exit` when it finishes ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 105 | 20 | 38 | 9944 | 1159459 | 109118 | 1.30 | unknown | unknown | unknown | unknown |  |  | pin |
| when `supervise.sh` refuses a launch under a name different from the live leaf's, because the leaf recorded in `.tdd/leaf.owner` is alive, it exits 2 and `.tdd/<refused-name>.exit` holds `2` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 205 | 50 | 94 | 17084 | 2255579 | 263409 | 2.90 | 914 | unknown | 1/5 | structural-owed |  |  | full |
| after such a refusal, `wait-leaf.sh <refused-name>` exits 2, not 3 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 17 | 34 | 6839 | 845763 | 89623 | 1.02 | unknown | unknown | unknown | unknown |  |  | pin |
| a refused launch does not run its command and leaves `.tdd/leaf.owner` naming the live leaf, unchanged ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 15 | 30 | 6978 | 717178 | 89180 | 1.00 | unknown | unknown | unknown | unknown |  |  | pin |
| a launch under a different name is not refused when the leaf recorded in `.tdd/leaf.owner` is alive but `.tdd/<owner-name>.exit` already exists: it runs its command and exits with that command's code ⟦criterion 4⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 241 | 58 | 116 | 21243 | 2774450 | 311437 | 3.47 | 1277 | 1/2 | 1/5 | structural-owed |  |  | full |
| a launch is still refused (exit 2, stderr naming the live leaf and its pid) when the recorded leaf is alive and `.tdd/<owner-name>.exit` does not exist ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 15 | 30 | 5573 | 724376 | 88020 | 0.96 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| when `supervise.sh` refuses a launch under a name different from the live leaf's, because the leaf recorded in `.tdd/leaf.owner` is alive, it exits 2 and `.tdd/<refused-name>.exit` holds `2` ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 285 | 1.03 |
| a launch under a different name is not refused when the leaf recorded in `.tdd/leaf.owner` is alive but `.tdd/<owner-name>.exit` already exists: it runs its command and exits with that command's code ⟦criterion 4⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 222 | 0.94 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 45 | 45 | 46 | 45 | 45 | 46 | 45 | 46 | 45 | 42 | 43 | 46 | 43 | 45 | 47 | 49 | 44 | 135 | 45 | 45 | 45 | 45 | 45 | 48 | 48 | 47 |
| target | 46 | 45 | 46 | 44 | 43 | 43 | 44 | 45 | 0 | 44 | 45 | 48 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 23 | 22 | 22 | 21 | 24 | 23 | 24 | 22 | 23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 197 | 384 | 74638 | 9273173 | 1176943 | 12.76 |
