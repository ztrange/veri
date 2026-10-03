### 📊 Metrics — issue 707

Wall time for the issue: 1666 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/745.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 12 | 2 | 4 | 1160 | 60107 | 38287 | 0.34 |
| red | 2 | 1 | 0 | 0 | 54 | 42 | 13 | 26 | 4342 | 588476 | 84045 | 0.88 |
| green | 2 | 1 | 0 | 0 | 143 | 63 | 16 | 32 | 5379 | 732269 | 81449 | 0.91 |
| refactor | 2 | 1 | 0 | 0 | 81 | 37 | 11 | 22 | 3693 | 477343 | 79643 | 0.81 |
| diff | 6 | 3 | 0 | 0 | 211 | 80 | 27 | 54 | 8349 | 1099589 | 231065 | 2.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 7 | 7 | 0 | 0 | 254 | 120 | 34 | 68 | 11938 | 1413624 | 274898 | 2.72 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 252 | 114 | 35 | 70 | 10985 | 1544160 | 239591 | 2.45 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A function `run_file(run, name)` in a module of `skills/tdd/scripts/veri/` returns the path of `<name>` inside the run directory's `.tdd/` directory (`<run>/.tdd/<name>`), for a plain name and for a glob pattern alike ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 142 | 40 | 80 | 13414 | 1798088 | 245137 | 2.59 | 360 | unknown | 0/5 | nothing-structural |  |  | full |
| `veri/status.py` builds its per-run `.tdd/` paths (`events.jsonl`, `conductor.pid`, `issue-<n>.md`) through `run_file`, with no `os.path.join(run, ".tdd"` left in it; the `.tdd/wt/*` registry glob is untouched ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 9 | 18 | 2465 | 363099 | 75955 | 0.73 | 60 | unknown | unknown | unknown |  |  | full |
| `dashboard_endpoints.py` builds its six per-run `.tdd/` paths (`events.jsonl`, `issue-<n>.md`, `issue-<n>-spec.md`, the leaf's supervised log, the leaf's conductor out, the `*` conductor-out glob) through `run_file`, with no `os.path.join(run, ".tdd"` left in it; the `.tdd/wt/*` registry glob is untouched ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 10 | 20 | 3395 | 421008 | 78828 | 0.78 | 129 | unknown | unknown | unknown |  |  | full |
| Both scripts' outputs and exit codes are unchanged: the branch's diff modifies none of `dashboard.test.sh`, `status.test.sh` or `tests/py/test_status.py`, and all three pass ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 16 | 2489 | 315482 | 76282 | 0.72 | 95 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A function `run_file(run, name)` in a module of `skills/tdd/scripts/veri/` returns the path of `<name>` inside the run directory's `.tdd/` directory (`<run>/.tdd/<name>`), for a plain name and for a glob pattern alike ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 81 | 0.81 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 3 | 3 | 3 | 0 | 3 | 3 | 4 | 42 | 18 |
| fast | 29 | 27 | 26 |  |  |  |  |  |  |  |  |
| target | 1 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 69 | 138 | 22923 | 2957784 | 514489 | 5.17 |
