### 📊 Metrics — issue 1675

Wall time for the issue: 855 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1758.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 3 | 6 | 1115 | 79687 | 17127 | 0.06 |
| diff | 6 | 3 | 0 | 0 | 152 | 92 | 29 | 58 | 8116 | 804403 | 88448 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 84 | 49 | 17 | 34 | 4053 | 456346 | 57180 | 0.23 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 83 | 54 | 15 | 30 | 5178 | 427744 | 48395 | 0.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| In test_comment_class.py's tree-audit case, a CLASS_3_LINES roster entry whose file or line text is no longer in the tree is dropped from the comparison, so deleting a bash suite's cases or the whole suite never fails the case; the change is confined to skills/tdd/scripts/tests/py/test_comment_class.py, no production change, and the case keeps its tree_audit mark ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 7 | 14 | 2856 | 185794 | 29593 | 0.12 | 81 | n/a | n/a | n/a |  |  | full |
| In test_comment_class.py's tree-audit case, a class-3 line whose text changes while it stays in its suite still fails the case, and the failure names that line's file and its line number; test-only, confined to test_comment_class.py ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 9 | 18 | 2751 | 250156 | 30534 | 0.13 | 83 | n/a | n/a | n/a |  |  | full |
| In test_comment_class.py's tree-audit case, a new class-3 line added to a suite and not in CLASS_3_LINES still fails the case until it is added to the roster, the failure naming its file and its line number; test-only, confined to test_comment_class.py ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 13 | 26 | 2509 | 368453 | 28321 | 0.13 | 82 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 6 | 6 | 7 | 6 | 6 |
| affected | 1 | 0 | 0 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 32 | 64 | 9231 | 884090 | 105575 | 0.44 |
