### 📊 Metrics — issue 439

Wall time for the issue: 9783 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/441.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 20 | 9 | 0 | 0 | 1963 | 1779 | 297 | 520 | 134072 | 14519464 | 1069179 | 21.31 |
| green | 24 | 9 | 3 | 0 | 3647 | 1825 | 370 | 670 | 132158 | 18120440 | 1204097 | 24.41 |
| refactor | 18 | 9 | 0 | 0 | 2185 | 1413 | 233 | 446 | 104664 | 12001297 | 903098 | 17.65 |
| pin | 2 | 2 | 0 | 0 | 134 | 112 | 29 | 50 | 9490 | 1317723 | 102578 | 1.92 |
| plan | 1 | 1 | 0 | 0 | 33 | 28 | 3 | 6 | 2340 | 103823 | 36832 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2849 | 16.48 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| plan | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| build-verify-prompt.sh accepts a plan phase and builds its prompt from the issue spec and the ledger named as its third argument ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 776 | 144 | 254 | 58273 | 6862095 | 502768 | 9.92 | 1669 | 2/2 | 1/5 | structural-owed |
| build-verify-prompt.sh exits 2 with nothing on stdout for a plan invocation that names no ledger or names one it cannot read ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 417 | 71 | 130 | 28413 | 3359394 | 292747 | 5.32 | 562 | unknown | 1/5 | structural-owed |
| The plan prompt asks whether the steps tagged for a criterion together deliver that criterion as written, and requires a REJECT reason to name the criterion and the part of it no step covers ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 436 | 90 | 164 | 34144 | 4329925 | 298415 | 6.00 | 571 | unknown | 0/5 | nothing-left |
| The plan prompt directs a PASS when every criterion is delivered by the steps tagged for it ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 396 | 79 | 134 | 26003 | 3359670 | 279759 | 5.13 | 525 | unknown | 0/5 | nothing-left |
| The plan prompt requires a step judged too big for one Red to Green to Refactor cycle to be named in the reason under either verdict ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 504 | 87 | 162 | 36433 | 4373213 | 303221 | 6.13 | 647 | unknown | 0/5 | nothing-left |
| The plan prompt states that a step carrying no criterion tag is never by itself a reason to REJECT ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 426 | 87 | 150 | 28587 | 3933248 | 290402 | 5.59 | 545 | unknown | 1/5 | nothing-structural |
| The plan phase prompt carries only the issue spec and the ledger, and the four cycle phase prompts carry no ledger ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 191 | 31 | 54 | 15347 | 1552308 | 116222 | 2.32 | 248 | unknown | unknown | unknown |
| SKILL.md has the conductor run the plan verifier once after the ledger is committed and before the first step, and a REJECT rewrites the plan and re-verifies instead of ending the run ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 894 | 145 | 274 | 72883 | 8359169 | 482399 | 10.83 | 2257 | 1/2 | 3/5 | nothing-structural |
| SKILL.md treats a plan verification that rendered no verdict as a system failure bail rather than a PASS ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 204 | 33 | 62 | 13357 | 1732124 | 105843 | 2.26 | 244 | unknown | unknown | unknown |
| SKILL.md's script entries for build-verify-prompt.sh, verify.sh and run-verdict.sh name the plan phase beside the four cycle phases | 6 | 3 | 0 | 0 | 0 | 0 | 444 | 85 | 156 | 34846 | 4300344 | 305301 | 6.08 | 822 | unknown | 1/5 | nothing-structural |
| The plan prompt treats a step that restates a criterion as a mechanism as delivering it only when that mechanism is sufficient for the criterion as written, and directs a REJECT when no step establishes the criterion as written ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 441 | 77 | 146 | 32098 | 3797434 | 301875 | 5.72 | 585 | unknown | 0/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 59 | 2 | 4 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 0 | 74 | 114 | 75 | 124 | 119 | 119 | 119 | 119 | 14 | 0 | 0 | 0 | 0 | 0 | 75 | 127 | 0 | 76 | 0 | 3 | 2 | 2 | 3 | 3 | 2 | 0 |
| fast | 3 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 3 | 2 | 3 | 3 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 3 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 274 | 275 | 273 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 932 | 1692 | 382724 | 46062747 | 3315784 | 65.77 |
