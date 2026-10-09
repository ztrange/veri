### 📊 Metrics — issue 986

Wall time for the issue: 1694 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1240.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 1 | 2 | 1270 | 12385 | 31707 | 0.14 |
| red | 2 | 0 | 0 | 0 | 99 | 89 | 16 | 30 | 9049 | 767015 | 101330 | 1.15 |
| pin | 2 | 2 | 0 | 0 | 35 | 24 | 7 | 14 | 3256 | 260327 | 78915 | 0.40 |
| diff | 4 | 2 | 0 | 0 | 252 | 94 | 25 | 46 | 9271 | 1026716 | 166627 | 1.37 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 174 | 66 | 19 | 36 | 7775 | 692446 | 191991 | 0.98 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 227 | 151 | 30 | 56 | 15071 | 1373997 | 186588 | 2.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With its fake answering the two-name `git rev-parse --git-path rebase-merge --git-path rebase-apply` call with both paths one per line, the rebase-already-in-progress case of tests/py/test_rebase_onto_default.py (rebase directory created before main() runs) expects exit 2, empty stdout, git's refusal on stderr, and neither `git diff --name-only --diff-filter=U` nor `git rebase --abort` among the recorded calls ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 11 | 22 | 5467 | 517505 | 89287 | 0.76 | unknown | unknown | unknown | unknown |  |  | pin |
| The own-conflict cases of tests/py/test_rebase_onto_default.py (the no-unmerged-files call of the in-progress test and the conflicting-rebase-under-either-backend test) answer the two-name --git-path call with both paths and create their rebase directory only when the fake's `git rebase -q <onto>` runs, and still expect exit 1 with the conflict output ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 12 | 22 | 6838 | 509837 | 90958 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| Every fake in tests/py/test_rebase_onto_default.py that answers `git rev-parse --git-path` also answers the two-name form `--git-path rebase-merge --git-path rebase-apply` with both paths, one per line ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 15 | 28 | 6741 | 673932 | 93192 | 0.82 | 179 | n/a | n/a | n/a |  |  | full |
| skills/tdd/scripts/veri/rebase_onto_default.py is unchanged on the branch ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 18 | 2530 | 352784 | 73435 | 0.55 | 112 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 0 |  |
| target | 0 | 0 | 1 | 0 | 0 |
| fast | 27 | 28 | 28 | 29 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 49 | 92 | 22846 | 2066443 | 378579 | 3.05 |
