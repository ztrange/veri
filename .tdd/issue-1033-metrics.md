### 📊 Metrics — issue 1033

Wall time for the issue: 1748 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1049.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 880 | 11866 | 30003 | 0.13 |
| red | 4 | 1 | 0 | 0 | 141 | 119 | 27 | 54 | 10223 | 1277370 | 177812 | 1.73 |
| green | 2 | 1 | 0 | 0 | 126 | 46 | 13 | 26 | 4423 | 567522 | 81853 | 0.69 |
| refactor | 2 | 1 | 0 | 0 | 48 | 25 | 8 | 16 | 2422 | 304086 | 78127 | 0.56 |
| pin | 2 | 2 | 0 | 0 | 42 | 26 | 8 | 16 | 2845 | 300152 | 75493 | 0.39 |
| diff | 2 | 1 | 0 | 0 | 81 | 40 | 11 | 22 | 3723 | 455102 | 77497 | 0.61 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 218 | 96 | 30 | 60 | 9850 | 1162270 | 257886 | 1.36 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 230 | 167 | 38 | 76 | 14666 | 1753828 | 262899 | 2.75 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A file tracked in HEAD and matched by .gitignore appears in the preserved attempt's tree with its worktree content, the in-process cases that pin the snapshot's git call sequence updated to the new sequence ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 121 | 33 | 66 | 11100 | 1433481 | 248547 | 2.00 | 333 | unknown | 0/5 | nothing-left |  |  | full |
| Beside a tracked file .gitignore matches, an untracked ignored file is absent from the preserved tree, an untracked non-ignored file is present, and a tracked file deleted from the worktree is absent ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 12 | 24 | 4635 | 535580 | 82441 | 0.69 | unknown | unknown | unknown | unknown |  |  | pin |
| Preserving a worktree holding a tracked file .gitignore matches leaves the caller's index, HEAD and branch untouched ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 11 | 22 | 4178 | 480069 | 82297 | 0.67 | unknown | unknown | unknown | unknown |  |  | pin |
| The existing contract cases in tests/preserve-attempt.test.sh are unchanged by the branch, tests/py/test_preserve_attempt.py changes only assertions pinning the snapshot's git call sequence, and both suites are green ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 11 | 22 | 3723 | 455102 | 77497 | 0.61 | 105 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A file tracked in HEAD and matched by .gitignore appears in the preserved attempt's tree with its worktree content, the in-process cases that pin the snapshot's git call sequence updated to the new sequence ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 48 | 0.56 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 3 | 1 | 0 | 2 | 2 | 2 | 2 | 1 | 2 | 0 |
| fast | 15 | 15 | 15 | 15 | 15 |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 3 | 3 | 2 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 68 | 136 | 24516 | 2916098 | 520785 | 4.11 |
