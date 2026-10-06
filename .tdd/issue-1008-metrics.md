### 📊 Metrics — issue 1008

Wall time for the issue: 1036 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1009.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 3 | 1 | 2 | 372 | 11866 | 29460 | 0.12 |
| red | 2 | 1 | 0 | 0 | 76 | 63 | 15 | 30 | 5976 | 729035 | 88868 | 0.81 |
| green | 2 | 1 | 0 | 0 | 152 | 82 | 19 | 36 | 6115 | 811284 | 80335 | 0.74 |
| refactor | 2 | 1 | 0 | 0 | 67 | 43 | 13 | 24 | 3790 | 510389 | 79377 | 0.62 |
| predicate | 1 | 0 | 0 | 0 | 16 | 14 | 2 | 4 | 1239 | 53007 | 36149 | 0.32 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 136 | 64 | 23 | 44 | 7500 | 912416 | 146109 | 0.84 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 181 | 141 | 27 | 52 | 9992 | 1203165 | 168080 | 1.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A suite run through run-suite.sh reads maintenance.auto=false from its git config (git config --get maintenance.auto prints false inside the suite), as it does under make test ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 202 | 49 | 94 | 17120 | 2103715 | 284729 | 2.50 | 384 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A suite run through run-suite.sh reads maintenance.auto=false from its git config (git config --get maintenance.auto prints false inside the suite), as it does under make test ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 67 | 0.62 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 4 | 0 | 2 | 4 | 1 | 0 | 0 |
| fast | 15 | 15 | 15 |  |  |  |  |  |  |  |
| target | 3 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 96 | 17492 | 2115581 | 314189 | 2.63 |
