### 📊 Metrics — issue 1228

Wall time for the issue: 7237 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1249.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 8 | 1 | 2 | 948 | 11966 | 34842 | 0.15 |
| diff | 4 | 2 | 0 | 0 | 1077 | 274 | 44 | 86 | 24319 | 2638064 | 208294 | 2.28 |
| rebase | 3 | 1 | 0 | 0 | 3311 | 102 | 37 | 72 | 8862 | 1992818 | 117581 | 1.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 4 | 0 | 0 | 2373 | 103 | 34 | 66 | 9218 | 1643494 | 182765 | 1.15 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 2031 | 281 | 48 | 94 | 24911 | 2999354 | 177952 | 2.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| scratch-copy-libs.test.sh no longer walks every suite under tests/ and tests/unit/ line by line in a bash `while read` loop with regex matches once per case (the walks at :56 on the real tree, :81, :105 and :124): the suite tree is read in one pass shared by the cases, or each case selects only its candidate lines with a single external text tool before any per-line bash work, and the suite stays in tests/unit/ using no git, python3, server, sleep or nested suite ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 224 | 31 | 60 | 19620 | 1993537 | 114862 | 1.51 | 645 | n/a | n/a | n/a |  |  | full |
| scratch-copy-libs.test.sh reports the same verdicts as before the branch: every case's name and expected hits are unchanged, the planted offenders (a.test.sh:3, unit/b.test.sh:2 and the #749 plants d–i) are still named, and the real tree's four audits stay clean ⟦diff-checked⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 1 | 152 | 50 | 98 | 13561 | 2637345 | 211013 | 2.01 | 503 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 77 | 79 | 74 | 73 |
| affected | 10 | 76 |  |  |
| all | 1180 | 1177 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 82 | 160 | 34129 | 4642848 | 360717 | 3.67 |
