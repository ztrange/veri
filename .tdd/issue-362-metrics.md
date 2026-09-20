### 📊 Metrics — issue 362

Wall time for the issue: 3421 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/397.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 7 | 3 | 0 | 0 | 612 | 555 | 102 | 184 | 44514 | 5208934 | 364672 | 7.36 |
| green | 6 | 3 | 0 | 0 | 1384 | 493 | 111 | 206 | 39177 | 5644632 | 316595 | 6.97 |
| refactor | 6 | 3 | 0 | 0 | 758 | 354 | 66 | 120 | 26595 | 2983508 | 287586 | 5.03 |
| pin | 1 | 1 | 0 | 0 | 38 | 32 | 7 | 12 | 2481 | 255732 | 39554 | 0.59 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| The refactor verifier prompt tells the verifier to report an unhandled edge case the spec implies as a NEW_STEP: line before VERDICT:, and no longer to REJECT for it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 431 | 84 | 154 | 33702 | 4026746 | 299516 | 5.85 | 1166 | unknown | 0/5 | nothing-structural |
| Every built verifier prompt's output contract allows NEW_STEP: lines before the final VERDICT:/REASON: pair ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 368 | 76 | 138 | 28973 | 3505531 | 281169 | 5.29 | 1052 | unknown | 0/5 | nothing-structural |
| parse-verdict.sh returns the same verdict and reason for output carrying NEW_STEP: lines before the final pair as for one without ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 100 | 17 | 32 | 8374 | 745039 | 84573 | 1.43 | unknown | unknown | unknown | unknown |
| SKILL.md's Refactor section adds the passing verify-refactor output's NEW_STEP: values to the ledger after STEP, in the same add-ledger-step.sh call as the refactor leaf's ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 535 | 109 | 198 | 41718 | 5815490 | 343149 | 7.38 | 792 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 183 | 181 | 180 | 2 | 2 | 183 | 183 | 182 | 1 | 1 | 2 | 48 | 54 | 1 | 2 |
| fast | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 1 | 0 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 286 | 522 | 112767 | 14092806 | 1008407 | 19.95 |
