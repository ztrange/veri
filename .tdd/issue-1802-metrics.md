### 📊 Metrics — issue 1802

Wall time for the issue: 1056 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1830.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 2 | 0 | 0 | 23 | 18 | 3 | 6 | 1796 | 64792 | 25767 | 0.09 |
| red | 1 | 0 | 0 | 0 | 42 | 39 | 6 | 12 | 3229 | 184481 | 19296 | 0.10 |
| diff | 4 | 2 | 0 | 0 | 116 | 78 | 14 | 28 | 6749 | 361755 | 50954 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 70 | 48 | 9 | 18 | 4723 | 213741 | 51157 | 0.20 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 111 | 87 | 14 | 28 | 7051 | 397287 | 44860 | 0.22 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 42 | 0.10 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The dead-library guard in test_dead_libraries.py reports, by name, both `lib/a.sh` and `lib/b.sh` when `lib/a.sh` is named only by `lib/b.sh` and nothing outside `lib/` names `lib/b.sh` (a fixture tree under tmp_path, a small case: no process) ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 39 | 6 | 12 | 3229 | 184481 | 19296 | 0.10 | unknown | unknown | unknown | unknown |  |  | full |
| The dead-library guard in test_dead_libraries.py counts a library live only when a chain of names reaching it starts at an entry point outside `lib/`: with `lib/a.sh` named only by `lib/b.sh` and nothing outside `lib/` naming `lib/b.sh`, both are reported dead, by name; with an entry point naming `lib/b.sh`, neither is. The work changes only the test file (no production change); its new cases are small (a fixture tree under tmp_path, no process), and the existing tree_audit case still passes on the real repository ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 8 | 16 | 4161 | 211988 | 26622 | 0.13 | 109 | n/a | n/a | n/a |  |  | full |
| The dead-library guard reads `docs/hooks/reference-transaction` as an entry point: a library named only by that hook is not reported dead. The work changes only the test file (no production change); its new case is small (a fixture tree under tmp_path, no process), and the existing tree_audit case still passes on the real repository ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 6 | 12 | 2588 | 149767 | 24332 | 0.10 | 81 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 0 | 1 | 1 |
| fast | 4 | 5 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 23 | 46 | 11774 | 611028 | 96017 | 0.42 |
