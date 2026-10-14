### 📊 Metrics — issue 1528

Wall time for the issue: 1560 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1529.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 24 | 3 | 6 | 2828 | 77129 | 88079 | 0.39 |
| red | 5 | 1 | 0 | 0 | 163 | 120 | 40 | 78 | 13033 | 2107987 | 252620 | 1.35 |
| pin | 3 | 3 | 0 | 0 | 50 | 33 | 9 | 18 | 3667 | 364811 | 133488 | 0.61 |
| green | 2 | 1 | 0 | 0 | 185 | 40 | 14 | 26 | 4588 | 673288 | 96694 | 0.50 |
| refactor | 2 | 1 | 0 | 0 | 93 | 20 | 7 | 14 | 2080 | 297882 | 89322 | 0.41 |
| predicate | 1 | 0 | 0 | 0 | 12 | 6 | 3 | 6 | 585 | 120421 | 41621 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 277 | 103 | 26 | 52 | 10984 | 1091051 | 357854 | 1.65 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 258 | 140 | 50 | 96 | 15797 | 2550467 | 343970 | 1.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| An event recorded with the default directory from a directory outside any git worktree still lands in ./.tdd/events.jsonl under that directory ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 13 | 26 | 4849 | 691252 | 97881 | 0.51 | unknown | unknown | unknown | unknown |  |  | pin |
| An explicit non-empty directory argument to event.append and event.mark is used as given, even when cwd is a subdirectory of a git worktree ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 20 | 3918 | 486881 | 93217 | 0.46 | unknown | unknown | unknown | unknown |  |  | pin |
| An event recorded through event.sh with the default directory, with cwd set to a subdirectory of a temp git repo, lands in <repo toplevel>/.tdd/events.jsonl and no <subdir>/.tdd is created ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 99 | 35 | 66 | 10387 | 1638781 | 282815 | 1.40 | 406 | unknown | 0/5 | nothing-left |  |  | full |
| timed-test-run.sh's test-run event, run with cwd set to a subdirectory of a temp git repo, lands in <repo toplevel>/.tdd/events.jsonl and no <subdir>/.tdd is created ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 43 | 15 | 30 | 4799 | 747475 | 139832 | 0.68 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| An event recorded through event.sh with the default directory, with cwd set to a subdirectory of a temp git repo, lands in <repo toplevel>/.tdd/events.jsonl and no <subdir>/.tdd is created ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 93 | 0.41 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 2 | 2 | 2 | 1 |
| target | 0 | 1 | 1 | 1 | 2 | 0 | 1 |
| fast | 64 | 61 | 63 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 76 | 148 | 26781 | 3641518 | 701824 | 3.44 |
