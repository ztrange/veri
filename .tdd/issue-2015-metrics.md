### 📊 Metrics — issue 2015

Wall time for the issue: 1307 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2052.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 21 | 4 | 8 | 1409 | 94373 | 33747 | 0.11 |
| red | 5 | 0 | 0 | 0 | 193 | 164 | 40 | 80 | 18812 | 1255999 | 117773 | 0.61 |
| pin | 5 | 5 | 0 | 0 | 104 | 72 | 18 | 34 | 5791 | 423985 | 65127 | 0.26 |
| diff | 2 | 1 | 0 | 0 | 41 | 27 | 8 | 16 | 1600 | 199915 | 21523 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 149 | 105 | 25 | 48 | 7765 | 589183 | 109338 | 0.41 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 215 | 179 | 45 | 90 | 19847 | 1385089 | 128832 | 0.66 |

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
| Test-only, no production change: a case per module reaches `supervise.py`, `build_develop_prompt.py`, `build_verify_prompt.py` and `run_verdict.py` through a symlinked skill directory and asserts each keeps the unresolved (abspath, symlinked) scripts directory its module-level `HERE`/`SCRIPTS` holds; each case fails when that module's site switches from `abspath` to `realpath` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 12 | 22 | 4173 | 293587 | 49274 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| Test-only, no production change: a case per module reaches `dashboard.py`, `orchestrate.py`, `parallel_conductors.py`, `push_branch.py` and `run_leaf.py` through a symlinked skill directory and asserts each keeps the unresolved (abspath, symlinked) scripts directory its module-level `SCRIPTS`/`GUARD` derives; each case fails when that module's site switches from `abspath` to `realpath` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 11 | 22 | 4268 | 313182 | 30675 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| Test-only, no production change: a case per module reaches `run_conductor.py` and `solvable_issues.py` through a symlinked skill directory and asserts the scripts directory each derives inside its function is the unresolved (abspath, symlinked) one; each case fails when that module's site switches from `abspath` to `realpath` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 11 | 22 | 6367 | 332952 | 35102 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| Test-only, no production change: a case per module reaches `ensure_run_state_ignored.py`, `issue_worktree.py`, `leaf_timeout.py`, `preserve_attempt.py` and `stop_run.py` through a symlinked skill directory and asserts the scripts directory each derives is the resolved (realpath, symlink target) one; each case fails when that module's site switches from `realpath` to `abspath` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 9 | 18 | 3888 | 258922 | 33166 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| Test-only, no production change: a case per module reaches `launch_floor.py` and `suite_reported.py` through a symlinked skill directory and asserts the `os.path.join(…, "..", …)` path each derives stays under the unresolved (abspath, symlinked) skill directory; each case fails when that module's site switches from `abspath` to `realpath` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 15 | 30 | 5907 | 481341 | 34683 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| Test-only: the branch changes no production line, and every existing case keeps its name and outcome ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 1600 | 199915 | 21523 | 0.09 | 69 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 |
| fast | 5 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 70 | 138 | 27612 | 1974272 | 238170 | 1.07 |
