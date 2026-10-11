### 📊 Metrics — issue 1313

Wall time for the issue: 7152 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 18 of 18 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1499.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 13 | 1 | 2 | 1675 | 12193 | 44303 | 0.20 |
| red | 28 | 12 | 0 | 0 | 754 | 568 | 155 | 308 | 66225 | 7827992 | 1400152 | 7.05 |
| green | 30 | 12 | 3 | 0 | 5538 | 804 | 223 | 428 | 83753 | 11533532 | 1410717 | 8.50 |
| refactor | 26 | 12 | 1 | 0 | 2035 | 344 | 129 | 248 | 35731 | 5988942 | 1226179 | 6.07 |
| pin | 4 | 4 | 0 | 0 | 78 | 54 | 18 | 34 | 6219 | 774590 | 181430 | 0.87 |
| diff | 4 | 2 | 0 | 0 | 1074 | 81 | 26 | 50 | 9469 | 1334864 | 207569 | 1.06 |
| rebase | 8 | 4 | 0 | 0 | 4766 | 135 | 49 | 92 | 14067 | 2261066 | 383319 | 1.90 |
| predicate | 6 | 0 | 0 | 0 | 75 | 51 | 21 | 42 | 4942 | 904583 | 264849 | 1.20 |
| structural | 4 | 0 | 0 | 0 | 762 | 87 | 31 | 62 | 9682 | 1614725 | 192182 | 1.03 |
| transform | 4 | 3 | 1 | 0 | 142 | 50 | 20 | 38 | 5139 | 871033 | 179919 | 0.86 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 55 | 50 | 5 | 0 | 6597 | 850 | 277 | 526 | 93057 | 12523049 | 2459514 | 12.02 |
| developer | claude-sonnet-5-5 | 53 | 0 | 0 | 0 | 7414 | 1067 | 338 | 666 | 123770 | 17558994 | 2680600 | 13.72 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 1231 | 270 | 58 | 112 | 20075 | 3041477 | 350505 | 2.99 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2704 | 3.95 | 0 | 0.00 |
| refactor | 244 | 1.08 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 142 | 0.86 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The one reader, `veri/tunables.py`, serves VERI_CONDUCTOR_STOP_TIMEOUT (default 10, bounded above so `signal.setitimer` cannot overflow): `orchestrate.sh` run with `VERI_CONDUCTOR_STOP_TIMEOUT=1e12` exits 2 with exactly one stderr line naming the variable and the value, no traceback, and `solvable-issues.sh` never started ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 101 | 32 | 62 | 11025 | 1527417 | 288322 | 1.42 | 431 | unknown | 0/5 | nothing-structural |  |  | full |
| `orchestrate.sh` reads VERI_CONDUCTOR_CTX_BUDGET through the one reader too: a value that is not a whole number exits 2 with one stderr line naming the variable and the value, no traceback, and nothing started ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 22 | 4455 | 553056 | 98508 | 0.49 | unknown | unknown | unknown | unknown |  |  | pin |
| `orchestrate.sh`'s header documents VERI_CONDUCTOR_STOP_TIMEOUT with its default and its bounds, beside VERI_CONDUCTOR_CTX_BUDGET's ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 12 | 24 | 3284 | 584693 | 90036 | 0.45 | 165 | n/a | n/a | n/a |  |  | full |
| `supervise.sh` run with a `VERI_KILL_POLL` that is not a number exits 2 with one stderr line naming VERI_KILL_POLL and the value, no traceback, before the leaf command is started, the value parsed by the one reader ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 13 | 26 | 5710 | 708287 | 103455 | 0.54 | unknown | unknown | unknown | unknown |  |  | pin |
| Every tunable in the one reader's table refuses a malformed or out-of-bounds value the same way — exit 2, one stderr line naming the variable and the value, no traceback — pinned by one case parametrized over the reader's whole table, so a tunable added to the table is covered by existing ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 191 | 60 | 110 | 21968 | 2980703 | 362748 | 2.37 | 565 | 1/2 | 0/5 | structural-owed |  |  | full |
| A small test fails, naming `file:line`, on any read of a VERI_* name from `os.environ`, `os.environb` or `os.getenv` in a module under `skills/tdd/scripts/veri/` other than the one reader, with an exemption list naming each module that still reads one directly today ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 14 | 26 | 6157 | 697587 | 100045 | 0.53 | unknown | unknown | unknown | unknown |  |  | pin |
| The guard's exemption list no longer names supervise.py, verify.py, wait_leaf.py, wait_ci.py or detach_command.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 283 | 63 | 122 | 21990 | 3190566 | 419155 | 2.68 | 1694 | 2/2 | 0/5 | structural-owed |  |  | full |
| The guard's exemption list no longer names leaf_timeout.py, leaf_model.py, build_develop_prompt.py, add_ledger_step.py, step_budget.py or time_budget.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 113 | 34 | 64 | 13885 | 1663188 | 303195 | 1.52 | 426 | unknown | 0/5 | structural-owed |  |  | full |
| The guard's exemption list no longer names parallel_conductors.py, orchestrate.py, run_conductor.py, workqueue.py, profile.py or status.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 151 | 45 | 90 | 16136 | 2245074 | 384108 | 2.14 | 881 | 1/2 | 1/5 | structural-owed |  |  | full |
| The guard's exemption list no longer names github.py, solvable_issues.py, skill_drift.py, launch_floor.py, run_suite.py or event.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 121 | 39 | 78 | 14562 | 2041050 | 299462 | 1.55 | 562 | unknown | 1/5 | nothing-structural |  |  | full |
| The guard has no exemption list left: every remaining module (run_leaf.py, run_verdict.py, stop_run.py and any other the list still names) takes its VERI_* values from the one reader, and the guard passes on the tree with no exemption ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 95 | 34 | 66 | 10872 | 1633015 | 283740 | 1.41 | 377 | unknown | 0/5 | nothing-left |  |  | full |
| An autouse fixture in `tests/py/conftest.py` starts every pytest case with no VERI_* variable but VERI_VENV, and no CLAUDE_*, GH_* or GIT_* variable, set — whatever the shell that ran pytest had set; a case that wants one sets it with `monkeypatch` ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 102 | 31 | 58 | 11461 | 1412336 | 294761 | 1.44 | 1581 | unknown | 1/5 | nothing-structural |  |  | full |
| The same fixture starts every pytest case under a fixed locale (LC_ALL=C, every other LC_* and LANG unset), whatever the shell that ran pytest had set ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 75 | 26 | 52 | 8545 | 1221216 | 288494 | 1.36 | 995 | unknown | 0/5 | nothing-left |  |  | full |
| A medium pytest case's `git` still refuses a remote URL after the fixture clears GIT_*: the offline git settings the `make test` recipe passes in GIT_CONFIG_* are restored for it by the fixture, visibly | 6 | 3 | 0 | 0 | 0 | 0 | 111 | 33 | 64 | 12858 | 1634956 | 304005 | 1.51 | 465 | unknown | 1/5 | nothing-left |  |  | full |
| `make hermetic` and `skills/tdd/scripts/tests/hermetic/` are gone, every reference to them in the Makefile, CLAUDE.md and the suites is removed or reworded, and `CLAUDE.md` says the pytest leg's isolation holds by construction through the conftest fixture and the one reader ⟦diff-checked⟧ ⟦criterion 4⟧ | 18 | 5 | 1 | 0 | 0 | 0 | 273 | 97 | 190 | 29460 | 4677351 | 851144 | 4.17 | 941 | unknown | unknown | unknown |  |  | full |
| `VERI_CONDUCTOR_STOP_TIMEOUT` above 100000000 (macOS `setitimer`'s ceiling) exits 2 before any conductor starts, 100000000 itself is accepted, a case at 100000001 pins the refusal, and the `orchestrate.sh` header states that limit ⟦added⟧ ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 93 | 33 | 66 | 10180 | 1632263 | 288906 | 1.42 | 395 | unknown | 0/5 | nothing-left |  |  | full |
| Every `VERI_*` read in `veri/` goes through `tunables.read`, indirect reads through a name variable included — `push_branch.py:44`, `refactor_budget.py:33`, `metrics.py:380`, `event.py:145`, `parallel_conductors.py:35`, `solvable_issues.py:45` — and the guard goes red on a planted `os.environ.get(name)` read ⟦added⟧ ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 140 | 44 | 86 | 14932 | 2291545 | 298056 | 1.57 | 484 | unknown | 1/5 | nothing-structural |  |  | full |
| On the branch rebased onto a `main` that carries #1490 (#1485), the model-knob reads (`leaf_model.py`'s `_env()` and its callers, `verify.py` included) go through `tunables.read`, while #1485's shipped defaults and its empty/whitespace-as-unset handling still hold, pinned by #1485's own cases passing on the rebased tip ⟦added⟧ ⟦criterion 7⟧ | 8 | 4 | 0 | 0 | 0 | 0 | 157 | 51 | 96 | 17747 | 2417024 | 388176 | 1.97 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The one reader, `veri/tunables.py`, serves VERI_CONDUCTOR_STOP_TIMEOUT (default 10, bounded above so `signal.setitimer` cannot overflow): `orchestrate.sh` run with `VERI_CONDUCTOR_STOP_TIMEOUT=1e12` exits 2 with exactly one stderr line naming the variable and the value, no traceback, and `solvable-issues.sh` never started ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 92 | 0.43 |
| Every tunable in the one reader's table refuses a malformed or out-of-bounds value the same way — exit 2, one stderr line naming the variable and the value, no traceback — pinned by one case parametrized over the reader's whole table, so a tunable added to the table is covered by existing ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 132 | 0.47 |
| The guard's exemption list no longer names supervise.py, verify.py, wait_leaf.py, wait_ci.py or detach_command.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 101 | 0.44 |
| The guard's exemption list no longer names leaf_timeout.py, leaf_model.py, build_develop_prompt.py, add_ledger_step.py, step_budget.py or time_budget.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 81 | 0.42 |
| The guard's exemption list no longer names parallel_conductors.py, orchestrate.py, run_conductor.py, workqueue.py, profile.py or status.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 1 | 244 | 1.08 |
| The guard's exemption list no longer names github.py, solvable_issues.py, skill_drift.py, launch_floor.py, run_suite.py or event.py: each takes its VERI_* values from the one reader, with its defaults and its refusals unchanged ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 113 | 0.51 |
| The guard has no exemption list left: every remaining module (run_leaf.py, run_verdict.py, stop_run.py and any other the list still names) takes its VERI_* values from the one reader, and the guard passes on the tree with no exemption ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 92 | 0.41 |
| An autouse fixture in `tests/py/conftest.py` starts every pytest case with no VERI_* variable but VERI_VENV, and no CLAUDE_*, GH_* or GIT_* variable, set — whatever the shell that ran pytest had set; a case that wants one sets it with `monkeypatch` ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 741 | 0.48 |
| The same fixture starts every pytest case under a fixed locale (LC_ALL=C, every other LC_* and LANG unset), whatever the shell that ran pytest had set ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 148 | 0.41 |
| A medium pytest case's `git` still refuses a remote URL after the fixture clears GIT_*: the offline git settings the `make test` recipe passes in GIT_CONFIG_* are restored for it by the fixture, visibly | 1 | 1/5 | nothing-left | PASS | 0 | 106 | 0.50 |
| `VERI_CONDUCTOR_STOP_TIMEOUT` above 100000000 (macOS `setitimer`'s ceiling) exits 2 before any conductor starts, 100000000 itself is accepted, a case at 100000001 pins the refusal, and the `orchestrate.sh` header states that limit ⟦added⟧ ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 80 | 0.42 |
| Every `VERI_*` read in `veri/` goes through `tunables.read`, indirect reads through a name variable included — `push_branch.py:44`, `refactor_budget.py:33`, `metrics.py:380`, `event.py:145`, `parallel_conductors.py:35`, `solvable_issues.py:45` — and the guard goes red on a planted `os.environ.get(name)` read ⟦added⟧ ⟦criterion 6⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 105 | 0.49 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 3/3 | budget-spent |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 1 | 0 | 0 | 3 | 0 | 17 | 1 | 0 | 30 | 29 | 32 | 1 | 3 | 0 | 1 | 1 | 12 | 2 | 2 | 1 | 35 | 203 | 200 | 2 | 1 | 153 | 7 | 11 | 2 | 36 | 12 | 2 | 0 | 0 | 12 | 1 | 3 | 1 | 2 | 0 | 1 | 1 | 1 | 0 | 3 | 1 | 15 | 155 | 0 | 1 | 0 | 1 | 0 | 107 | 1 | 1 | 9 | 0 | 41 | 0 | 1 | 5 | 13 | 1 | 4 | 3 | 1 | 3 | 1 | 1 | 17 | 3 | 3 | 3 | 12 | 2 | 2 | 588 | 2 | 56 | 589 | 3 | 2 | 597 | 62 | 3 | 3 | 44 | 3 | 0 | 605 | 559 | 19 | 58 | 18 | 18 | 0 | 5 | 17 | 1 | 2 | 1 | 0 | 2 | 0 | 1 | 0 | 7 | 1 | 13 | 4 | 24 | 0 | 0 | 1 | 0 | 0 |
| fast | 55 | 54 | 55 | 56 | 54 | 54 | 53 | 56 | 55 | 54 | 55 | 55 | 55 | 55 | 56 | 56 | 55 | 55 | 56 | 55 | 56 | 55 | 55 | 55 | 56 | 54 | 56 | 56 | 54 | 55 | 55 | 55 | 57 | 55 | 55 | 60 | 59 | 62 | 60 | 60 | 56 | 63 | 56 | 57 | 56 | 56 | 57 | 57 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 3 | 2 | 0 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 564 | 562 | 567 | 568 | 555 | 558 | 620 | 555 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 673 | 1304 | 236902 | 33123520 | 5490619 | 28.72 |
